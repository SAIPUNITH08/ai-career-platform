import streamlit as st


st.set_page_config(
    page_title="AI Career Intelligence Platform",
    page_icon="💼",
    layout="wide",
)


PAGES = {
    "home": {
        "label": "Home",
        "icon": "🏠",
        "description": "Overview",
    },
    "resume": {
        "label": "Resume Analyzer",
        "icon": "📄",
        "description": "ATS scoring",
    },
    "jobs": {
        "label": "Job Scraper",
        "icon": "🔍",
        "description": "Live jobs",
    },
    "email": {
        "label": "Email Generator",
        "icon": "✉️",
        "description": "Outreach",
    },
    "dashboard": {
        "label": "Dashboard",
        "icon": "📊",
        "description": "Market trends",
    },
}


def get_active_page():
    page = st.query_params.get("page", "home")
    return page if page in PAGES else "home"


def render_sidebar(active_page):
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] {
                background: #0f1115;
                border-right: 1px solid rgba(255, 255, 255, 0.08);
            }

            [data-testid="stSidebar"] > div:first-child {
                padding-top: 1.5rem;
            }

            .sidebar-brand {
                display: flex;
                align-items: center;
                gap: 0.8rem;
                padding: 0.4rem 0.3rem 1.4rem;
                border-bottom: 1px solid rgba(255, 255, 255, 0.08);
                margin-bottom: 1.2rem;
            }

            .brand-mark {
                width: 52px;
                height: 52px;
                display: grid;
                place-items: center;
                border-radius: 14px;
                background: linear-gradient(135deg, #b8ff3d 0%, #65f06e 100%);
                color: #111827;
                font-size: 1.05rem;
                font-weight: 900;
                letter-spacing: 0;
                box-shadow: 0 0 24px rgba(184, 255, 61, 0.22);
            }

            .brand-title {
                color: #f9fafb;
                font-size: 1.05rem;
                font-weight: 800;
                line-height: 1.05;
            }

            .brand-subtitle {
                color: #7d8793;
                font-size: 0.72rem;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                margin-top: 0.12rem;
            }

            .nav-list {
                display: flex;
                flex-direction: column;
                gap: 0.35rem;
            }

            .nav-item {
                display: flex;
                align-items: center;
                gap: 0.8rem;
                padding: 0.82rem 0.9rem;
                border-radius: 10px;
                color: #8b949e !important;
                text-decoration: none !important;
                border: 1px solid transparent;
                transition: background 150ms ease, color 150ms ease, border 150ms ease;
            }

            .nav-item:hover {
                color: #e5e7eb !important;
                background: rgba(255, 255, 255, 0.045);
                border-color: rgba(255, 255, 255, 0.06);
            }

            .nav-item.active {
                color: #d7ff65 !important;
                background: rgba(184, 255, 61, 0.15);
                border-color: rgba(184, 255, 61, 0.12);
                font-weight: 800;
            }

            .nav-icon {
                width: 1.35rem;
                text-align: center;
                font-size: 1.05rem;
            }

            .nav-text {
                display: flex;
                flex-direction: column;
                gap: 0.05rem;
            }

            .nav-label {
                font-size: 0.98rem;
                line-height: 1.15;
            }

            .nav-description {
                color: #626a75;
                font-size: 1rem;
                font-weight: 500;
            }

            .sidebar-footer {
                position: fixed;
                bottom: 1.1rem;
                left: 1.45rem;
                color: #6b7280;
                font-size: 0.78rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    nav_links = []
    for slug, item in PAGES.items():
        active_class = " active" if slug == active_page else ""
        nav_links.append(
            f"""<a class="nav-item{active_class}" href="?page={slug}" target="_self">
<span class="nav-icon">{item["icon"]}</span>
<span class="nav-text">
<span class="nav-label">{item["label"]}</span>
<span class="nav-description">{item["description"]}</span>
</span>
</a>"""
        )

    st.sidebar.markdown(
        f"""<div class="sidebar-brand">
<div class="brand-mark">AI</div>
<div>
<div class="brand-title">AI Career</div>
<div class="brand-subtitle">Platform</div>
</div>
</div>
<div class="nav-list">
{''.join(nav_links)}
</div>
<div class="sidebar-footer">Career tools powered by AI</div>""",
        unsafe_allow_html=True,
    )


page = get_active_page()
render_sidebar(page)


if page == "home":
    st.title("💼 AI Career Intelligence Platform")
    st.markdown("### Your AI-powered career assistant")
    st.markdown(
        """
    ## Welcome! 👋
    This platform helps you:
    - 📄 **Analyze your resume** and get ATS score
    - 🔍 **Find live jobs** matching your skills
    - ✉️ **Generate cold emails** to recruiters
    - 📊 **Explore job market** trends
    """
    )
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Resume Score", "0%", "Upload resume")
    col2.metric("Jobs Found", "0", "Scrape jobs")
    col3.metric("Emails Generated", "0", "Generate now")
    col4.metric("Skills Matched", "0", "Analyze now")

elif page == "resume":
    from resume_analyzer import show_resume_analyzer

    show_resume_analyzer()

elif page == "jobs":
    from job_scraper import show_job_scraper

    show_job_scraper()

elif page == "email":
    from email_generator import show_email_generator

    show_email_generator()

elif page == "dashboard":
    from dashboard import show_dashboard

    show_dashboard()
