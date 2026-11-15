# AI-Based Resume Matching & Candidate Ranking System

An AI-powered web application that compares multiple candidate resumes against a Job Description (JD), calculates matching scores, and ranks candidates based on their suitability for the role.

## Project Overview

The AI Resume Matching System helps recruiters evaluate multiple resumes efficiently. It extracts candidate information from PDF and DOCX files, identifies relevant skills and experience, and uses semantic similarity to compare resumes with a job description.

The application supports batch resume processing and provides a candidate ranking dashboard with detailed matching analysis.

## Key Features

### 1. Job Description Analysis
- Enter a Job Description.
- Extract required technical skills.
- Identify required experience.
- Extract educational qualifications.

### 2. Resume Upload and Parsing
- Upload multiple resumes in one batch.
- Supports PDF and DOCX formats.
- Extract candidate name, email, phone number, skills, experience and education.

### 3. AI-Based Resume Matching
- Semantic similarity using Sentence Transformers.
- Skill matching and missing skill identification.
- Candidate experience evaluation.
- Overall matching score between 0 and 100.

### 4. Candidate Ranking Dashboard
- Automatically rank candidates by matching score.
- Display candidate experience and matching percentage.
- Show matched skill counts.
- Select candidates to view detailed analysis.

### 5. Candidate-Level Analysis
- Extracted candidate information.
- Overall matching score.
- Matched and missing skills.
- Experience comparison.
- Score breakdown and reasons behind the score.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React.js |
| Frontend tooling | Vite |
| Backend | Python, FastAPI |
| Document parsing | pdfplumber, python-docx |
| Semantic matching | Sentence Transformers |
| Embedding model | all-MiniLM-L6-v2 |
| Similarity calculation | Scikit-learn |
| Numerical processing | NumPy |
| API communication | REST API |

## System Architecture

```text
                 Recruiter
                     |
                     v
          React Frontend (Vite)
                     |
                     v
             FastAPI Backend
                     |
          +----------+----------+
          |          |          |
          v          v          v
       Resume       JD       Matching
       Parser     Parser      Service
          |          |          |
          v          v          v
      Candidate   Required   Semantic
      Information Requirements Matching
          |          |          |
          +----------+----------+
                     |
                     v
             Matching Scores
                     |
                     v
             Candidate Ranking
                     |
                     v
           React Results Dashboard
                     |
                     v
           Candidate-Level Analysis
```

## Matching Algorithm

The system calculates an overall matching score using three components:

1. **Skill Matching Score (50%)**

   Measures how many required job skills are found in the candidate's resume.

   Formula:

   `Skill Score = (Matched Required Skills / Total Required Skills) × 100`

2. **Semantic Similarity Score (30%)**

   Uses the Sentence Transformers `all-MiniLM-L6-v2` model to generate embeddings for the resume and Job Description.

   Cosine similarity is calculated between the two embeddings and converted into a percentage.

3. **Experience Matching Score (20%)**

   Compares the candidate's extracted experience with the required experience.

   Formula:

   `Experience Score = (Candidate Experience / Required Experience) × 100`

   The experience score is capped at 100%.

### Final Matching Score

`Overall Score = (Skill Score × 0.50) + (Semantic Similarity × 0.30) + (Experience Score × 0.20)`

The final score is rounded to two decimal places.

Candidates are ranked in descending order of their overall matching scores.

**Note:** Skills are identified using the project's predefined skill list. Education and qualifications are extracted from the Job Description and resumes, but they are not currently included as separate components in the weighted matching formula.

## Project Structure

```text
AI-Resume-Matcher/
│
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   │   ├── resume.py
│   │   │   ├── jd.py
│   │   │   └── matching.py
│   │   │
│   │   ├── services/
│   │   │   ├── document_parser.py
│   │   │   ├── candidate_extractor.py
│   │   │   ├── jd_parser.py
│   │   │   └── matching_service.py
│   │   │
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── database.py
│   │
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   │
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── .gitignore
└── README.md
```

## Installation and Setup

### Prerequisites

- Python 3.12 or compatible version.
- Node.js and npm.
- Git.

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd AI-Resume-Matcher
```

### 2. Backend Setup

Create and activate a virtual environment.

**Windows PowerShell:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install backend dependencies:

```powershell
cd backend
pip install -r requirements.txt
```

Start the FastAPI server:

```powershell
uvicorn app.main:app --reload
```

Backend URL:

`http://127.0.0.1:8000`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

### 3. Frontend Setup

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Frontend URL:

`http://localhost:5173`

Make sure the backend is running before using the frontend.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Check application status |
| GET | `/health` | Health check |
| POST | `/resumes/extract` | Extract information from a resume |
| POST | `/resumes/batch-extract` | Extract information from multiple resumes |
| POST | `/job-description/analyze` | Analyze a Job Description |
| POST | `/matching/batch` | Match and rank multiple resumes |

## Testing

The application was tested using 10 synthetic sample resumes in PDF and DOCX formats.

Testing covered:

- Multiple resume uploads.
- PDF and DOCX text extraction.
- Candidate information extraction.
- Job Description requirement extraction.
- Skill matching.
- Semantic similarity calculation.
- Experience evaluation.
- Candidate ranking.
- Candidate-level analysis.

Only synthetic/sample resume data should be used for testing. Do not upload real candidate personal information.

## Current Scope and Limitations

- Skill extraction uses a predefined list of technical skills.
- Candidate information extraction uses rule-based text patterns.
- Semantic similarity is based on sentence embeddings and cosine similarity.
- Matching results are returned for the uploaded batch; they are not persistently stored in a database.
- The current frontend accepts pasted Job Description text.

## Future Improvements

- Persistent storage for candidate and matching results.
- More advanced skill and qualification extraction.
- Support for uploading Job Description documents.
- Improved resume parsing for different document layouts.

## Author

Developed as a practical project demonstrating Python backend development, document processing, NLP, semantic matching, and React frontend development.
