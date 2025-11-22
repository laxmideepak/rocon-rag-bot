# Step-by-Step: Upload to Vercel Blob Storage

## Step 1: Link Your Project

Run this command and follow the prompts:

```bash
cd /Users/deepakchowdary/Downloads/rocon-rag-bot
vercel link
```

**What to expect:**
- It will ask if you want to link to an existing project or create a new one
- If creating new: choose a name (e.g., `rocon-rag-bot`)
- Select your scope (your Vercel account/team)
- It will create a `.vercel` folder with project configuration

## Step 2: Create Blob Store (if needed)

After linking, you may need to create a Blob store:

**Option A: Via Dashboard**
1. Go to https://vercel.com/dashboard
2. Select your project
3. Go to **Storage** tab
4. Click **Create Database/Store**
5. Select **Blob Store**
6. Name it (e.g., `rocon-rag-blob`)

**Option B: Via CLI (if available)**
```bash
vercel blob store create rocon-rag-blob
```

## Step 3: Upload Files

Once linked and blob store exists:

```bash
# Upload FAISS index
vercel blob put vectorstore/faiss_index.bin

# Upload metadata
vercel blob put vectorstore/metadata.pkl
```

**You'll see output like:**
```
✓ Uploaded: https://[hash].public.blob.vercel-storage.com/faiss_index.bin
```

**Copy these URLs!**

## Step 4: Set Environment Variables

In Vercel Dashboard:
1. Go to your project → **Settings** → **Environment Variables**
2. Add:
   - **Name:** `VERCEL_BLOB_FAISS_URL`
   - **Value:** (paste the URL from faiss_index.bin)
   - **Environment:** Production, Preview, Development (check all)
3. Add:
   - **Name:** `VERCEL_BLOB_META_URL`
   - **Value:** (paste the URL from metadata.pkl)
   - **Environment:** Production, Preview, Development (check all)

## Step 5: Deploy

```bash
vercel --prod
```

## Troubleshooting

### "No Vercel Blob token found"
- Make sure you ran `vercel link` first
- Make sure a Blob store exists in your project

### "Project not found"
- Create the project first in Vercel dashboard
- Or use `vercel link` and select "Create new project"

### Alternative: Skip Blob Storage
Since your files are only ~12.6MB (under 250MB limit), you can skip blob storage entirely and just deploy with files included!

