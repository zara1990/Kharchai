# KharchAI — API Contract

## Implemented Endpoints

### GET /health

Returns the health status of the backend.

**Response — HTTP 200**

```json
{
  "status": "ok"
}
```

---

## Future Endpoints (Not Implemented)

### POST /analyze-receipt

> ⚠️ **This endpoint is NOT implemented.** It is documented here for planning purposes only.

Accepts a receipt image and returns structured financial data extracted by AI.

**Request**

```
Content-Type: multipart/form-data

image: <receipt image file>
```

**Response concept — HTTP 200**

```json
{
  "merchant": "...",
  "date": "...",
  "currency": "PKR",
  "total": 0,
  "items": [
    {
      "name": "...",
      "amount": 0,
      "category": "..."
    }
  ]
}
```

This endpoint will require OpenAI multimodal AI integration (not in scope for Milestone 1).
