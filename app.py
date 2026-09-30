import webbrowser
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from database import init_db, get_db
from resume_parser import extract_text_from_pdf
from matcher import analyze_match, THRESHOLD

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

init_db()


def save_candidate_result(name, email, filename, job_id, result):
    db = get_db()
    db.execute("""
        INSERT INTO candidates
        (name, email, resume_filename, job_id, score, shortlisted,
         matched_skills, missing_skills, reasons, skill_score,
         experience_score, education_score, semantic_score, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name, email, filename, job_id, result["score"], int(result["shortlisted"]),
        ", ".join(result["matched_skills"]),
        ", ".join(result["missing_skills"]),
        " | ".join(result["reasons"]),
        result["skill_score"], result["experience_score"],
        result["education_score"], result["semantic_score"],
        datetime.now().isoformat(timespec="seconds")
    ))
    db.commit()


@app.route("/")
def dashboard():
    db = get_db()
    jobs = db.execute("SELECT * FROM jobs ORDER BY id DESC").fetchall()
    stats = {
        "total": db.execute("SELECT COUNT(*) c FROM candidates").fetchone()["c"],
        "shortlisted": db.execute("SELECT COUNT(*) c FROM candidates WHERE shortlisted=1").fetchone()["c"],
        "rejected": db.execute("SELECT COUNT(*) c FROM candidates WHERE shortlisted=0").fetchone()["c"],
        "jobs": db.execute("SELECT COUNT(*) c FROM jobs").fetchone()["c"],
    }
    recent = db.execute("""
        SELECT candidates.*, jobs.title job_title
        FROM candidates LEFT JOIN jobs ON jobs.id = candidates.job_id
        ORDER BY candidates.id DESC LIMIT 10
    """).fetchall()
    return render_template("dashboard.html", jobs=jobs, stats=stats, recent=recent, threshold=THRESHOLD)


@app.route("/jobs/new", methods=["GET", "POST"])
def new_job():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        threshold = float(request.form.get("threshold") or THRESHOLD)

        if not title or not description:
            flash("Job title and description are required.")
            return render_template("job_form.html")

        db = get_db()
        db.execute(
            "INSERT INTO jobs(title, description, threshold, created_at) VALUES (?, ?, ?, ?)",
            (title, description, threshold, datetime.now().isoformat(timespec="seconds"))
        )
        db.commit()
        flash("Job created successfully.")
        return redirect(url_for("dashboard"))

    return render_template("job_form.html", default_threshold=THRESHOLD)


@app.route("/jobs/<int:job_id>")
def job_detail(job_id):
    db = get_db()
    job = db.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    if not job:
        flash("Job not found.")
        return redirect(url_for("dashboard"))

    candidates = db.execute("""
        SELECT * FROM candidates WHERE job_id=? ORDER BY score DESC, id DESC
    """, (job_id,)).fetchall()
    return render_template("job_detail.html", job=job, candidates=candidates)


@app.route("/jobs/<int:job_id>/screen", methods=["POST"])
def screen_resumes(job_id):
    db = get_db()
    job = db.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    if not job:
        flash("Job not found.")
        return redirect(url_for("dashboard"))

    resumes = request.files.getlist("resumes")
    processed = 0

    for resume in resumes:
        if not resume or not resume.filename.lower().endswith(".pdf"):
            continue

        filename = secure_filename(resume.filename)
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        resume.save(path)

        try:
            text = extract_text_from_pdf(path)
            result = analyze_match(text, job["description"], threshold=job["threshold"])

            # Try to extract a useful default name/email from the form; email can
            # later be edited in the candidate detail workflow.
            candidate_name = request.form.get("candidate_name", "").strip() or os.path.splitext(filename)[0]
            candidate_email = request.form.get("candidate_email", "").strip()

            save_candidate_result(candidate_name, candidate_email, filename, job_id, result)

            if result["shortlisted"] and candidate_email:
                from email_service import send_shortlist_email
                send_shortlist_email(candidate_email, candidate_name, result["score"])

            processed += 1
        except Exception as exc:
            flash(f"{filename}: {exc}")

    flash(f"Processed {processed} resume(s).")
    return redirect(url_for("job_detail", job_id=job_id))


@app.route("/candidates/<int:candidate_id>")
def candidate_detail(candidate_id):
    db = get_db()
    candidate = db.execute("""
        SELECT candidates.*, jobs.title job_title, jobs.description job_description
        FROM candidates LEFT JOIN jobs ON jobs.id = candidates.job_id
        WHERE candidates.id=?
    """, (candidate_id,)).fetchone()
    if not candidate:
        flash("Candidate not found.")
        return redirect(url_for("dashboard"))
    return render_template("candidate_detail.html", candidate=candidate)


@app.route("/api/stats")
def api_stats():
    db = get_db()
    return jsonify({
        "total": db.execute("SELECT COUNT(*) c FROM candidates").fetchone()["c"],
        "shortlisted": db.execute("SELECT COUNT(*) c FROM candidates WHERE shortlisted=1").fetchone()["c"],
        "rejected": db.execute("SELECT COUNT(*) c FROM candidates WHERE shortlisted=0").fetchone()["c"],
    })


if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:5000")
    app.run(debug=True)