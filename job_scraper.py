import streamlit as st
import requests
import pandas as pd
from groq import Groq
import os
import json
from dotenv import load_dotenv

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
JSEARCH_API_KEY = os.getenv("JSEARCH_API_KEY")  # RapidAPI key


def get_jsearch_jobs(job_title, location="India"):
    jobs = []
    try:
        query = f"{job_title} in {location}" if location else f"{job_title} in India"
        url = "https://jsearch.p.rapidapi.com/search"
        headers = {
            "X-RapidAPI-Key": JSEARCH_API_KEY,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }
        params = {
            "query": query,
            "page": "1",
            "num_pages": "1",
            "country": "in",
            "date_posted": "month"
        }
        response = requests.get(url, headers=headers, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            for job in data.get("data", []):
                # Salary
                min_sal = job.get("job_min_salary")
                max_sal = job.get("job_max_salary")
                sal_currency = job.get("job_salary_currency", "INR")
                sal_period = job.get("job_salary_period", "")
                if min_sal and max_sal:
                    salary = f"{sal_currency} {int(min_sal):,} - {int(max_sal):,} / {sal_period}"
                else:
                    salary = "Not disclosed"

                jobs.append({
                    "Job Title": job.get("job_title", "N/A"),
                    "Company": job.get("employer_name", "N/A"),
                    "Location": f"{job.get('job_city', '')} {job.get('job_state', '')}".strip() or job.get("job_country", "India"),
                    "Salary": salary,
                    "Employment Type": job.get("job_employment_type", "N/A"),
                    "Experience": job.get("job_required_experience", {}).get("required_experience_in_months", "N/A"),
                    "Description": (job.get("job_description", "N/A") or "")[:300] + "...",
                    "Link": job.get("job_apply_link", "#"),
                    "Posted": (job.get("job_posted_at_datetime_utc") or "N/A")[:10],
                    "Source": f"{job.get('job_publisher', 'JSearch')} ✅"
                })
        else:
            st.error(f"JSearch API error: {response.status_code} — {response.text}")
    except Exception as e:
        st.error(f"JSearch error: {e}")
    return jobs


def get_ai_jobs_fallback(job_title, location, num_jobs=8):
    prompt = f"""
    Generate {num_jobs} realistic job listings for "{job_title}" jobs in "{location or 'India'}".
    Return ONLY a JSON array with no extra text:
    [
      {{
        "Job Title": "Senior React Developer",
        "Company": "Infosys",
        "Location": "Bengaluru, Karnataka",
        "Salary": "₹8,00,000 - ₹15,00,000 per year",
        "Employment Type": "Full-time",
        "Experience": "3-5 years",
        "Description": "We are looking for a skilled React developer...",
        "Link": "https://www.naukri.com",
        "Posted": "2025-06-01",
        "Source": "AI Generated 🤖"
      }}
    ]
    Use realistic Indian companies (TCS, Infosys, Wipro, HCL, Flipkart, Swiggy, Zomato, etc.) and INR salaries.
    Return ONLY valid JSON, no markdown.
    """
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000
    )
    text = response.choices[0].message.content.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)


def get_market_insights(jobs, job_title):
    if not jobs:
        return "No jobs to analyze."
    jobs_text = "\n".join([
        f"- {j.get('Job Title')} at {j.get('Company')} | {j.get('Location')} | {j.get('Salary', 'N/A')}"
        for j in jobs[:6]
    ])
    prompt = f"""
    Based on these {job_title} job listings in India:
    {jobs_text}

    Provide:
    1. 🔥 Top 5 most in-demand skills
    2. 📈 Market trend in India 2025
    3. 💰 Salary ranges in INR (fresher/mid/senior)
    4. 🏢 Top Indian companies hiring
    5. 💡 3 tips to get hired faster in India

    Keep it concise and actionable. Focus on Indian job market.
    """
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800
    )
    return response.choices[0].message.content


def show_job_scraper():
    st.title("🔍 Live Job Finder")
    st.markdown("Real jobs from **Google for Jobs / LinkedIn / Indeed (India)** + AI-powered market insights!")

    col1, col2, col3 = st.columns(3)
    with col1:
        job_title = st.text_input("Job Title", placeholder="e.g. React Developer")
    with col2:
        location = st.text_input("Location", placeholder="e.g. Bengaluru, Mumbai, Delhi")
    with col3:
        source = st.selectbox("Source", [
            "🌐 JSearch (Real Indian Jobs)",
            "🤖 AI Generated"
        ])

    if st.button("🔍 Find Jobs", type="primary"):
        if not job_title:
            st.error("Please enter a job title!")
            return

        all_jobs = []

        with st.spinner("🔍 Fetching live jobs from India..."):
            if source == "🌐 JSearch (Real Indian Jobs)":
                if not JSEARCH_API_KEY:
                    st.error("❌ JSEARCH_API_KEY not found in .env file! Get it free at rapidapi.com/jsearch")
                    return
                all_jobs = get_jsearch_jobs(job_title, location)
                if not all_jobs:
                    st.warning("No live jobs found. Switching to AI mode...")
                    all_jobs = get_ai_jobs_fallback(job_title, location)
            else:
                all_jobs = get_ai_jobs_fallback(job_title, location)

        if all_jobs:
            st.success(f"🎉 Found {len(all_jobs)} jobs!")
            st.markdown("---")

            for job in all_jobs:
                with st.expander(
                    f"🏢 {job.get('Job Title')} — {job.get('Company')} | 📍 {job.get('Location')} | {job.get('Source', '')}"
                ):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**💰 Salary:** {job.get('Salary', 'Not disclosed')}")
                        st.write(f"**💼 Type:** {job.get('Employment Type', 'N/A')}")
                        st.write(f"**📅 Posted:** {job.get('Posted', 'N/A')}")
                    with col2:
                        link = job.get('Link', '#')
                        if link and link != '#':
                            st.markdown(f"[🔗 Apply Now]({link})")
                    st.write(f"**📝 Description:** {job.get('Description', 'N/A')}")

            st.markdown("---")
            df = pd.DataFrame(all_jobs)
            csv = df.to_csv(index=False)
            st.download_button(
                "📥 Download Jobs CSV",
                csv, f"{job_title}_india_jobs.csv", "text/csv"
            )

            st.subheader("🤖 AI Market Insights (India)")
            with st.spinner("Analyzing Indian market trends..."):
                insights = get_market_insights(all_jobs, job_title)
            st.markdown(insights)
        else:
            st.warning("No jobs found. Try different keywords or switch to AI mode!")