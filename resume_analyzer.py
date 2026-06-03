import streamlit as st
import fitz
import os
import io
import re
from groq import Groq
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("❌ GROQ_API_KEY not found in .env file!")
    st.stop()

client = Groq(api_key=api_key)


def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def analyze_resume(resume_text, job_description):
    """
    Strict ATS scoring — forces the model to count keyword matches
    before assigning a score, so it can't round-up generously.
    """
    prompt = f"""
You are a strict ATS (Applicant Tracking System) scanner. You do NOT give compliments — you give accurate scores.

STEP 1 — Extract every required keyword/skill/tool from the job description below.
STEP 2 — For each keyword, check if it appears (exact or close synonym) in the resume.
STEP 3 — Calculate: score = (matched keywords / total keywords) * 100, then apply penalties:
  - Deduct 5 pts if no quantified achievements (numbers/metrics) in experience
  - Deduct 5 pts if no strong professional summary tailored to role
  - Deduct 3 pts for each major required skill completely missing

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Respond in EXACTLY this format (no deviations):

ATS Score: XX/100

📋 Keyword Match Analysis:
Total keywords in JD: N
Matched in resume: N
Match rate: XX%

✅ Top 5 Strengths:
1. ...
2. ...
3. ...
4. ...
5. ...

❌ Top 5 Gaps / Areas to Improve:
1. ...
2. ...
3. ...
4. ...
5. ...

🔑 Missing Keywords (must add to resume):
keyword1, keyword2, keyword3, keyword4, keyword5 ...

📌 Overall Recommendation:
[2-3 sentences — be direct and honest]
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500
    )
    return response.choices[0].message.content


def improve_resume(resume_text, job_description, analysis):
    """
    Targeted improvement — explicitly uses the missing keywords list
    from the analysis to rewrite bullet points.
    """
    # Pull missing keywords out of the analysis to give the model a concrete list
    missing_match = re.search(
        r'Missing Keywords[^:]*:(.*?)(?:\n\n|\n📌|\Z)', analysis, re.DOTALL | re.IGNORECASE
    )
    missing_keywords = missing_match.group(1).strip() if missing_match else "See analysis above"

    prompt = f"""
You are a professional resume writer and ATS optimization expert.

YOUR GOAL: Rewrite the resume so it scores 95+ on ATS for this specific job.

ORIGINAL RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

MISSING KEYWORDS THAT MUST BE ADDED:
{missing_keywords}

MANDATORY RULES:
1. Keep every real fact: name, contact info, company names, job titles, dates, education, GPA
2. DO NOT invent experience, tools, or projects the person never had
3. Every missing keyword above MUST appear naturally in the rewritten resume
   — weave them into existing bullet points or skills section, not as a separate list
4. Rewrite ALL experience bullets using: Action Verb + Task + Result/Impact + Number where possible
   Example bad:  "Worked on React components"
   Example good: "Engineered 12+ reusable React components reducing UI build time by 35%"
5. Write a 3-sentence Professional Summary that mirrors the job description language exactly
6. Put Skills section BEFORE Experience (ATS scans top-down)
7. Remove every filler phrase: "responsible for", "assisted with", "helped", "worked on"

OUTPUT: Return ONLY the improved resume. No commentary. No explanation. No markdown code blocks.

FORMAT:
[Full Name]
[email] | [phone] | [location] | [linkedin/github if exists]

PROFESSIONAL SUMMARY
[3 tailored sentences using JD language]

TECHNICAL SKILLS
[Grouped by category, include ALL missing keywords here too]

EXPERIENCE
[Job Title] | [Company] | [Start – End]
• [Strong bullet]
• [Strong bullet]
• [Strong bullet]

EDUCATION
[Degree] | [College] | [Year]

PROJECTS
[Name] | [Tech stack]
• [Impact-focused bullet]

CERTIFICATIONS
• [If any]
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=3000
    )
    return response.choices[0].message.content


def rescore_improved(original_resume, improved_resume, job_description, original_analysis):
    """
    Comparative rescoring — forces the model to compare both versions
    and explain why the score changed (or didn't).
    """
    orig_score = extract_ats_score(original_analysis)

    prompt = f"""
You are a strict ATS auditor. You are comparing TWO versions of a resume for the SAME job.

JOB DESCRIPTION:
{job_description}

VERSION A (ORIGINAL — scored {orig_score}/100 previously):
{original_resume}

VERSION B (IMPROVED — you must score this independently):
{improved_resume}

INSTRUCTIONS:
1. Re-extract all required keywords from the JD
2. Count how many appear in Version B (be strict — partial matches count 0.5)
3. Check if Version B fixed the weaknesses from Version A
4. Calculate Version B's score using the SAME strict formula:
   score = (matched / total) * 100, minus penalties for missing metrics, weak summary, major gaps

RESPOND IN EXACTLY THIS FORMAT:

New ATS Score: XX/100

📊 Score Comparison:
Original score: {orig_score}/100
New score: XX/100
Change: +X pts / -X pts

🔍 What Improved:
• [specific thing that changed and helped]
• [specific thing that changed and helped]

⚠️ Still Missing (fix these for 95+):
• [keyword or issue still absent]
• [keyword or issue still absent]

📌 Verdict:
[1-2 honest sentences on whether the improvement was real or cosmetic]
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800
    )
    return response.choices[0].message.content


def extract_ats_score(text):
    """Extract ATS score number from analysis text."""
    for pattern in [
        r'(?:New\s+)?ATS Score[:\s]+(\d{1,3})\s*/\s*100',
        r'(?:New\s+)?ATS Score[:\s]+(\d{1,3})',
        r'New score[:\s]+(\d{1,3})',
        r'\b([6-9]\d|100)\b',
    ]:
        match = re.search(pattern, text[:500], re.IGNORECASE)
        if match:
            val = int(match.group(1))
            if 0 <= val <= 100:
                return val
    return None


def generate_pdf(resume_text):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        rightMargin=0.75*inch, leftMargin=0.75*inch,
        topMargin=0.75*inch,  bottomMargin=0.75*inch
    )
    styles = getSampleStyleSheet()

    name_style = ParagraphStyle("N", parent=styles["Normal"], fontSize=20,
        fontName="Helvetica-Bold", textColor=colors.HexColor("#1a1a2e"),
        spaceAfter=4, alignment=TA_CENTER)
    contact_style = ParagraphStyle("C", parent=styles["Normal"], fontSize=9,
        fontName="Helvetica", textColor=colors.HexColor("#555555"),
        spaceAfter=8, alignment=TA_CENTER)
    section_style = ParagraphStyle("S", parent=styles["Normal"], fontSize=11,
        fontName="Helvetica-Bold", textColor=colors.HexColor("#7c3aed"),
        spaceBefore=12, spaceAfter=4)
    body_style = ParagraphStyle("B", parent=styles["Normal"], fontSize=9.5,
        fontName="Helvetica", textColor=colors.HexColor("#2d2d2d"),
        spaceAfter=3, leading=14)
    bullet_style = ParagraphStyle("BL", parent=styles["Normal"], fontSize=9.5,
        fontName="Helvetica", textColor=colors.HexColor("#2d2d2d"),
        spaceAfter=2, leftIndent=16, leading=14)
    subheader_style = ParagraphStyle("SH", parent=styles["Normal"], fontSize=10,
        fontName="Helvetica-Bold", textColor=colors.HexColor("#1a1a2e"), spaceAfter=2)

    story = []
    lines = resume_text.strip().split("\n")
    i = 0

    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines):
        story.append(Paragraph(lines[i].strip(), name_style))
        i += 1

    contact_lines = []
    while i < len(lines) and lines[i].strip() and not lines[i].strip().isupper():
        contact_lines.append(lines[i].strip())
        i += 1
    if contact_lines:
        story.append(Paragraph(" | ".join(contact_lines), contact_style))

    story.append(HRFlowable(width="100%", thickness=1.5,
                             color=colors.HexColor("#7c3aed"), spaceAfter=6))

    while i < len(lines):
        line = lines[i].strip()
        if not line:
            story.append(Spacer(1, 3))
        elif line.isupper() and len(line) > 2:
            story.append(Paragraph(line, section_style))
            story.append(HRFlowable(width="100%", thickness=0.5,
                                     color=colors.HexColor("#e0d4ff"), spaceAfter=4))
        elif line.startswith(("•", "-", "*")):
            story.append(Paragraph(f"• {line.lstrip('•-* ').strip()}", bullet_style))
        elif "|" in line:
            story.append(Paragraph(line, subheader_style))
        else:
            story.append(Paragraph(line, body_style))
        i += 1

    doc.build(story)
    buffer.seek(0)
    return buffer


def show_resume_analyzer():
    st.title("📄 Resume Analyzer")
    st.markdown("Upload your resume and get a **strict, honest ATS score** with improvement tips!")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Upload Your Resume")
        pdf_file = st.file_uploader("Choose your resume (PDF only)", type=["pdf"])
    with col2:
        st.subheader("Paste Job Description")
        job_description = st.text_area(
            "Copy and paste the job description here",
            height=200,
            placeholder="Paste the job description you are applying for..."
        )

    if st.button("🔍 Analyze My Resume", type="primary"):
        if pdf_file is None:
            st.error("Please upload your resume PDF!")
        elif not job_description:
            st.error("Please paste a job description!")
        else:
            with st.spinner("🤖 Strictly analyzing your resume..."):
                resume_text = extract_text_from_pdf(pdf_file)
                st.session_state["resume_text"]    = resume_text
                st.session_state["job_description"] = job_description
                st.session_state.pop("improved_resume", None)
                st.session_state.pop("new_analysis", None)
                result = analyze_resume(resume_text, job_description)
                st.session_state["analysis_result"] = result

    # ── Original analysis display ────────────────────────────────────────────
    if "analysis_result" in st.session_state and "improved_resume" not in st.session_state:
        result = st.session_state["analysis_result"]
        score  = extract_ats_score(result)

        st.success("✅ Analysis Complete!")
        st.markdown("---")

        if score is not None:
            color = "#22c55e" if score >= 80 else "#f59e0b" if score >= 60 else "#ef4444"
            st.markdown(
                f'<div style="text-align:center;padding:20px;border-radius:12px;'
                f'background:#1e1e2e;border:2px solid {color};margin-bottom:16px;">'
                f'<span style="font-size:3rem;font-weight:900;color:{color};">{score}</span>'
                f'<span style="font-size:1.5rem;color:#aaa;">/100</span>'
                f'<div style="color:#aaa;margin-top:4px;font-size:0.9rem;">ATS Score</div></div>',
                unsafe_allow_html=True
            )

        st.markdown(result)
        st.download_button("📥 Download Analysis", result,
                           "resume_analysis.txt", "text/plain")

    # ── Improve section ──────────────────────────────────────────────────────
    if "analysis_result" in st.session_state:
        st.markdown("---")
        st.subheader("🚀 AI Resume Improver")
        st.markdown("Rewrites your resume to target **95+ ATS** by injecting every missing keyword into your existing experience.")

        if st.button("✨ Auto-Improve My Resume", type="primary"):
            with st.spinner("🤖 Rewriting resume with targeted keyword injection..."):
                improved = improve_resume(
                    st.session_state["resume_text"],
                    st.session_state["job_description"],
                    st.session_state["analysis_result"]
                )
                st.session_state["improved_resume"] = improved
                st.session_state.pop("new_analysis", None)

    # ── Improved resume display ──────────────────────────────────────────────
    if "improved_resume" in st.session_state:
        improved = st.session_state["improved_resume"]

        st.success("✅ Resume rewritten with keyword optimization!")
        st.markdown("---")
        st.markdown(
            f'<div style="background:#1e1e2e;padding:24px;border-radius:10px;'
            f'border-left:4px solid #7c3aed;white-space:pre-wrap;font-size:13.5px;'
            f'line-height:1.7;font-family:monospace;">{improved}</div>',
            unsafe_allow_html=True
        )

        # ── Comparative re-score ─────────────────────────────────────────────
        st.markdown("---")
        st.subheader("🎯 Compare ATS Scores")
        st.markdown("Scores the **improved version vs original** using keyword counting — no re-upload needed.")

        if st.button("📊 Check New ATS Score", type="secondary", use_container_width=True):
            with st.spinner("🤖 Comparing original vs improved resume..."):
                new_analysis = rescore_improved(
                    st.session_state["resume_text"],
                    improved,
                    st.session_state["job_description"],
                    st.session_state["analysis_result"]
                )
                st.session_state["new_analysis"] = new_analysis

        if "new_analysis" in st.session_state:
            new_text   = st.session_state["new_analysis"]
            old_score  = extract_ats_score(st.session_state["analysis_result"])
            new_score  = extract_ats_score(new_text)

            if old_score and new_score:
                delta = new_score - old_score
                delta_label = f"+{delta}" if delta >= 0 else str(delta)
                mood = "🎉 Real improvement!" if delta > 3 else (
                       "✅ Slight gain" if delta >= 0 else "⚠️ Try improving again")

                old_color = "#ef4444" if old_score < 70 else "#f59e0b" if old_score < 85 else "#22c55e"
                new_color = "#ef4444" if new_score < 70 else "#f59e0b" if new_score < 85 else "#22c55e"

                c1, c2, c3 = st.columns(3)
                c1.metric("📄 Original", f"{old_score}/100")
                c2.metric("✨ Improved", f"{new_score}/100", delta_label)
                c3.metric("📈 Change",   f"{delta_label} pts", mood)

                # Visual score bars
                st.markdown(
                    f'<div style="display:flex;gap:12px;margin:16px 0;">'
                    f'<div style="flex:1;background:#1e1e2e;border-radius:8px;padding:12px;">'
                    f'<div style="color:#aaa;font-size:0.8rem;margin-bottom:6px;">Original</div>'
                    f'<div style="height:8px;background:#333;border-radius:4px;">'
                    f'<div style="width:{old_score}%;height:100%;background:{old_color};border-radius:4px;"></div></div>'
                    f'<div style="color:{old_color};font-weight:bold;margin-top:4px;">{old_score}%</div></div>'
                    f'<div style="flex:1;background:#1e1e2e;border-radius:8px;padding:12px;">'
                    f'<div style="color:#aaa;font-size:0.8rem;margin-bottom:6px;">Improved</div>'
                    f'<div style="height:8px;background:#333;border-radius:4px;">'
                    f'<div style="width:{new_score}%;height:100%;background:{new_color};border-radius:4px;"></div></div>'
                    f'<div style="color:{new_color};font-weight:bold;margin-top:4px;">{new_score}%</div></div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            st.markdown("---")
            st.markdown(new_text)

        # ── Downloads ────────────────────────────────────────────────────────
        st.markdown("---")
        st.subheader("📥 Download Improved Resume")
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📄 Download as TXT", improved,
                "improved_resume.txt", "text/plain",
                use_container_width=True
            )
        with col2:
            pdf_buffer = generate_pdf(improved)
            st.download_button(
                "📑 Download as PDF", pdf_buffer,
                "improved_resume.pdf", "application/pdf",
                use_container_width=True
            )