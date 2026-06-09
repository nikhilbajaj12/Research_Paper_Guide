# PaperGuide AI

Conference-Aware Research Paper Submission Assistant

## MVP Overview

PaperGuide AI helps researchers prepare papers for conference submission by analyzing compliance with submission guidelines and generating Overleaf-ready LaTeX packages.

**Supported Conference**: NeurIPS 2025 (MVP)

## Architecture

```
Frontend (Next.js + React + TypeScript)  ←→  Backend (FastAPI + SQLAlchemy + SQLite)
```

## Project Structure

```
├── frontend/              # Next.js frontend app
│   ├── src/
│   │   ├── app/           # Pages (dashboard, upload, report, packages)
│   │   ├── components/    # Reusable UI components
│   │   ├── services/      # API client layer
│   │   ├── types/         # TypeScript interfaces
│   │   ├── constants/     # Routes, labels
│   │   ├── utils/         # Formatters, validators
│   │   └── styles/        # Global CSS
│   ├── Containerfile      # Podman container definition
│   └── package.json
│
├── paperguide-ai/         # Backend
│   └── backend/
│       ├── app/
│       │   ├── routes/        # API endpoints
│       │   ├── services/      # Business logic
│       │   ├── checkers/      # Rule-based compliance checkers
│       │   ├── parsers/       # PDF/DOCX/LaTeX parsers
│       │   ├── generators/    # LaTeX & report generators
│       │   ├── schemas/       # Pydantic models
│       │   ├── core/          # Config, logging, exceptions
│       │   └── models/        # SQLAlchemy models
│       ├── Containerfile      # Podman container definition
│       └── run.py
│
├── podman-compose.yml     # Multi-container orchestration
└── README.md
```

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v1/conferences` | List conferences |
| GET | `/api/v1/conferences/{id}` | Conference details + guidelines |
| POST | `/api/v1/papers/upload` | Upload paper (PDF/DOCX/ZIP) |
| POST | `/api/v1/compliance/analyze` | Run compliance checks |
| POST | `/api/v1/packages/generate` | Generate Overleaf ZIP |
| GET | `/api/v1/packages/{id}/download` | Download generated package |
| GET | `/health` | Health check |

## Running Locally (without containers)

### Backend

```bash
cd paperguide-ai/backend
python -m venv venv
venv\Scripts\activate    # Windows
pip install -r requirements.txt
cp .env.example .env
python run.py
```

Backend runs at: http://localhost:8000

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Frontend runs at: http://localhost:3000

## Running with Podman

```bash
# Copy env files
cp paperguide-ai/backend/.env.example paperguide-ai/backend/.env
cp frontend/.env.example frontend/.env

# Build and run
podman-compose up --build

# Or with podman compose plugin
podman compose up --build
```

## End-to-End Demo Flow

1. Open http://localhost:3000
2. Select **NeurIPS 2025** conference
3. Upload a PDF/DOCX/LaTeX ZIP paper file
4. Click **Upload & Analyze**
5. Review compliance score, issues, and passed checks
6. Click **Generate Overleaf Package**
7. Download the ZIP package
8. Upload ZIP to Overleaf
9. Ensure `neurips_2026.sty` exists in project
10. Set `main.tex` as main file
11. Recompile and review
12. Address compliance issues and submit

## Compliance Checks (Rule-Based)

- **Anonymity** - Detect emails, author names, acknowledgments
- **Page Limit** - Check page count against conference limit
- **References** - Ensure References/Bibliography section exists
- **Citations** - Detect inline citation patterns
- **Template** - Verify conference style file for LaTeX uploads
- **Checklist** - Check for required submission checklist
- **Claims Integrity** - Flag numeric claims for verification

## Known Limitations

- No AI/LLM integration (placeholders ready)
- In-memory paper storage (no database persistence)
- NeurIPS-only for MVP
- No authentication/authorization
- No Overleaf API integration
- References.bib contains templates only (no auto-extraction)

## Future Phases

- AI-assisted fix generation
- Multi-conference support (CVPR, ICML, ACL, etc.)
- User accounts and project history
- Database persistence
- PDF report generation
- OpenReview integration
- Overleaf direct upload
