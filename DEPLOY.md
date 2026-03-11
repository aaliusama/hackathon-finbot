# Deployment Checklist

## Local Testing ✓
- [x] App runs on `http://localhost:10000`
- [x] All 5 tools working (budget, compound interest, savings, finance tips, crypto)
- [x] RAG database auto-builds
- [x] Memory persists across conversation turns
- [x] Guardrails redirect off-topic questions

---

## Before Deploying to Render

### 1. GitHub Setup
```bash
# Create new repo: https://github.com/new
# Name it: hackathon-finbot

# Clone and push code
git clone https://github.com/YOUR_USERNAME/hackathon-finbot.git
cd hackathon-finbot

# Copy files from C:\Users\aaliu\hackathon-finbot (SKIP .env!)
git add .
git commit -m "Initial commit: FinBot AI finance assistant"
git push origin main
```

### 2. Render Configuration
1. Sign in to https://render.com with GitHub
2. Click **New +** → **Web Service**
3. Select `hackathon-finbot` repo
4. Settings:
   - **Name**: `finbot`
   - **Runtime**: `Python 3.13`
   - **Build Command**: `uv sync`
   - **Start Command**: `chainlit run main.py --port $PORT --host 0.0.0.0`

### 3. Add Environment Variables in Render Dashboard
```
AWS_ACCESS_KEY_ID = [your key]
AWS_SECRET_ACCESS_KEY = [your secret]
AWS_DEFAULT_REGION = eu-west-1
OPENAI_API_KEY = [optional - for tracing]
PYTHONIOENCODING = utf-8
```

### 4. Deploy
- Click **Create Web Service**
- Wait 3-5 minutes for build
- App URL: `https://finbot.onrender.com`

---

## After Deployment

### Test on Render
Visit your Render URL and test:
1. "Who won the World Cup?" (guardrail)
2. "How do I invest?" (RAG)
3. Budget question (tool calling)
4. "Bitcoin price?" (live data)
5. Follow-up question (memory)

### Demo Script (5 min live demo)
```
Q1: "Who won the World Cup?"
A: Guardrail redirects to finance

Q2: "How should I pay off debt faster?"
A: RAG returns debt strategies (watch for tool call step)

Q3: "I earn $5k/month: rent $1500, food $400, transport $300, entertainment $300, savings $500, other $200"
A: Budget analyzer shows 50/30/20 breakdown

Q4: "What's the Bitcoin price?"
A: Live Binance API data

Q5: "If I save $300/month at 4%, how long to reach $10,000?"
A: Uses goal planner + remembers context (memory)
```

---

## Troubleshooting

**Build fails on Render?**
- Check that `pyproject.toml` is in root
- Check that `main.py` exists
- Verify all dependencies are in `pyproject.toml`

**App crashes after deploy?**
- Check environment variables are set (especially AWS keys)
- View logs in Render dashboard (Logs tab)

**ChromaDB "collection not found" error?**
- RAG auto-builds on first startup — just wait 10 sec and refresh

---

## Files in Repo (Don't Commit .env!)
```
✓ finance_agent.py       - Agent with 5 tools
✓ main.py                - Chainlit app
✓ pyproject.toml         - Dependencies (uv)
✓ data/finance_tips.txt  - RAG knowledge base
✓ rag_setup/*.py         - RAG setup script
✓ .chainlit/config.toml  - UI config
✓ start_on_render.sh     - Render start command
✓ .gitignore             - Don't commit secrets/cache
✗ .env                   - NEVER COMMIT (add to .gitignore)
✗ chroma/                - Auto-generated on first run
✗ conversation_history/  - Auto-generated per session
```
