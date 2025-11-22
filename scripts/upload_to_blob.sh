#!/bin/bash
# Script to upload vectorstore files to Vercel Blob Storage

echo "📦 Uploading vectorstore files to Vercel Blob Storage..."
echo ""

# Check if vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Install it with: npm install -g vercel"
    exit 1
fi

# Upload FAISS index
echo "📤 Uploading faiss_index.bin..."
BLOB_FAISS_URL=$(vercel blob put vectorstore/faiss_index.bin 2>/dev/null | grep -o 'https://[^[:space:]]*' | head -1)

if [ -z "$BLOB_FAISS_URL" ]; then
    echo "⚠️  Upload failed. Run manually:"
    echo "   vercel blob put vectorstore/faiss_index.bin"
    echo "   Copy the URL from the output and set it as VERCEL_BLOB_FAISS_URL environment variable"
else
    echo "✅ Uploaded: $BLOB_FAISS_URL"
    echo ""
    echo "📝 Add this to Vercel environment variables:"
    echo "   VERCEL_BLOB_FAISS_URL=$BLOB_FAISS_URL"
fi

# Upload metadata
echo ""
echo "📤 Uploading metadata.pkl..."
BLOB_META_URL=$(vercel blob put vectorstore/metadata.pkl 2>/dev/null | grep -o 'https://[^[:space:]]*' | head -1)

if [ -z "$BLOB_META_URL" ]; then
    echo "⚠️  Upload failed. Run manually:"
    echo "   vercel blob put vectorstore/metadata.pkl"
    echo "   Copy the URL from the output and set it as VERCEL_BLOB_META_URL environment variable"
else
    echo "✅ Uploaded: $BLOB_META_URL"
    echo ""
    echo "📝 Add this to Vercel environment variables:"
    echo "   VERCEL_BLOB_META_URL=$BLOB_META_URL"
fi

echo ""
echo "✅ Upload complete!"
echo ""
echo "Next steps:"
echo "1. Add VERCEL_BLOB_FAISS_URL and VERCEL_BLOB_META_URL to Vercel environment variables"
echo "2. Deploy your project: vercel --prod"

