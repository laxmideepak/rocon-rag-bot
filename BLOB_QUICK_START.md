# Quick Start: Vercel Blob Storage

## Prerequisites

1. Vercel CLI installed: `npm install -g vercel`
2. Logged in: `vercel login`
3. Project linked: `vercel link` (in your project directory)

## Upload Files

```bash
# Navigate to project
cd /Users/deepakchowdary/Downloads/rocon-rag-bot

# Upload files (will prompt if store doesn't exist)
vercel blob put vectorstore/faiss_index.bin
vercel blob put vectorstore/metadata.pkl
```

**Copy the URLs** that are output from each command.

## Set Environment Variables

In Vercel Dashboard:
1. Go to your project → **Settings** → **Environment Variables**
2. Add:
   - `VERCEL_BLOB_FAISS_URL` = URL from faiss_index.bin
   - `VERCEL_BLOB_META_URL` = URL from metadata.pkl

Or via CLI:
```bash
vercel env add VERCEL_BLOB_FAISS_URL production
# Paste the URL when prompted

vercel env add VERCEL_BLOB_META_URL production
# Paste the URL when prompted
```

## Alternative: Skip Blob Storage

If your deployment is under 250MB (currently ~12.6MB ✅), you can skip blob storage and include files directly in deployment. No changes needed!

