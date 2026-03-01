# AI Safety Testing Harness

A red-team testing platform for evaluating LLM safety mechanisms. Run adversarial prompts against AI models and measure which guardrails catch them.

## Why I Built This

As LLMs get deployed in production, safety testing becomes critical—but manual red-teaming doesn't scale. You can't hand-test every jailbreak variation before deployment. I wanted a systematic way to run adversarial prompts and measure exactly which detection layers caught (or missed) each attack, so I could quantify guardrail effectiveness rather than rely on spot-checking.

## How It Works

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          FRONTEND (Next.js)                                 │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐ │
│  │  Test Library   │  │  Run Tests      │  │  Results Dashboard          │ │
│  │  Management     │  │  (Single/Batch) │  │  (Metrics, Charts, Logs)    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘ │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │ REST API
┌───────────────────────────────────▼─────────────────────────────────────────┐
│                          BACKEND (FastAPI)                                  │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                         TEST RUNNER SERVICE                           │ │
│  │                                                                       │ │
│  │   Input ──▶ PRE-GUARDRAIL ──▶ LLM API ──▶ POST-GUARDRAIL ──▶ Score   │ │
│  │              (5 layers)        (Gemini)    (refusal check)            │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    5-LAYER GUARDRAIL PIPELINE                       │   │
│  │                                                                     │   │
│  │   1. Jailbreak Detection     ─── "ignore all previous instructions" │   │
│  │   2. Prompt Injection        ─── "SYSTEM: override directives"      │   │
│  │   3. Harmful Content         ─── keyword matching (weapons, hacking)│   │
│  │   4. Role Manipulation       ─── "you are now EvilGPT"              │   │
│  │   5. Encoding Tricks         ─── base64, ROT13, obfuscation         │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────────┐  │
│  │  Safety Scorer   │  │  Incident        │  │  Refusal Verification   │  │
│  │  (weighted 0-100)│  │  Tracking        │  │  (output validation)    │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────────────┘  │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼─────────────────────────────────────────┐
│                         SUPABASE (PostgreSQL)                               │
│                                                                             │
│   adversarial_prompts     test_runs              incidents                  │
│   (test library)          (execution results)    (security breaches)        │
└─────────────────────────────────────────────────────────────────────────────┘
```

The test flow works in stages:

1. **Pre-guardrail check**: Input passes through 5 regex-based detection layers
2. **Model query**: If not blocked, prompt goes to the LLM (Gemini by default)
3. **Post-guardrail check**: Response is validated for refusal patterns and harmful content
4. **Scoring**: Safety score calculated from weighted components (pre: 30%, post: 40%, jailbreak prevention: 30%)
5. **Incident creation**: If jailbreak succeeds or safety score is low, an incident is logged

## Key Technical Decisions

- **Regex-based detection over embeddings**: Regex gives ~95% detection on known jailbreak patterns with <10ms latency per layer. Semantic similarity would catch novel attacks better, but adds 100ms+ per check. For a testing harness where you're running hundreds of tests, speed matters more than catching zero-days—you can add new patterns as attacks evolve.

- **Pre AND post guardrail checks**: Early versions only validated input. But a model can pass input guardrails and still produce harmful output if it misinterprets the prompt or if the attack is subtle. The post-check looks for refusal indicators ("I cannot help with that") and flags responses that appear to comply with harmful requests.

- **Test suites organized by attack category**: The seed data has 5 categories (jailbreak, injection, harmful, manipulation, encoding) with varying severity levels. This lets you run targeted tests ("how well do we catch encoding tricks?") and measure false positive rates by including benign prompts that shouldn't be blocked.

## Tech Stack

**Backend**
- Python 3.11
- FastAPI
- Pydantic (schema validation)
- Supabase (PostgreSQL + REST API)
- Google Gemini API (swappable in `backend/app/services/tester.py`)

**Frontend**
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- shadcn/ui components
- Recharts (metrics visualization)

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Supabase account (free tier works)
- Google Gemini API key (free tier works)

### Database Setup

1. Create a project at [supabase.com](https://supabase.com)
2. Go to SQL Editor and run `database/schema.sql`
3. Run `database/seed_data.sql` to populate test prompts
4. Copy your project URL and anon key from Settings → API

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Add GOOGLE_API_KEY, SUPABASE_URL, SUPABASE_KEY to .env

python run.py  # Runs on http://localhost:8000
```

### Frontend

```bash
cd frontend
npm install

cp .env.local.example .env.local
# Add NEXT_PUBLIC_API_URL=http://localhost:8000

npm run dev  # Runs on http://localhost:3000
```

Open http://localhost:3000, pick a prompt from the test library, and run it.

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app entry point
│   │   ├── db/
│   │   │   └── supabase.py         # Database client
│   │   ├── models/
│   │   │   └── schemas.py          # Pydantic models
│   │   ├── routers/
│   │   │   ├── tests.py            # /api/test endpoints
│   │   │   ├── results.py          # /api/results endpoints
│   │   │   └── library.py          # /api/library endpoints
│   │   └── services/
│   │       ├── guardrails.py       # 5-layer detection pipeline
│   │       ├── tester.py           # Test runner orchestration
│   │       └── scorer.py           # Safety score calculation
│   ├── requirements.txt
│   └── run.py
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx                # Dashboard home
│   │   ├── tests/page.tsx          # Run tests interface
│   │   ├── library/page.tsx        # Manage test prompts
│   │   └── results/page.tsx        # View test results
│   ├── components/
│   │   ├── SafetyChart.tsx         # Metrics visualization
│   │   ├── TestResultCard.tsx      # Individual result display
│   │   └── MetricsCard.tsx         # Summary statistics
│   └── lib/
│       └── api.ts                  # Backend API client
│
├── database/
│   ├── schema.sql                  # Table definitions
│   └── seed_data.sql               # Initial test prompts
│
└── .env.example                    # Environment template
```

## What I Learned

The hardest part of this project was defining what "safe" actually means. Regex catches known patterns well—if someone says "ignore all previous instructions," that's an obvious jailbreak attempt. But adversarial prompts are creative: base64 encoding, hypothetical framing ("for a movie script..."), or role manipulation ("pretend you're an AI researcher"). Each edge case forced me to decide: is this harmful intent or legitimate use? The "for educational purposes" pattern is a good example—security researchers legitimately need to understand attack techniques, but attackers use the same framing. I ended up including these as test cases with `expected_blocked: false` to measure false positive rates. The scoring system (30% pre-guardrail, 40% post-guardrail, 30% jailbreak prevention) was tuned by running the test suite repeatedly and adjusting until the scores matched my intuition about which failures were worse.

## License

MIT
