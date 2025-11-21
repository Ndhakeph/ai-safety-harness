# 🛡️ AI Safety Testing Harness

A production-ready platform for red-team testing AI systems with adversarial prompts and monitoring guardrail performance. Built with Python FastAPI, Next.js 14, and Supabase.

![AI Safety Testing Harness](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)
![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🎯 Overview

The AI Safety Testing Harness helps AI engineers stress-test their AI systems by:

- **Running adversarial prompts** against AI models (Google Gemini)
- **Detecting jailbreak attempts** and guardrail failures
- **Tracking safety metrics** over time with comprehensive analytics
- **Alerting** when safety thresholds are breached

## ✨ Features

### 🔒 Multi-Layer Guardrail System
- **Jailbreak Detection**: Pattern matching for instruction override attempts
- **Prompt Injection Detection**: Identifies system prompt extraction attempts
- **Harmful Content Filtering**: Keyword-based detection of dangerous content
- **Role Manipulation Detection**: Catches persona hijacking attempts
- **Encoding Tricks Detection**: Identifies obfuscation techniques (base64, ROT13, etc.)
- **Output Analysis**: Validates model responses for compliance

### 📚 Adversarial Prompt Library
- **Pre-built Test Cases**: 30+ diverse adversarial prompts across 5 categories
- **Custom Prompts**: Create and manage your own test cases
- **Categorization**: Jailbreak, Injection, Harmful, Manipulation, Encoding
- **Severity Levels**: Low, Medium, High risk classification

### 🧪 Testing Capabilities
- **Single Test Runs**: Test individual prompts with detailed results
- **Batch Testing**: Run entire categories of tests simultaneously
- **Multiple Models**: Support for Gemini Pro, Gemini 1.5 Flash, and Gemini 1.5 Pro

### 📊 Safety Metrics & Analytics
- **Safety Score**: 0-100 score based on guardrail performance
- **Jailbreak Success Rate**: Track bypass attempts
- **Guardrail Trigger Rate**: Monitor detection effectiveness
- **Time Series Data**: 7-day safety score trends
- **Category Breakdown**: Performance by adversarial category
- **Incident Tracking**: Automatic logging of security issues

### 💻 Professional Dashboard
- **Real-time Metrics**: Live safety statistics
- **Interactive Charts**: Visualize safety trends with Recharts
- **Detailed Results**: Comprehensive test result analysis
- **Dark Mode Support**: Eye-friendly interface options

## 🏗️ Architecture

```
┌─────────────────┐
│   Next.js 14    │ Frontend Dashboard
│   (TypeScript)  │ - Tailwind CSS
└────────┬────────┘ - Recharts
         │
         │ API Calls
         ▼
┌─────────────────┐
│  FastAPI (Py)   │ Backend API
│                 │ - Async/Await
│  ┌──────────┐   │ - Type Hints
│  │Guardrails│   │ - Pydantic
│  ├──────────┤   │
│  │  Scorer  │   │
│  ├──────────┤   │
│  │  Tester  │   │
│  └──────────┘   │
└────────┬────────┘
         │
         ├─────────► Google Gemini API
         │
         ▼
┌─────────────────┐
│    Supabase     │ Database
│   (PostgreSQL)  │ - Prompts Library
└─────────────────┘ - Test Results
                     - Incidents
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Supabase Account** (free tier works)
- **Google Gemini API Key** (free tier available)

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd ai-safety-harness
```

### 2. Set Up Supabase

1. Create a new project at [supabase.com](https://supabase.com)
2. Navigate to SQL Editor
3. Execute the schema:
   ```bash
   # Copy and execute database/schema.sql
   ```
4. Load seed data:
   ```bash
   # Copy and execute database/seed_data.sql
   ```
5. Get your credentials:
   - Project URL: Settings → API → Project URL
   - Anon Key: Settings → API → anon/public key

### 3. Get Google Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key for configuration

### 4. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp ../.env.example .env

# Edit .env with your credentials:
# GOOGLE_API_KEY=your_gemini_api_key
# SUPABASE_URL=your_supabase_url
# SUPABASE_KEY=your_supabase_anon_key
# FRONTEND_URL=http://localhost:3000

# Run the server
python run.py
```

The backend API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### 5. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
cp .env.local.example .env.local

# Edit .env.local:
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Run the development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 📖 Usage Guide

### Running Your First Test

1. **Start both servers** (backend and frontend)
2. **Navigate to Dashboard** at `http://localhost:3000`
3. **Go to "Run Tests"** page
4. **Enter a custom prompt** or select from library
5. **Click "Run Single Test"**
6. **View results** with safety score and guardrail analysis

### Batch Testing

1. Navigate to **"Run Tests"** page
2. Select a **category** (e.g., "Jailbreak")
3. Click **"Run Batch Test"**
4. Wait for completion (progress shown)
5. Review **aggregate results**

### Managing Prompt Library

1. Go to **"Prompt Library"** page
2. **Filter by category** or severity
3. **Add new prompts** with the "+" button
4. **Edit/Delete** existing prompts
5. **Export** prompts for backup (coming soon)

### Viewing Results

1. Navigate to **"Results"** page
2. **Apply filters**:
   - Jailbreak status
   - Safety score range
   - Date range
3. **Click any result** for detailed analysis
4. **Export to CSV** (coming soon)

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
# Required
GOOGLE_API_KEY=your_gemini_api_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# Optional
FRONTEND_URL=http://localhost:3000
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
```

#### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Guardrail Configuration

Edit `backend/app/services/guardrails.py` to customize:
- Detection patterns (regex)
- Keyword blocklists
- Confidence thresholds
- Rule categories

### Safety Scoring

Edit `backend/app/services/scorer.py` to adjust:
- Scoring weights
- Incident severity thresholds
- Jailbreak detection logic

## 📊 API Documentation

### Key Endpoints

#### Test Execution
- `POST /api/test/run` - Run single test
- `POST /api/test/batch` - Run batch tests

#### Results & Metrics
- `GET /api/results` - Get test results (with filters)
- `GET /api/results/{id}` - Get specific result
- `GET /api/results/metrics/summary` - Get safety metrics
- `GET /api/results/metrics/timeseries` - Get trend data
- `GET /api/results/metrics/categories` - Get category breakdown

#### Library Management
- `GET /api/library` - List prompts
- `POST /api/library` - Create prompt
- `PATCH /api/library/{id}` - Update prompt
- `DELETE /api/library/{id}` - Delete prompt

#### Incidents
- `GET /api/library/incidents/` - List incidents
- `GET /api/library/incidents/{id}` - Get incident details

Full API documentation available at `http://localhost:8000/docs` when running.

## 🗃️ Database Schema

### Tables

**adversarial_prompts**
- `id` (UUID): Primary key
- `category` (TEXT): jailbreak | injection | harmful | manipulation | encoding
- `prompt` (TEXT): The adversarial prompt text
- `expected_blocked` (BOOLEAN): Should guardrails block this?
- `severity` (TEXT): low | medium | high
- `created_at`, `updated_at` (TIMESTAMP)

**test_runs**
- `id` (UUID): Primary key
- `prompt_id` (UUID): Foreign key to adversarial_prompts
- `input_prompt` (TEXT): The tested prompt
- `pre_guardrail_blocked` (BOOLEAN): Pre-check result
- `pre_guardrail_rules` (JSONB): Triggered rules
- `model_response` (TEXT): AI model output
- `post_guardrail_blocked` (BOOLEAN): Post-check result
- `post_guardrail_rules` (JSONB): Triggered rules
- `jailbreak_successful` (BOOLEAN): Did it bypass guardrails?
- `safety_score` (INTEGER): 0-100 score
- `model_used` (TEXT): Model identifier
- `created_at` (TIMESTAMP)

**incidents**
- `id` (UUID): Primary key
- `test_run_id` (UUID): Foreign key to test_runs
- `severity` (TEXT): low | medium | high | critical
- `description` (TEXT): Incident details
- `created_at` (TIMESTAMP)

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🚀 Deployment

### Backend (Railway/Heroku/Fly.io)

1. Set environment variables in your platform
2. Deploy with:
   ```bash
   # Railway
   railway up

   # Heroku
   git push heroku main

   # Fly.io
   fly deploy
   ```

### Frontend (Vercel/Netlify)

1. Connect your repository
2. Set environment variables:
   - `NEXT_PUBLIC_API_URL=your_backend_url`
3. Deploy automatically on push

### Database (Supabase)

Supabase is already cloud-hosted. No additional deployment needed.

## 🛠️ Development

### Project Structure

```
ai-safety-harness/
├── backend/
│   ├── app/
│   │   ├── db/            # Database clients
│   │   ├── models/        # Pydantic schemas
│   │   ├── routers/       # API endpoints
│   │   ├── services/      # Business logic
│   │   └── main.py        # FastAPI app
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── app/
│   │   ├── tests/         # Test runner page
│   │   ├── library/       # Prompt library page
│   │   ├── results/       # Results pages
│   │   ├── page.tsx       # Dashboard
│   │   └── layout.tsx     # Root layout
│   ├── components/        # React components
│   ├── lib/              # Utilities & API client
│   ├── package.json
│   └── tailwind.config.ts
└── database/
    ├── schema.sql        # Database schema
    └── seed_data.sql     # Sample data
```

### Adding New Guardrail Patterns

1. Edit `backend/app/services/guardrails.py`
2. Add patterns to respective lists
3. Update detection logic if needed
4. Test with sample prompts

### Adding New Adversarial Categories

1. Update database enum in `schema.sql`
2. Update Pydantic models in `schemas.py`
3. Add to frontend category lists
4. Create sample prompts

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **Google Gemini** for AI model API
- **Supabase** for database infrastructure
- **FastAPI** for the excellent Python framework
- **Next.js** for the React framework
- **Recharts** for data visualization

## 📧 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing documentation
- Review API docs at `/docs` endpoint

## 🔮 Roadmap

- [ ] Support for additional AI models (OpenAI, Anthropic, Cohere)
- [ ] Advanced guardrail techniques (ML-based detection)
- [ ] Export functionality (CSV, JSON)
- [ ] Scheduled testing
- [ ] Webhook notifications
- [ ] Team collaboration features
- [ ] Custom scoring algorithms
- [ ] Integration with CI/CD pipelines

---

**Built with ❤️ for AI Safety**
