# 🚀 Vercel Deployment Guide

This guide will help you deploy your ROCON RAG chatbot to Vercel.

## Prerequisites

- Vercel account (free tier works)
- OpenAI API key
- Node.js installed (for Vercel CLI)

## Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

## Step 2: Login to Vercel

```bash
vercel login
```

## Step 3: Link Your Project

```bash
cd /Users/deepakchowdary/Downloads/rocon-rag-bot
vercel link
```

## Step 4: Add Environment Variables

```bash
vercel env add OPENAI_API_KEY
# Paste your OpenAI API key when prompted
```

## Step 5: Handle Large Files (Vectorstore)

Vercel has a 250MB deployment limit. Your vectorstore files might exceed this.

### Option A: Upload to Vercel Blob (Recommended)

```bash
# Install Vercel Blob CLI
npm install -g @vercel/blob

# Upload vectorstore files
vercel blob upload vectorstore/faiss_index.bin
vercel blob upload vectorstore/metadata.pkl

# Note the URLs and add them as environment variables:
vercel env add VERCEL_BLOB_FAISS_URL
vercel env add VERCEL_BLOB_META_URL
```

### Option B: Include in Deployment (if under 250MB)

If your total deployment size is under 250MB, you can include the vectorstore directly.

## Step 6: Deploy

```bash
vercel --prod
```

## Step 7: Test Your Deployment

Once deployed, you'll get a URL like `https://your-app.vercel.app`

Test the health endpoint:
```bash
curl https://your-app.vercel.app/api/health
```

Test the chat endpoint:
```bash
curl -X POST https://your-app.vercel.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I create a site?", "use_query_expansion": false}'
```

## Troubleshooting

### Issue: Deployment fails due to size
**Solution**: Use Vercel Blob or S3 for vectorstore files

### Issue: Timeout errors
**Solution**: 
- Disable query expansion for faster responses: `"use_query_expansion": false`
- Reduce `k` parameter in search
- Consider upgrading to Vercel Pro (60s timeout vs 10s)

### Issue: Module not found errors
**Solution**: Ensure all dependencies are in `api/requirements.txt`

## API Endpoints

- `GET /` - Root endpoint
- `GET /api/health` - Health check
- `POST /api/chat` - Chat with RAG bot
- `POST /api/search` - Direct vector search

## Frontend Integration

See the Next.js frontend example in the deployment guide or create your own frontend that calls these endpoints.

