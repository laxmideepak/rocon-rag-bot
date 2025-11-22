# Get Blob Store Token

Since your project is linked but the blob store needs a token, here's how to get it:

## Option 1: Get Token from Vercel Dashboard

1. Go to your blob store: https://vercel.com/laxmideepaks-projects/rocon-docs-assistant/stores/blob/store_idMoco9Z3gXvvlN6/browser
2. Click on **Settings** or look for **Tokens** section
3. Copy the **Read/Write Token**
4. Use it to upload:

```bash
# Set token as environment variable
export BLOB_READ_WRITE_TOKEN="your-token-here"

# Then upload
vercel blob put vectorstore/faiss_index.bin
vercel blob put vectorstore/metadata.pkl
```

## Option 2: Upload via Dashboard

1. Go to the blob store browser: https://vercel.com/laxmideepaks-projects/rocon-docs-assistant/stores/blob/store_idMoco9Z3gXvvlN6/browser
2. Click **Upload** button
3. Upload `vectorstore/faiss_index.bin` and `vectorstore/metadata.pkl`
4. Copy the URLs that are generated
5. Add them as environment variables in Vercel:
   - `VERCEL_BLOB_FAISS_URL`
   - `VERCEL_BLOB_META_URL`

## Option 3: Skip Blob Storage (Recommended)

Since your files are only ~12.6MB (well under 250MB), you can skip blob storage:

1. Make sure `vectorstore/` is NOT in `.vercelignore`
2. Deploy: `vercel --prod`
3. Files will be included in deployment automatically

This is simpler and works perfectly for your use case!

