# AI-Powered Resume Customization Web Application

## Overview
End-to-end AI-powered resume customization web application that enables users to personalize their resumes based on job descriptions with AI-driven content suggestions while maintaining original formatting.

## Features
- User authentication with profile management
- Master resume upload and parsing (PDF/DOCX)
- Job description analysis with AI keyword extraction
- AI-powered content enhancement using OpenAI GPT-4.1
- Side-by-side suggestion comparison
- ATS compliance checking
- Resume export in multiple formats
- Version history and analytics

## Tech Stack
- **Backend**: FastAPI, Python 3.11+
- **Frontend**: Streamlit
- **Database**: PostgreSQL
- **AI**: OpenAI GPT-4.1 (user-provided API keys)
- **Deployment**: Render.com
- **Storage**: Render Persistent Disk

## Quick Start

### Prerequisites
- Python 3.11+
- OpenAI API Key
- PostgreSQL (for production)

### Local Development

1. Clone the repository:
```bash
git clone <your-repo-url>
cd ai-resume-customizer
```

2. Set up virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r frontend/requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the backend:
```bash
uvicorn app.main:app --reload
```

6. Run the frontend (in another terminal):
```bash
cd frontend
streamlit run streamlit_app.py
```

### Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## Project Structure

```
ai-resume-customizer/
├── app/                    # FastAPI backend
│   ├── main.py            # Main application
│   ├── config.py          # Configuration
│   ├── models/            # Data models
│   ├── api/               # API routes
│   ├── services/          # Business logic
│   ├── database/          # Database operations
│   └── utils/             # Utilities
├── frontend/              # Streamlit frontend
│   ├── streamlit_app.py   # Main frontend app
│   ├── components/        # UI components
│   └── requirements.txt   # Frontend dependencies
├── tests/                 # Test files
├── scripts/               # Deployment scripts
├── docs/                  # Documentation
├── requirements.txt       # Backend dependencies
├── .env.example          # Environment template
├── Dockerfile            # Docker configuration
├── render.yaml           # Render deployment config
└── README.md
```

## License
MIT License
