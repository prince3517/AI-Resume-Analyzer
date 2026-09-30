# AI Resume & Job Description Matcher

A Flask-based AI recruitment screening demo that compares a candidate resume with a job description.

## Features

- Upload a resume PDF
- Extract resume text
- Detect common skills in resume and job description
- Calculate skill, experience, education and semantic scores
- Produce a weighted match percentage
- Shortlist automatically at **85% or above**
- Show reasons when below 85%
- Send a shortlist email automatically when SMTP is configured
- Uses Sentence Transformers for semantic similarity when available
- Falls back to TF-IDF similarity if the transformer model cannot be loaded

## Project structure

```text
ai_resume_job_matcher/
├── app.py
├── matcher.py
├── resume_parser.py
├── email_service.py
├── requirements.txt
├── .env.example
├── README.md
├── templates/
│   └── index.html
├── static/
│   └── style.css
└── uploads/
```

## 1. Install Python

Use Python 3.10 or newer.

## 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate again.

## 3. Install packages

```powershell
pip install -r requirements.txt
```

The first use of Sentence Transformers may download the `all-MiniLM-L6-v2` model.

## 4. Configure email

Copy `.env.example` to `.env`.

For Gmail, use a Google **App Password**, not your normal Gmail password. Your Google account must have 2-Step Verification enabled.

Example:

```text
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_16_character_app_password
FROM_EMAIL=your_email@gmail.com
```

Do not commit `.env` to GitHub.

## 5. Run

```powershell
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## How the score works

The current demo uses:

- Skills: 55%
- Experience: 20%
- Education: 10%
- Semantic similarity: 15%

Final score:

```text
Skill × 0.55
+ Experience × 0.20
+ Education × 0.10
+ Semantic similarity × 0.15
```

If the final score is **85% or higher**, the candidate is marked shortlisted.

If it is below 85%, the application displays missing skills and other detected gaps.

## Important project limitation

This is an educational prototype, not a production hiring decision system. A resume score can miss relevant experience because of wording, formatting, incomplete resumes, or limitations in the skill dictionary/model.

For a production system, add human review, candidate consent/privacy controls, audit logs, bias testing, and a validated scoring model.

## Suggested next upgrades

1. Recruiter login
2. Multiple resumes at once
3. Candidate database
4. Job-description database
5. Dashboard
6. More complete skill taxonomy
7. LLM-based structured resume extraction
8. Explainable scoring
9. Admin-configurable threshold
10. Docker deployment
