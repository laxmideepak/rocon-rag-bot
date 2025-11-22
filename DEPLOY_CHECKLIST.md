# ✅ Vercel Deployment Checklist

## Pre-Deployment

- [x] Created `api/chat.py` with FastAPI endpoints
- [x] Created `vercel.json` configuration
- [x] Created `api/requirements.txt` with dependencies
- [x] Created `.vercelignore` to exclude unnecessary files
- [x] Verified vectorstore size (2.7MB - under limit)
- [x] Verified data/docs.jsonl exists

## Deployment Steps

### 1. Install Vercel CLI
```bash
npm install -g vercel
```

### 2. Login
```bash
vercel login
```

### 3. Link Project
```bash
cd /Users/deepakchowdary/Downloads/rocon-rag-bot
vercel link
```

### 4. Add Environment Variables
```bash
vercel env add OPENAI_API_KEY
# Paste your OpenAI API key when prompted
# (Get it from https://platform.openai.com/api-keys)
```

### 5. Deploy
```bash
vercel --prod
```

## Post-Deployment

- [ ] Test health endpoint: `curl https://your-app.vercel.app/api/health`
- [ ] Test chat endpoint with a simple question
- [ ] Monitor Vercel logs for any errors
- [ ] Update frontend API URL if needed

## File Sizes

- vectorstore/: 2.7MB ✅
- data/docs.jsonl: ~9.9MB ✅
- Total: ~12.6MB (well under 250MB limit) ✅

## Notes

- Vectorstore files are included in deployment (under size limit)
- Raw HTML files are excluded (not needed)
- API uses 60s timeout and 3008MB memory (Pro plan recommended)

