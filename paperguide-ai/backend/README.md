# PaperGuide AI Backend - README

## Project Overview

**PaperGuide AI** is a conference-aware research paper submission assistant. It helps researchers select target conferences, upload papers, analyze for compliance issues, and generate Overleaf-ready LaTeX packages.

**Current Phase**: Phase 1 - Foundation & Core Infrastructure (MVP)  
**Status**: Scaffold Complete - Ready for Implementation

---

## Quick Start

### Prerequisites
- Python 3.10+
- pip or poetry

### Installation

1. **Clone/Setup Project**
   ```bash
   cd backend
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup Environment**
   ```bash
   cp .env.example .env
   # Edit .env if needed
   ```

5. **Run Development Server**
   ```bash
   python run.py
   # or
   uvicorn app.main:app --reload
   ```

6. **Access API**
   - API Docs: http://localhost:8000/api/docs
   - Health Check: http://localhost:8000/health

---

## Project Structure

```
backend/
├── app/
│   ├── core/              # Configuration, logging, exceptions
│   ├── models/            # SQLAlchemy ORM models
│   ├── schemas/           # Pydantic validation schemas
│   ├── routes/            # API endpoint handlers
│   ├── services/          # Business logic layer
│   ├── checkers/          # Rule-based compliance checks
│   ├── agents/            # AI-assisted analysis (placeholder)
│   ├── parsers/           # PDF and file parsing
│   ├── generators/        # LaTeX, ZIP, report generation
│   ├── repositories/      # Data access layer (optional)
│   ├── utils/             # Helper functions
│   ├── main.py           # FastAPI app factory
│   └── database.py       # Database configuration
├── tests/                 # Test suites
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── e2e/              # End-to-end tests
├── data/                 # Conference data and guidelines
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── pytest.ini           # Pytest configuration
├── run.py              # Entry point
└── README.md           # This file
```

---

## Architecture

### Layers

1. **Routes** (API Layer)
   - HTTP request handling
   - Input validation
   - Response formatting

2. **Services** (Business Logic)
   - Orchestration of checkers/agents
   - Data processing
   - Workflow management

3. **Checkers** (Rule-Based Compliance)
   - PageLimitChecker
   - AnonymityChecker
   - ReferenceFormatChecker
   - MarginChecker
   - TemplateChecker
   - SectionChecker
   - ClaimsIntegrityChecker (basic rule-based)

4. **Agents** (AI-Assisted Analysis - Phase 2)
   - GuidelineAgent
   - PaperParsingAgent
   - ClaimsIntegrityAgent (full AI version)
   - ResultAuthenticityAgent
   - GenerationAgent

5. **Parsers** (File Processing)
   - PDFParser
   - MetadataExtractor

6. **Generators** (Output Creation)
   - LaTeXGenerator
   - BibTeXGenerator
   - ZIPGenerator
   - ReportGenerator

7. **Utils** (Helper Functions)
   - Date utilities
   - File utilities
   - Validation utilities
   - LLM utilities (Phase 2)

---

## API Endpoints

### Conferences
- `GET /api/v1/conferences` - List conferences with filtering
- `GET /api/v1/conferences/{id}` - Get conference details with guidelines
- `GET /api/v1/conferences/{id}/guidelines` - Get guidelines only

### Papers
- `POST /api/v1/papers` - Upload paper
- `GET /api/v1/papers/{id}` - Get paper details
- `GET /api/v1/papers/{id}/metadata` - Get paper metadata
- `DELETE /api/v1/papers/{id}` - Delete paper

### Compliance
- `POST /api/v1/papers/{id}/analyze` - Run compliance analysis
- `GET /api/v1/papers/{id}/analyze/status` - Get analysis status
- `GET /api/v1/papers/{id}/report` - Get compliance report

### Generation
- `POST /api/v1/papers/{id}/generate` - Generate package
- `GET /api/v1/papers/{id}/generation/status` - Get generation status
- `GET /api/v1/papers/{id}/download` - Download ZIP package

### Projects
- `GET /api/v1/projects` - List user projects
- `GET /api/v1/projects/{id}` - Get project details
- `POST /api/v1/projects/{id}/resubmit` - Resubmit to different conference

---

## Database

**Current Setup**: SQLite (local file - `paperguide.db`)

### Models
- Conference
- ConferenceGuidelines
- Paper
- ComplianceIssue
- ComplianceReport
- Project

### Future: PostgreSQL
Update `DATABASE_URL` in `.env` to use PostgreSQL for production.

---

## Testing

### Run All Tests
```bash
pytest
```

### Run Specific Test Suite
```bash
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```

### Generate Coverage Report
```bash
pytest --cov=app --cov-report=html
```

---

## MVP Scope (Phase 1)

✅ **Completed in Scaffold**
- Project structure
- Core configuration
- Database models (SQLAlchemy)
- Pydantic schemas
- API route structure
- Services layer (empty)
- Checkers (7 rule-based checkers)
- Agent placeholders (5 agents - not implemented yet)
- Parser and generator structure
- Test structure
- Documentation

⏳ **Next Steps (Phase 2-5)**
- Load NeurIPS guidelines data
- Implement conference service
- Implement paper upload and parsing
- Implement compliance analysis orchestration
- Implement package generation
- Frontend implementation
- Testing
- Deployment

---

## TODO Tracking

All TODO items are marked with `# TODO:` comments throughout the code. Key areas:

1. **Core Business Logic**
   - Conference filtering and retrieval
   - Paper parsing and metadata extraction
   - Compliance analysis orchestration
   - Package generation

2. **Data**
   - Load NeurIPS guidelines from official sources
   - Add conference metadata

3. **Integrations (Phase 2)**
   - OpenAI LLM integration
   - Background job processing (Celery)
   - Redis caching
   - Email notifications

4. **Frontend**
   - React components
   - Conference selection UI
   - Paper upload interface
   - Compliance report visualization
   - Package download

---

## Code Style

- Python: PEP 8
- Docstrings: Google style
- Type Hints: Full typing coverage
- Formatting: Black
- Linting: Flake8

### Format Code
```bash
black app/
```

### Lint Code
```bash
flake8 app/
```

### Type Check
```bash
mypy app/
```

---

## Contributing

1. Follow the project structure
2. Add TODO comments for incomplete work
3. Write tests for new features
4. Keep services thin - use checkers/agents/parsers
5. Document complex logic

---

## Risks & Assumptions (MVP)

### Key Assumptions
1. NeurIPS is representative of conference requirements
2. Rule-based checkers sufficient for MVP (agents in Phase 2)
3. SQLite adequate for MVP (PostgreSQL for production)
4. PDF parsing libraries sufficient
5. Single paper per project (no batch processing)

### Known Risks
- PDF parsing accuracy varies by document format
- Rule-based claims checker limited (semantic analysis needed in Phase 2)
- No authentication/multi-user support in MVP
- Large file handling needs optimization
- LLM cost management needed when implemented

---

## Next Phase: Phase 2 - Guidelines & Services

See [PLANNING.md](../PLANNING.md) for full project plan.

### Phase 2 Deliverables
- Load NeurIPS guidelines (verify official sources)
- Implement ConferenceService with database queries
- Implement PaperService for file handling
- Start implementing ComplianceService
- Implement basic PDF parsing
- Add initial data loading

---

## Contact & Support

TODO: Add team information

---

**Last Updated**: June 9, 2026  
**Version**: 0.1.0-alpha
