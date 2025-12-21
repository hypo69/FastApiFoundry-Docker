# 📊 Monitoring & Logs API

## GET `/api/v1/logs/health`

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "period": "1h",
    "metrics": {
      "errors_count": 0,
      "warnings_count": 2,
      "api_requests": 45,
      "avg_response_time": 1.23,
      "active_models": 1
    }
  }
}
```

## GET `/api/v1/logs/errors?hours=24`

**Response:**
```json
{
  "success": true,
  "data": {
    "period": "24h",
    "total_errors": 5,
    "error_types": {
      "connection_error": 3,
      "model_error": 2
    },
    "recent_errors": [
      {
        "timestamp": "2025-01-09T09:30:00Z",
        "message": "Model timeout",
        "module": "foundry-client"
      }
    ]
  }
}
```

## GET `/api/v1/logs/performance?hours=24`

**Response:**
```json
{
  "success": true,
  "data": {
    "api_performance": {
      "total_requests": 150,
      "avg_response_time": 1.23,
      "requests_per_hour": 6.25
    },
    "model_performance": {
      "models": {
        "deepseek-chat": {
          "operations": 45,
          "successful": 43,
          "failed": 2,
          "avg_duration": 2.1
        }
      }
    }
  }
}
```

## GET `/api/v1/logs/recent?level=error&limit=50`

**Response:**
```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "timestamp": "2025-01-09T10:30:00Z",
        "level": "error",
        "logger": "foundry-client",
        "message": "Connection timeout"
      }
    ],
    "total_returned": 10,
    "level_filter": "error"
  }
}
```