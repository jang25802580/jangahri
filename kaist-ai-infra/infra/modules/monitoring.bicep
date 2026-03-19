// Monitoring module: diagnostic settings, alerts, and workbook
@description('Log Analytics workspace name')
param logAnalyticsName string

@description('Application Insights name')
param appInsightsName string

@description('Function App name')
param functionAppName string

@description('Storage Account name')
param storageAccountName string

@description('Cosmos DB account name')
param cosmosAccountName string

@description('Location')
param location string

@description('Resource tags')
param tags object

// Existing resources
resource law 'Microsoft.OperationalInsights/workspaces@2023-09-01' existing = {
  name: logAnalyticsName
}

resource ai 'Microsoft.Insights/components@2020-02-02' existing = {
  name: appInsightsName
}

resource func 'Microsoft.Web/sites@2023-12-01' existing = {
  name: functionAppName
}

resource storage 'Microsoft.Storage/storageAccounts@2023-01-01' existing = {
  name: storageAccountName
}

resource cosmos 'Microsoft.DocumentDB/databaseAccounts@2024-05-15' existing = {
  name: cosmosAccountName
}

// Diagnostic Settings: forward metrics to Log Analytics
resource diagStorage 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: '${storage.name}-diag-to-law'
  scope: storage
  properties: {
    workspaceId: law.id
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
        retentionPolicy: {
          enabled: false
          days: 0
        }
      }
    ]
  }
}

resource diagFunc 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: '${func.name}-diag-to-law'
  scope: func
  properties: {
    workspaceId: law.id
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
        retentionPolicy: {
          enabled: false
          days: 0
        }
      }
    ]
  }
}

resource diagCosmos 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: '${cosmos.name}-diag-to-law'
  scope: cosmos
  properties: {
    workspaceId: law.id
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
        retentionPolicy: {
          enabled: false
          days: 0
        }
      }
    ]
  }
}

// Action Group for Alerts (email placeholder)
resource actionGroup 'Microsoft.Insights/actionGroups@2021-09-01-preview' = {
  name: 'ag-${location}-alerts'
  location: location
  properties: {
    groupShortName: 'kaistalerts'
    enabled: true
    emailReceivers: [
      {
        name: 'owner'
        emailAddress: 'owner@example.com'
        status: 'Enabled'
      }
    ]
  }
}

// Metric Alert: Function App Errors
resource funcErrorsAlert 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: 'ma-func-errors-${location}'
  location: location
  properties: {
    description: 'Alert when Function App reports >=1 errors in 5 minute interval'
    severity: 2
    enabled: true
    scopes: [func.id]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    criteria: {
      allOf: [
        {
          criterionType: 'StaticThresholdCriterion'
          name: 'ErrorsCriterion'
          metricName: 'Errors'
          metricNamespace: 'Microsoft.Web/sites'
          operator: 'GreaterThanOrEqual'
          threshold: 1
          timeAggregation: 'Total'
        }
      ]
    }
    autoMitigate: true
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

// Metric Alert: Cosmos DB Throttled Requests
resource cosmosThrottleAlert 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: 'ma-cosmos-throttle-${location}'
  location: location
  properties: {
    description: 'Alert when Cosmos DB reports throttled requests'
    severity: 2
    enabled: true
    scopes: [cosmos.id]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    criteria: {
      allOf: [
        {
          criterionType: 'StaticThresholdCriterion'
          name: 'ThrottledCriterion'
          metricName: 'ThrottledRequests'
          metricNamespace: 'Microsoft.DocumentDB/databaseAccounts'
          operator: 'GreaterThan'
          threshold: 0
          timeAggregation: 'Total'
        }
      ]
    }
    autoMitigate: true
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

// Simple Workbook placeholder
resource workbook 'Microsoft.Insights/workbooks@2020-10-20' = {
  name: 'wb-pdf-chatbot-${location}'
  location: location
  properties: {
    displayName: 'PDF Chatbot Monitoring'
    serializedData: json('{"version":"Notebook/1.0","items":[],"metadata":{}}')
  }
}

// Outputs
output logAnalyticsWorkspaceId string = law.id
output applicationInsightsInstrumentationKey string = ai.properties.InstrumentationKey
output applicationInsightsConnectionString string = ai.properties.ConnectionString
output actionGroupId string = actionGroup.id
output workbookId string = workbook.id
