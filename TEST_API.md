# Testing Your Deployed Vercel API

## Prerequisites

After deploying to Vercel, you'll receive a URL like:
- `https://rocon-rag-bot.vercel.app`
- Or your custom domain

## Test Commands

### 1. Test Health Endpoint

```bash
# Replace with your actual Vercel URL
curl https://your-app.vercel.app/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "vectors_indexed": 131
}
```

### 2. Test Root Endpoint

```bash
curl https://your-app.vercel.app/
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "ROCON Docs RAG API",
  "version": "1.0.0"
}
```

### 3. Test Chat Endpoint (Fast - No Query Expansion)

```bash
curl -X POST https://your-app.vercel.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I create a site?", "use_query_expansion": false}'
```

**Expected Response:**
```json
{
  "answer": "To create a site using ROCON...",
  "sources": [
    {
      "title": "Create Site",
      "url": "https://docs.roconpaas.io/home/create-site",
      "category": "Getting Started"
    }
  ],
  "metadata": {
    "chunks_retrieved": 6,
    "confidence": "high",
    "top_score": 0.833,
    "query_expanded": false
  }
}
```

### 4. Test Chat Endpoint (With Query Expansion)

```bash
curl -X POST https://your-app.vercel.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I create a site?", "use_query_expansion": true}'
```

### 5. Test Search Endpoint (Direct Vector Search)

```bash
curl -X POST https://your-app.vercel.app/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "create site", "k": 3}'
```

**Expected Response:**
```json
{
  "query": "create site",
  "results": [
    {
      "title": "Create Site",
      "url": "https://docs.roconpaas.io/home/create-site",
      "content": "...",
      "vector_score": 0.833,
      "rerank_score": 0.85
    }
  ]
}
```

## Interactive Testing Script

Save this as `test_vercel_api.sh`:

```bash
#!/bin/bash

# Set your Vercel URL
VERCEL_URL="${1:-https://your-app.vercel.app}"

echo "🧪 Testing Vercel API: $VERCEL_URL"
echo ""

# Test health
echo "1️⃣ Testing /api/health..."
curl -s "$VERCEL_URL/api/health" | jq '.' || curl -s "$VERCEL_URL/api/health"
echo ""

# Test chat
echo "2️⃣ Testing /api/chat..."
curl -s -X POST "$VERCEL_URL/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I create a site?", "use_query_expansion": false}' \
  | jq '.answer' || echo "Response received"
echo ""

echo "✅ Tests complete!"
```

## Python Test Script

```python
import requests
import json

VERCEL_URL = "https://your-app.vercel.app"  # Replace with your URL

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{VERCEL_URL}/api/health")
    print("Health Check:", response.json())
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_chat():
    """Test chat endpoint"""
    response = requests.post(
        f"{VERCEL_URL}/api/chat",
        json={
            "question": "How do I create a site?",
            "use_query_expansion": False
        }
    )
    data = response.json()
    print("Chat Response:")
    print(f"Answer: {data['answer'][:100]}...")
    print(f"Sources: {len(data['sources'])}")
    print(f"Confidence: {data['metadata']['confidence']}")
    assert response.status_code == 200
    assert "answer" in data

if __name__ == "__main__":
    test_health()
    test_chat()
    print("✅ All tests passed!")
```

## Common Issues

### Issue: 500 Internal Server Error
**Solution:** Check Vercel logs and ensure:
- `OPENAI_API_KEY` is set in environment variables
- Vectorstore files are accessible (or blob URLs are set)

### Issue: Timeout
**Solution:** 
- Use `"use_query_expansion": false` for faster responses
- Check Vercel function timeout settings (should be 60s)

### Issue: Module Not Found
**Solution:** Ensure all dependencies are in `api/requirements.txt`

## Monitoring

View logs in Vercel dashboard:
1. Go to your project
2. Click **Deployments**
3. Click on a deployment
4. View **Function Logs**

