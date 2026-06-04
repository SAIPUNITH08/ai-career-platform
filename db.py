"""
Supabase database helpers — all user activity is stored here.

Tables (run the SQL in supabase_setup.sql to create them):
  user_activity   – one row per event (resume_analyzed, job_searched, email_generated, skill_analyzed)
  resume_scores   – history of ATS scores per user
"""

import streamlit as st
from auth import get_supabase, get_user_id
from datetime import datetime, timezone


# ── Generic activity logger ──────────────────────────────────────────────────

def log_activity(activity_type: str, metadata: dict = None):
    """Log any user activity to the user_activity table."""
    uid = get_user_id()
    if not uid:
        return
    try:
        sb = get_supabase()
        sb.table("user_activity").insert({
            "user_id":       uid,
            "activity_type": activity_type,
            "metadata":      metadata or {},
            "created_at":    datetime.now(timezone.utc).isoformat(),
        }).execute()
    except Exception as e:
        # Never crash the main app because of a logging failure
        pass


def log_resume_score(score: int, job_title: str = "", improved_score: int = None):
    """Log a resume ATS score event."""
    uid = get_user_id()
    if not uid:
        return
    try:
        sb = get_supabase()
        sb.table("resume_scores").insert({
            "user_id":       uid,
            "score":         score,
            "improved_score": improved_score,
            "job_title":     job_title,
            "created_at":    datetime.now(timezone.utc).isoformat(),
        }).execute()
        log_activity("resume_analyzed", {"score": score, "job_title": job_title})
    except Exception as e:
        pass


def log_job_search(job_title: str, location: str, jobs_found: int):
    log_activity("job_searched", {
        "job_title":  job_title,
        "location":   location,
        "jobs_found": jobs_found,
    })


def log_email_generated(email_type: str, company: str = ""):
    log_activity("email_generated", {"email_type": email_type, "company": company})


def log_skill_analyzed(role: str, match_score: int):
    log_activity("skill_analyzed", {"role": role, "match_score": match_score})


# ── Dashboard data fetchers ──────────────────────────────────────────────────

def get_user_stats() -> dict:
    """Return aggregate counts for the current user."""
    uid = get_user_id()
    if not uid:
        return {}
    try:
        sb = get_supabase()
        rows = (
            sb.table("user_activity")
            .select("activity_type")
            .eq("user_id", uid)
            .execute()
            .data
        )
        counts = {
            "resume_analyzed": 0,
            "job_searched":    0,
            "email_generated": 0,
            "skill_analyzed":  0,
        }
        for r in rows:
            t = r.get("activity_type", "")
            if t in counts:
                counts[t] += 1
        return counts
    except Exception:
        return {}


def get_resume_score_history() -> list:
    """Return list of resume score records for current user, newest first."""
    uid = get_user_id()
    if not uid:
        return []
    try:
        sb = get_supabase()
        return (
            sb.table("resume_scores")
            .select("*")
            .eq("user_id", uid)
            .order("created_at", desc=True)
            .limit(20)
            .execute()
            .data
        )
    except Exception:
        return []


def get_recent_activity(limit: int = 10) -> list:
    """Return recent activity rows for current user."""
    uid = get_user_id()
    if not uid:
        return []
    try:
        sb = get_supabase()
        return (
            sb.table("user_activity")
            .select("*")
            .eq("user_id", uid)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
            .data
        )
    except Exception:
        return []


def get_latest_resume_score() -> int | None:
    history = get_resume_score_history()
    if history:
        return history[0].get("score")
    return None