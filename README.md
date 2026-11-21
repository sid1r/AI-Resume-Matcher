# AI Resume Matcher

An AI-powered resume screening and candidate ranking system that analyzes multiple resumes against a given Job Description (JD). The application extracts candidate information, evaluates skill compatibility, calculates matching scores, and ranks candidates based on their suitability for a job role.

The system combines Natural Language Processing (NLP), semantic similarity, rule-based matching, and a weighted scoring mechanism to simplify the recruitment screening process.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Problem Statement](#problem-statement)
- [Objectives](#objectives)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [Matching Methodology](#matching-methodology)
- [Installation and Setup](#installation-and-setup)
- [Running the Application](#running-the-application)
- [Application Workflow](#application-workflow)
- [Sample Data](#sample-data)
- [API Documentation](#api-documentation)
- [Future Enhancements](#future-enhancements)

---

## Project Overview

AI Resume Matcher is a web-based recruitment assistance system designed to automate the initial stages of resume screening.

Recruiters can upload multiple resumes and provide a Job Description. The system extracts relevant information from PDF and DOCX files, identifies candidate skills and experience, and compares each candidate's profile with the job requirements.

Using Sentence Transformers and cosine similarity, the system evaluates semantic relevance in addition to matching individual skills.

Candidates are then assigned matching scores and ranked according to their overall compatibility with the Job Description.

## Problem Statement

Traditional resume screening is a time-consuming process, especially when recruiters receive a large number of applications.

Manually reviewing resumes can lead to:

- Significant time consumption.
- Difficulty identifying relevant skills.
- Inconsistent candidate evaluation.
- Challenges in comparing multiple candidates.
- Possibility of overlooking suitable candidates.

This project addresses these challenges by providing an automated resume screening and ranking system.

## Objectives

1. Automate resume information extraction.
2. Support bulk uploading of candidate resumes.
3. Extract technical skills, functional skills, education, experience, and other candidate details.
4. Analyze Job Descriptions and identify required qualifications.
5. Calculate candidate compatibility using multiple evaluation parameters.
6. Use semantic similarity to understand contextual relevance.
7. Identify matched and missing skills.
8. Rank candidates based on their overall matching scores.
9. Provide a dashboard for viewing candidate information and evaluation results.

## Key Features

### 1. Multiple Resume Upload

- Upload multiple resumes in a single operation.
- Supports PDF and DOCX file formats.
- Processes uploaded resumes individually.
- Displays successful and failed processing counts.

### 2. Resume Information Extraction

Automatically extracts the following candidate information:

| Information | Description |
|---|---|
| Candidate Name | Name of the candidate |
| Email | Candidate email address |
| Phone Number | Contact number |
| Technical Skills | Programming languages, frameworks, tools, and technologies |
| Functional Skills | Communication, teamwork, problem-solving, etc. |
| Experience | Total professional experience |
| Education | Academic qualifications |
| Previous Companies | Companies mentioned in the resume |
| Designations | Previous job roles and designations |
| Certifications | Professional certifications |
| Projects | Project titles and descriptions |

### 3. Job Description Analysis

The system analyzes the provided Job Description and identifies:

- Required technical skills.
- Functional skills.
- Required experience.
- Educational qualifications.
- Technical skill alternatives and groups.

### 4. AI-Based Semantic Matching

- Uses Sentence Transformers for text embeddings.
- Uses the `all-MiniLM-L6-v2` pretrained model.
- Converts resume and Job Description text into numerical vector representations.
- Uses cosine similarity to calculate semantic relevance.

### 5. Weighted Matching Algorithm

The system evaluates candidates using multiple parameters and combines them into an overall matching score.

### 6. Candidate Ranking

- Calculates an overall matching score for every candidate.
- Ranks candidates based on their scores.
- Displays candidate information alongside matching results.
- Helps recruiters identify candidates whose profiles best match the job requirements.

### 7. Matching Breakdown

The dashboard displays:

- Overall matching score.
- Skill matching score.
- Semantic similarity score.
- Matched technical skills.
- Missing technical skills.
- Matched functional skills.
- Missing functional skills.
- Candidate experience and education details.

### 8. Candidate Details Dashboard

Provides a detailed view of each candidate, including personal information, skills, experience, education, certifications, projects, previous companies, and matching evaluation.

### 9. Database Integration

- Uses SQLite for persistent data storage.
- Uses SQLAlchemy for database interaction.
- Stores Job Descriptions, candidate information, and matching results.

---

## Technology Stack

### Backend

- **Python** – Core programming language.
- **FastAPI** – Backend framework for building REST APIs.
- **SQLAlchemy** – Database ORM.
- **SQLite** – Database management.
- **Pydantic** – Data validation and request handling.

### Frontend

- **React.js** – Frontend library.
- **Vite** – Frontend development and build tool.
- **CSS** – Styling and dashboard layout.

### AI / Machine Learning

- **Sentence Transformers** – Semantic text embeddings.
- **all-MiniLM-L6-v2** – Pretrained sentence embedding model.
- **Scikit-learn** – Cosine similarity calculation.
- **NLP** – Resume and Job Description text analysis.

### Document Processing

- **pdfplumber** – PDF text extraction.
- **python-docx** – DOCX document processing.

### Development Tools

- Visual Studio Code
- Git
- GitHub
- Postman
- Swagger UI

---

## System Architecture

The application follows a frontend-backend architecture.

```text
                 USER / RECRUITER
                        |
                        v
               REACT FRONTEND
                  (Vite)
                        |
                        v
                 FASTAPI BACKEND
                        |
           +------------+------------+
           |            |            |
           v            v            v
       Resume       Job Description  Matching
       Router          Router         Router
           |            |            |
           v            v            v
      Document       JD Parser     Matching
      Parser                       Service
           |            |            |
           v            v            v
      Candidate     Requirements   Scoring
      Extractor      Extraction    Algorithm
           |            |            |
           +------------+------------+
                        |
                        v
                AI / NLP PROCESSING
                        |
              Sentence Transformers
                        |
                Cosine Similarity
                        |
                        v
                 CANDIDATE RANKING
                        |
                        v
                  SQLITE DATABASE
                        |
                        v
                MATCHING DASHBOARD
```

---

## Project Structure

```text
AI-Resume-Matcher/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   │
│   │   ├── ai/
│   │   │   └── __init__.py
│   │   │
│   │   ├── routers/
│   │   │   ├── __init__.py
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
│   │   ├── database.py
│   │   ├── models.py
│   │   └── main.py
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
│   ├── package-lock.json
│   └── vite.config.js
│
├── sample_data/
│   ├── sample_jd.txt
│   └── resumes/
│
├── .gitignore
└── README.md
```

---

## Matching Methodology

The application uses a weighted scoring approach to evaluate candidate suitability.

The matching score is calculated using the following project-defined weights:

| Evaluation Parameter | Weight |
|---|---:|
| Technical Skills | 40% |
| Semantic Similarity | 20% |
| Experience | 20% |
| Education | 10% |
| Functional Skills | 10% |
| **Total** | **100%** |

### Matching Formula

Overall Matching Score:

`(Technical Skills × 0.40) + (Semantic Similarity × 0.20) + (Experience × 0.20) + (Education × 0.10) + (Functional Skills × 0.10)`

Each component is evaluated and represented as a percentage before calculating the final score.

**Note:** These weights are configurable project-level choices, not an industry-standard recruitment formula.

### Semantic Similarity

The application uses the `all-MiniLM-L6-v2` Sentence Transformer model to generate embeddings for resume and Job Description text.

Cosine similarity is used to measure how closely the resume content relates to the Job Description.

This helps identify relevant information even when the exact wording differs.

---

## Installation and Setup

### Prerequisites

Make sure the following tools are installed:

- Python 3.10 or later.
- Node.js and npm.
- Git.
- Visual Studio Code (recommended).

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/AI-Resume-Matcher.git
```

Navigate to the project directory:

```bash
cd AI-Resume-Matcher
```

### 2. Create a Python Virtual Environment

```bash
python -m venv .venv
```

Activate the virtual environment.

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Backend Dependencies

```powershell
cd backend
pip install -r requirements.txt
```

### 4. Install Frontend Dependencies

Open another terminal:

```powershell
cd frontend
npm install
```

---

## Running the Application

The backend and frontend must run in separate terminals.

### Start the Backend

```powershell
cd backend
..\.venv\Scripts\Activate.ps1
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Backend URL:

`http://127.0.0.1:8000`

### Start the Frontend

```powershell
cd frontend
npm run dev
```

Frontend URL:

`http://localhost:5173`

Open the frontend URL in your browser to use the application.

---

## Application Workflow

1. **Upload Resumes:** The recruiter uploads multiple candidate resumes in PDF or DOCX format.
2. **Document Processing:** The backend extracts text from the uploaded documents.
3. **Candidate Extraction:** Candidate details, skills, experience, education, certifications, projects, and previous companies are identified.
4. **Enter Job Description:** The recruiter provides the Job Description for the required position.
5. **JD Analysis:** The system extracts technical skills, functional skills, experience requirements, and qualifications.
6. **AI Matching:** Resume and Job Description content are compared using semantic similarity and skill-based evaluation.
7. **Score Calculation:** The weighted matching algorithm calculates the overall candidate score.
8. **Candidate Ranking:** Candidates are sorted based on their matching scores.
9. **View Results:** The recruiter can view candidate rankings, matching breakdowns, matched skills, missing skills, and detailed candidate profiles.

---

## Sample Data

The project includes sample data for testing the resume screening workflow.

Sample resumes are available in PDF and DOCX formats.

You can use the sample Job Description and resumes to test:

- Single resume processing.
- Multiple resume uploads.
- PDF document extraction.
- DOCX document extraction.
- Candidate information extraction.
- Job Description parsing.
- Skill matching.
- Semantic similarity.
- Candidate ranking.
- Previous company extraction.

---

## API Documentation

FastAPI provides interactive API documentation through Swagger UI.

After starting the backend, open:

`http://127.0.0.1:8000/docs`

Swagger UI allows you to:

- Explore available API endpoints.
- View request and response schemas.
- Upload resumes and test API operations.
- Submit Job Descriptions.
- Test matching functionality.

---

## Future Enhancements

The following features can be considered for future development:

- Advanced resume parsing using large language models.
- More robust handling of different resume layouts and formats.
- Candidate filtering by experience, skills, and education.
- Exporting candidate ranking reports to PDF or Excel.
- Recruiter authentication and role-based access control.
- Cloud deployment.
- Advanced analytics and recruitment insights.
- Integration with Applicant Tracking Systems (ATS).

---

## Project Purpose

This project was developed to demonstrate the practical application of Python backend development, AI/ML, Natural Language Processing, document processing, database management, and frontend integration in an automated recruitment screening system.

**AI Resume Matcher – Making Resume Screening Smarter and More Efficient.**

---

## Author



**Sidra Rahman**  
B.Tech – Artificial Intelligence and Machine Learning  
KNS Institute of Technology, Bengaluru (VTU)

- GitHub: https://github.com/sid1r
- LinkedIn:  https://www.linkedin.com/in/sidrarahman19
- Email: sidrarahman01@gmail.com

**Project:** AI Resume Matcher  
**Technologies:** Python, FastAPI, React, SQLite, Sentence Transformers, Scikit-learn.
