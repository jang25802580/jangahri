const SESSION_KEY = 'chatSessionId';

export function getSessionId(): string {
  let sessionId = localStorage.getItem(SESSION_KEY);
  if (!sessionId) {
    sessionId = crypto.randomUUID();
    localStorage.setItem(SESSION_KEY, sessionId);
  }
  return sessionId;
}

export function resetSessionId(): string {
  const sessionId = crypto.randomUUID();
  localStorage.setItem(SESSION_KEY, sessionId);
  return sessionId;
}
