# Deployment Status

## Current Configuration

✅ **Project Linked:** `rocon-docs-assistant`  
✅ **vercel.json:** Configured with `builds` for Python runtime  
✅ **Files:** Vectorstore (~2.7MB) will be included in deployment  

## Function Settings

Since we're using `builds` configuration, function settings need to be set in Vercel Dashboard:

1. Go to: https://vercel.com/laxmideepaks-projects/rocon-docs-assistant/settings/functions
2. Configure:
   - **Max Duration:** 60 seconds
   - **Memory:** 2048 MB (max for Hobby plan)

Or set via CLI:
```bash
vercel env add VERCEL_FUNCTION_MEMORY production
# Enter: 2048

vercel env add VERCEL_FUNCTION_MAX_DURATION production  
# Enter: 60
```

## Environment Variables Required

Make sure these are set in Vercel:
- ✅ `OPENAI_API_KEY` - Set this in Vercel Dashboard → Settings → Environment Variables

## Test Your Deployment

Once deployed, test with:
```bash
# Get your production URL (from vercel ls or dashboard)
curl https://rocon-docs-assistant.vercel.app/api/health
```

Or use the test script:
```bash
python test_vercel_api.py https://rocon-docs-assistant.vercel.app
```

## Deployment URL

Check your latest deployment:
```bash
vercel ls --prod
```

Or visit: https://vercel.com/laxmideepaks-projects/rocon-docs-assistant

