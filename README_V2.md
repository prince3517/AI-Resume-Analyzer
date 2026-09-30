# AI Resume & Job Description Matcher — Version 2

Version 2 converts the first prototype into a recruiter-style screening application.

## New features

- Recruiter dashboard
- Create and save multiple job descriptions
- Configurable shortlist threshold per job
- SQLite database
- Multiple PDF resume upload
- Candidate history
- Candidate detail page
- Score breakdown
- Missing-skill explanations
- Shortlist email automation
- JSON statistics API
- Better 50/20/10/20 scoring model

## Folder structure

```text
AI_Resume_Job_Matcher_V2/
├── app.py
├── database.py
├── matcher.py
├── resume_parser.py
├── email_service.py
├── requirements.txt
├── README_V2.md
├── templates/
│   ├── dashboard.html
│   ├── job_form.html
│   ├── job_detail.html
│   └── candidate_detail.html
├── static/
│   └── style.css
└── uploads/
```

## Run

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## Email

Create a `.env` file:

```text
FLASK_SECRET_KEY=change-this
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_google_app_password
FROM_EMAIL=your_email@gmail.com
```

For Gmail, use a Google App Password rather than your normal account password.

## Scoring

Version 2 uses:

- Skills: 50%
- Experience: 20%
- Education: 10%
- Semantic similarity: 20%

Each job can have its own threshold; the default is 85%.

## Important

The score is an automated screening aid, not a complete hiring decision. Real deployments should add human review, privacy/consent controls, audit logs, security, bias testing, and validation against real labeled hiring data.
