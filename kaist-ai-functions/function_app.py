import logging
import azure.functions as func
from shared.config import get_config

logger = logging.getLogger(__name__)

# FunctionApp 정의 (인증 레벨 설정)
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# ---------------------------------------------------------------------------
# 1. Test Gemini (교수님 강의 예제 - 브라우저 확인용)
# ---------------------------------------------------------------------------
@app.route(route="test_gemini", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def test_gemini(req: func.HttpRequest) -> func.HttpResponse:
    """Test Gemini API connectivity."""
    import json
    from services.embedding_service import EmbeddingService

    try:
        # EmbeddingService의 ping 기능을 이용해 연결 확인
        EmbeddingService().ping()
        return func.HttpResponse(
            body=json.dumps({
                "status": "ok", 
                "message": "Hello! Gemini API is reachable.",
                "type": "text"
            }),
            status_code=200,
            mimetype="application/json",
        )
    except Exception as exc:
        logger.warning("Gemini connectivity test failed: %s", exc)
        return func.HttpResponse(
            body=json.dumps({
                "status": "unavailable", 
                "message": str(exc)
            }),
            status_code=503,
            mimetype="application/json",
        )

# ---------------------------------------------------------------------------
# 2. Health Check
# ---------------------------------------------------------------------------
@app.route(route="health", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def health(req: func.HttpRequest) -> func.HttpResponse:
    """Liveness probe — returns service connectivity status."""
    import json
    checks: dict[str, str] = {}

    # Azure Blob Storage
    try:
        from services.storage_service import BlobStorageService
        BlobStorageService().ping()
        checks["storage"] = "ok"
    except Exception as exc:
        logger.warning("Storage health check failed: %s", exc)
        checks["storage"] = "unavailable"

    # Azure Cosmos DB
    try:
        from services.cosmos_service import CosmosRepository
        CosmosRepository().ping()
        checks["cosmos"] = "ok"
    except Exception as exc:
        logger.warning("Cosmos health check failed: %s", exc)
        checks["cosmos"] = "unavailable"

    # Gemini API
    try:
        from services.embedding_service import EmbeddingService
        EmbeddingService().ping()
        checks["gemini"] = "ok"
    except Exception as exc:
        logger.warning("Gemini health check failed: %s", exc)
        checks["gemini"] = "unavailable"

    overall = "healthy" if all(v == "ok" for v in checks.values()) else "degraded"
    status_code = 200 if overall == "healthy" else 503

    return func.HttpResponse(
        body=json.dumps({"status": overall, "checks": checks}),
        status_code=status_code,
        mimetype="application/json",
    )

# ---------------------------------------------------------------------------
# 3. PDF Upload
# ---------------------------------------------------------------------------
@app.route(route="pdf/upload", methods=["POST"])
def pdf_upload(req: func.HttpRequest) -> func.HttpResponse:
    import json
    import uuid
    from datetime import datetime, timezone
    from shared.exceptions import InvalidFileTypeError
    from services.storage_service import BlobStorageService
    from services.cosmos_service import CosmosRepository
    from shared.models import DocumentRecord, UploadResponse

    try:
        file = req.files.get("file")
        if file is None:
            return func.HttpResponse(
                json.dumps({"error": "No file provided."}),
                status_code=400,
                mimetype="application/json",
            )

        content_type = file.content_type or ""
        if "pdf" not in content_type.lower():
            raise InvalidFileTypeError(f"Expected PDF, got '{content_type}'")

        file_bytes = file.read()
        document_id = str(uuid.uuid4())
        blob_name = f"{document_id}.pdf"
        
        storage = BlobStorageService()
        blob_url = storage.upload_pdf(file_bytes, blob_name)

        record = DocumentRecord(
            id=document_id,
            file_name=file.filename or blob_name,
            blob_url=blob_url,
            status="pending",
            uploaded_at=datetime.now(timezone.utc).isoformat(),
            size=len(file_bytes),
        )
        CosmosRepository().upsert_document(record.model_dump())

        return func.HttpResponse(
            body=UploadResponse(
                document_id=document_id,
                file_name=file.filename or blob_name,
                status="pending",
                uploaded_at=record.uploaded_at
            ).model_dump_json(),
            status_code=202,
            mimetype="application/json",
        )
    except Exception as exc:
        logger.exception("Upload failed")
        return func.HttpResponse(json.dumps({"error": str(exc)}), status_code=500)

# ---------------------------------------------------------------------------
# 4. PDF Status & Process
# ---------------------------------------------------------------------------
@app.route(route="pdf/status/{documentId}", methods=["GET"])
def pdf_status(req: func.HttpRequest) -> func.HttpResponse:
    import json
    from services.cosmos_service import CosmosRepository
    from shared.models import StatusResponse
    document_id = req.route_params.get("documentId", "")
    try:
        doc = CosmosRepository().get_document(document_id)
        return func.HttpResponse(StatusResponse(
            document_id=document_id,
            status=doc.get("status", "unknown"),
            progress=doc.get("progress", 0),
            chunk_count=doc.get("chunk_count", 0)
        ).model_dump_json(), status_code=200, mimetype="application/json")
    except Exception:
        return func.HttpResponse(json.dumps({"error": "Not found"}), status_code=404)

@app.route(route="pdf/process", methods=["POST"])
def pdf_process(req: func.HttpRequest) -> func.HttpResponse:
    import json
    from services.cosmos_service import CosmosRepository
    from services.storage_service import BlobStorageService
    from services.pdf_service import PDFService
    from services.embedding_service import EmbeddingService
    from shared.models import ChunkRecord
    import uuid
    from datetime import datetime, timezone

    try:
        body = req.get_json()
        document_id = body.get("documentId")
        repo = CosmosRepository()
        storage = BlobStorageService()
        pdf_service = PDFService()
        embedding_service = EmbeddingService()

        repo.update_document_status(document_id, "processing", progress=0)
        pdf_bytes = storage.download_pdf(f"{document_id}.pdf")
        pages = pdf_service.extract_text(pdf_bytes)
        chunks = pdf_service.chunk_text(pages)
        embeddings = embedding_service.embed_texts(chunks)

        for idx, (text, emb) in enumerate(zip(chunks, embeddings)):
            chunk = ChunkRecord(id=str(uuid.uuid4()), document_id=document_id, chunk_index=idx, text=text, embedding=emb, created_at=datetime.now(timezone.utc).isoformat())
            repo.upsert_chunk(chunk.model_dump())

        repo.update_document_status(document_id, "completed", progress=100, chunk_count=len(chunks))
        return func.HttpResponse(json.dumps({"documentId": document_id, "chunkCount": len(chunks)}), status_code=200)
    except Exception:
        return func.HttpResponse(status_code=500)

# ---------------------------------------------------------------------------
# 5. Chat Query & History
# ---------------------------------------------------------------------------
@app.route(route="chat/query", methods=["POST"])
def chat_query(req: func.HttpRequest) -> func.HttpResponse:
    import json
    import uuid
    from datetime import datetime, timezone
    from shared.models import ChatQueryRequest, ChatQueryResponse, SourceReference
    from services.cosmos_service import CosmosRepository
    from services.embedding_service import EmbeddingService
    from services.llm_service import LLMService

    try:
        body = req.get_json()
        query_req = ChatQueryRequest.model_validate(body)
        query_embedding = EmbeddingService().embed_texts([query_req.query])[0]
        top_chunks = CosmosRepository().vector_search_chunks(query_embedding=query_embedding, document_ids=query_req.document_ids, top_k=5)
        answer = LLMService().generate_rag_answer(query=query_req.query, context_chunks=[c["text"] for c in top_chunks])
        
        sources = [SourceReference(document_id=c["document_id"], file_name=c.get("file_name", ""), chunk_id=c["id"], relevance_score=c.get("score", 0.0), excerpt=c["text"][:300]) for c in top_chunks]
        return func.HttpResponse(ChatQueryResponse(answer=answer, sources=sources, message_id=str(uuid.uuid4()), timestamp=datetime.now(timezone.utc).isoformat()).model_dump_json(), status_code=200, mimetype="application/json")
    except Exception:
        return func.HttpResponse(status_code=500)

@app.route(route="chat/history", methods=["GET"])
def chat_history(req: func.HttpRequest) -> func.HttpResponse:
    import json
    from services.cosmos_service import CosmosRepository
    session_id = req.params.get("sessionId")
    try:
        messages = (CosmosRepository().get_session(session_id) or {}).get("messages", [])
        return func.HttpResponse(json.dumps({"messages": messages, "total": len(messages)}), status_code=200, mimetype="application/json")
    except Exception:
        return func.HttpResponse(status_code=500)


# ---------------------------------------------------------------------------
# 8. http_get (기본 스텁)
# ---------------------------------------------------------------------------
@app.route(route="http_get", methods=["GET"])
def http_get(req: func.HttpRequest) -> func.HttpResponse:
    name = req.params.get("name")
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get("name")
    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    return func.HttpResponse(
        "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
        status_code=200,
    )


# ---------------------------------------------------------------------------
# 9. http_post (기본 스텁)
# ---------------------------------------------------------------------------
@app.route(route="http_post", methods=["POST"])
def http_post(req: func.HttpRequest) -> func.HttpResponse:
    name = req.params.get("name")
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get("name")
    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    return func.HttpResponse(
        "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
        status_code=200,
    )
