# FinBot - Personal Finance Assistant

Hackathon project built on CEU AI Engineering coursework.

## Capabilities Demonstrated (4/6)
| Capability | Implementation |
|---|---|
| **Tool Calling** | 5 custom tools: compound interest, budget analyzer, savings planner, finance tips lookup, crypto prices |
| **RAG** | ChromaDB with 13 financial knowledge documents (auto-built on first run) |
| **Memory** | SQLiteSession for multi-turn conversation history |
| **Guardrails** | System prompt topic enforcement (finance topics only) |

---

## Local Setup & Run

### 1. Install dependencies
```bash
cd C:\Users\aaliu\hackathon-finbot
uv sync
```

### 2. Start the app
```bash
PYTHONIOENCODING=utf-8 uv run chainlit run main.py --port 10000
```
Then open **http://localhost:10000** in your browser.

The RAG database auto-builds on first run (no manual setup needed).

---

## Cloud Deployment (Render)

### Step 1: Create GitHub Repository
1. Go to https://github.com/new
2. Create a **public** repo named `hackathon-finbot`
3. Clone it and copy project files:
   ```bash
   git clone https://github.com/YOUR_USERNAME/hackathon-finbot.git
   cd hackathon-finbot

   # Copy all files from C:\Users\aaliu\hackathon-finbot
   # (except .env - don't commit secrets!)
   git add .
   git commit -m "Initial commit: FinBot hackathon project"
   git push origin main
   ```

### Step 2: Deploy on Render
1. Go to https://render.com and sign in with GitHub
2. Click **New +** → **Web Service**
3. Select your `hackathon-finbot` repository
4. Configure:
   - **Name**: `finbot` (or any name)
   - **Runtime**: `Python 3.13`
   - **Build Command**: `uv sync`
   - **Start Command**: `chainlit run main.py --port $PORT --host 0.0.0.0`
5. Add **Environment Variables**:
   ```
   AWS_ACCESS_KEY_ID=your_aws_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret
   AWS_DEFAULT_REGION=eu-west-1
   OPENAI_API_KEY=your_openai_key (optional)
   PYTHONIOENCODING=utf-8
   ```
6. Click **Create Web Service** → Deploy!
   - Build takes ~3-5 min
   - App will be available at `https://finbot.onrender.com`

---

## Demo Script (for presentation)

1. **Guardrail** — "Who won the World Cup?"
   → Shows topic enforcement ✓

2. **RAG** — "How should I pay off my debt faster?"
   → Tool calls finance_tips_lookup ✓

3. **Tool: Budget** — "I earn $5000/month: rent $1500, food $400, transport $300, entertainment $300, savings $500, other $200"
   → Shows 50/30/20 breakdown with status ✓

4. **Crypto Data** — "What's the Bitcoin price right now?"
   → Live Binance API data ✓

5. **Memory** — "If I increase savings by $200/month, how long to reach $10,000?"
   → References the $5k income from earlier ✓

---

## Architecture

```
main.py               → Chainlit web UI + streaming + memory
finance_agent.py      → Agent with 5 tools (no external dependencies)
data/finance_tips.txt → 13 financial knowledge documents
rag_setup/            → Build script for ChromaDB
chroma/               → Vector database (auto-created)
.chainlit/config.toml → UI configuration
start_on_render.sh    → Render deployment command
pyproject.toml        → Python dependencies (uv)
```

---

## Files Ready to Deploy

✅ `start_on_render.sh` - Render start command
✅ `pyproject.toml` - All dependencies listed
✅ `.env.template` - Environment variable template
✅ `.chainlit/config.toml` - UI config
✅ No manual RAG build needed (auto-builds)
