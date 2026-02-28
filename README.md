# AI Safety Testing Harness

A red-team testing platform for evaluating LLM safety mechanisms. Run adversarial prompts against AI models and see which guardrails catch them.

## Why I Built This

I got interested in AI safety after reading about jailbreak techniques that could bypass ChatGPT's safeguards. The problem is that manual red-teaming doesn't scale—you can't hand-test every edge case before deployment. I wanted to build something that could systematically run adversarial prompts and tell you exactly which detection layers caught (or missed) each attack.

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                    │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────┐ │
│  │ Test Library │  │ Run Tests     │  │ View Results │ │
│  │ Management   │  │ Interface     │  │ Dashboard    │ │
│  └──────────────┘  └───────────────┘  └──────────────┘ │
└───────────────────────┬─────────────────────────────────┘
                        │ REST API
┌───────────────────────▼─────────────────────────────────┐
│                   Backend (FastAPI)                      │
│  ┌──────────────────────────────────────────────────┐  │
│  │            Test Runner Service                    │  │
│  │  • Execute test → Call AI API → Capture response │  │
│  └────────┬─────────────────────────────────────────┘  │
│           │                                              │
│  ┌────────▼──────────┐  ┌────────────────┐  ┌────────┐│
│  │ Guardrail Service │  │ Safety Scorer  │  │ Logger ││
│  │  5 Detection Layers│  │ Risk Analysis  │  │        ││
│  └────────┬──────────┘  └────────────────┘  └────────┘│
│           │                                              │
└───────────┼──────────────────────────────────────────────┘
            │
┌───────────▼──────────────────────────────────────────┐
│           Supabase (PostgreSQL + REST API)           │
│  • adversarial_prompts (test library)                │
│  • test_runs (execution results)                     │
│  • incidents (security breach tracking)              │
└──────────────────────────────────────────────────────┘
```

The core idea is a **multi-layer detection pipeline**. Each prompt passes through 5 guardrail layers before hitting the AI model:

1. **Jailbreak detection** — catches "ignore all previous instructions" patterns
2. **Prompt injection** — flags system command syntax like `SYSTEM:` or `[ADMIN]`
3. **Harmful content** — keyword matching for weapons, hacking, fraud, etc.
4. **Role manipulation** — detects "you are now EvilGPT" style attacks
5. **Encoding tricks** — base64, ROT13, and other obfuscation

After the model responds, a **refusal verification** layer checks whether it actually declined harmful requests (since detecting bad input isn't enough—you need to verify safe output).

## Tech Stack

**Backend:** Python 3.11, FastAPI, Supabase, Pydantic

**Frontend:** Next.js 14, TypeScript, Tailwind CSS, shadcn/ui, Recharts

**Target Model:** Google Gemini API (swappable—see `backend/app/services/tester.py`)

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Supabase account (free tier works)
- Google Gemini API key (free tier works)

### Setup

```bash
git clone https://github.com/tacitusblindsbig/ai-safety-harness
cd ai-safety-harness
```

**Database (Supabase):**
1. Create a project at [supabase.com](https://supabase.com)
2. Go to SQL Editor and run `database/schema.sql`
3. Run `database/seed_data.sql` to populate test prompts
4. Copy your project URL and anon key from Settings → API

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add GOOGLE_API_KEY, SUPABASE_URL, and SUPABASE_KEY to .env
python run.py  # runs on localhost:8000
```

**Frontend (new terminal):**
```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev  # runs on localhost:3000
```

Open http://localhost:3000, pick a prompt from the test library, and run it.

## What I Learned

The biggest insight was that **regex-based detection has real limits**. It works well for known patterns (95% detection on jailbreaks) but struggles with novel attacks and encoding tricks (85%). If I were extending this, I'd add a semantic layer using embeddings to catch attacks that don't match existing patterns—but regex is a reasonable starting point and it's fast (<10ms per layer).

I also learned that guardrail systems need to check both input AND output. Early versions only flagged suspicious prompts but didn't verify the model's response. A model could pass guardrails and still produce harmful content if it misunderstood the prompt.

## License

MIT

## Author

**Nishad Dhakephalkar** — [github.com/tacitusblindsbig](https://github.com/tacitusblindsbig)
