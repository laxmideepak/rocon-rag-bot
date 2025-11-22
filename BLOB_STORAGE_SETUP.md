# Vercel Blob Storage Setup Guide

## Why Use Blob Storage?

Vercel has a **250MB deployment limit**. Your vectorstore files (2.7MB) and data files (9.9MB) are currently under the limit, but using blob storage:
- Reduces deployment size
- Allows for easier updates without redeploying
- Better for production scalability

## Option 1: Use Blob Storage (Recommended for Production)

### Step 1: Install Vercel CLI (if not already installed)

```bash
npm install -g vercel
```

### Step 2: Login and Link Project

```bash
# Login to Vercel
vercel login

# Link your project (if not already linked)
cd /path/to/rocon-rag-bot
vercel link
```

### Step 3: Create Blob Store (if needed)

If you haven't created a Blob store yet:
1. Go to your Vercel project dashboard
2. Navigate to **Storage** → **Create Database/Store**
3. Select **Blob Store**
4. Create the store

Alternatively, the first time you use `vercel blob put`, it may prompt you to create a store.

### Step 4: Upload Vectorstore Files

**Option A: If project is linked to Vercel:**
```bash
# Upload FAISS index
vercel blob put vectorstore/faiss_index.bin

# Upload metadata
vercel blob put vectorstore/metadata.pkl
```

**Option B: If you have a Blob token:**
```bash
# Get your token from Vercel Dashboard → Storage → Your Blob Store → Settings
export BLOB_READ_WRITE_TOKEN="your-token-here"

# Then upload
vercel blob put vectorstore/faiss_index.bin
vercel blob put vectorstore/metadata.pkl
```

**Note:** The command will output a URL. Copy each URL for the next step.

**Note the URLs** returned from each upload command.

### Step 5: Add Environment Variables in Vercel

In your Vercel project dashboard:
1. Go to **Settings** → **Environment Variables**
2. Add:
   - `VERCEL_BLOB_FAISS_URL` = URL from faiss_index.bin upload
   - `VERCEL_BLOB_META_URL` = URL from metadata.pkl upload

Or via CLI:
```bash
vercel env add VERCEL_BLOB_FAISS_URL
vercel env add VERCEL_BLOB_META_URL
```

### Step 6: Update .vercelignore

Add to `.vercelignore`:
```
vectorstore/
```

This excludes vectorstore from deployment since it will be downloaded from blob.

## Option 2: Include in Deployment (Current Setup)

If your total deployment size is under 250MB, you can include the vectorstore directly:

- Current size: ~12.6MB total ✅
- Vectorstore: 2.7MB ✅
- Data: 9.9MB ✅

**No changes needed** - your current setup will work!

## How It Works

The updated `vectorstore.py` will:
1. Check for `VERCEL_BLOB_FAISS_URL` and `VERCEL_BLOB_META_URL` environment variables
2. If set and files don't exist locally, download from blob storage
3. Otherwise, use local files (for development)

## Testing

After setting up blob storage, test locally:
```bash
export VERCEL_BLOB_FAISS_URL="your-blob-url-here"
export VERCEL_BLOB_META_URL="your-blob-url-here"
python -c "from app.vectorstore import load_index; load_index()"
```

