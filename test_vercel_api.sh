#!/bin/bash

# Test script for Vercel API
# Usage: ./test_vercel_api.sh [vercel-url]

VERCEL_URL="${1:-https://your-app.vercel.app}"

echo "🧪 Testing Vercel API: $VERCEL_URL"
echo ""

# Test health
echo "1️⃣ Testing /api/health..."
HEALTH_RESPONSE=$(curl -s "$VERCEL_URL/api/health")
echo "$HEALTH_RESPONSE" | jq '.' 2>/dev/null || echo "$HEALTH_RESPONSE"
echo ""

# Test root
echo "2️⃣ Testing / (root)..."
ROOT_RESPONSE=$(curl -s "$VERCEL_URL/")
echo "$ROOT_RESPONSE" | jq '.' 2>/dev/null || echo "$ROOT_RESPONSE"
echo ""

# Test chat (fast, no expansion)
echo "3️⃣ Testing /api/chat (no query expansion)..."
CHAT_RESPONSE=$(curl -s -X POST "$VERCEL_URL/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I create a site?", "use_query_expansion": false}')
echo "$CHAT_RESPONSE" | jq '.answer' 2>/dev/null || echo "Response received (check JSON)"
echo ""

# Test search
echo "4️⃣ Testing /api/search..."
SEARCH_RESPONSE=$(curl -s -X POST "$VERCEL_URL/api/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "create site", "k": 3}')
echo "$SEARCH_RESPONSE" | jq '.results | length' 2>/dev/null || echo "Response received"
echo ""

echo "✅ Tests complete!"
echo ""
echo "To view full responses, use jq or check the variables:"
echo "  HEALTH_RESPONSE, CHAT_RESPONSE, SEARCH_RESPONSE"

