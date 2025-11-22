# Set OpenAI API Key in Vercel

The deployment failed because the `OPENAI_API_KEY` environment variable is not set in Vercel.

## Option 1: Set via Vercel Dashboard (Recommended)

1. Go to your Vercel project: https://vercel.com/laxmideepaks-projects/rocon-docs-assistant
2. Navigate to **Settings** → **Environment Variables**
3. Click **Add New**
4. Add:
   - **Name:** `OPENAI_API_KEY`
   - **Value:** (paste your OpenAI API key from `.env` file)
   - **Environment:** Select all (Production, Preview, Development)
5. Click **Save**

## Option 2: Set via CLI

```bash
# Set the environment variable
vercel env add OPENAI_API_KEY production

# When prompted, paste your API key
# Repeat for preview and development if needed:
vercel env add OPENAI_API_KEY preview
vercel env add OPENAI_API_KEY development
```

## Option 3: Create Secret (Alternative)

If you want to use secrets:

```bash
# Create a secret
vercel secrets add openai_api_key

# When prompted, paste your API key
```

Then update `vercel.json` to use:
```json
"env": {
  "OPENAI_API_KEY": "@openai_api_key"
}
```

## After Setting the Variable

Deploy again:
```bash
vercel --prod
```

