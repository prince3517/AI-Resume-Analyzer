import sqlite3
from flask import g

DATABASE = "resume_matcher.db"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


def init_db():
    db = sqlite3.connect(DATABASE)
    db.executescript("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        threshold REAL NOT NULL DEFAULT 85,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT,
        resume_filename TEXT NOT NULL,
        job_id INTEGER,
        score REAL NOT NULL,
        shortlisted INTEGER NOT NULL,
        matched_skills TEXT,
        missing_skills TEXT,
        reasons TEXT,
        skill_score REAL,
        experience_score REAL,
        education_score REAL,
        semantic_score REAL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(job_id) REFERENCES jobs(id)
    );
    """)
    db.commit()
    db.close()
