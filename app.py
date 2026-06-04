import streamlit as st

st.set_page_config(
    page_title="AI Career Intelligence Platform",
    page_icon="💼",
    layout="wide",
)

# ── Auth gate ────────────────────────────────────────────────────────────────
from auth import is_logged_in, show_auth_page, sign_out, get_user_email, restore_session

# Restore session from stored tokens on every page load (survives tab switches)
restore_session()

if not is_logged_in():
    show_auth_page()
    st.stop()

# ── Logged-in app ────────────────────────────────────────────────────────────

PAGES = {
    "home":      {"label": "Home",            "icon": "🏠", "description": "Overview"},
    "resume":    {"label": "Resume Analyzer", "icon": "📄", "description": "ATS scoring"},
    "jobs":      {"label": "Job Scraper",     "icon": "🔍", "description": "Live jobs"},
    "email":     {"label": "Email Generator", "icon": "✉️",  "description": "Outreach"},
    "dashboard": {"label": "Dashboard",       "icon": "📊", "description": "Market trends"},
}


def get_active_page():
    page = st.query_params.get("page", "home")
    return page if page in PAGES else "home"


def render_sidebar(active_page):
    user_email = get_user_email() or "User"
    avatar_letter = user_email[0].upper()

    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background: #0f1115;
            border-right: 1px solid rgba(255,255,255,0.08);
        }
        [data-testid="stSidebar"] > div:first-child { padding-top: 1.5rem; }

        .sidebar-brand {
            display:flex; align-items:center; gap:.8rem;
            padding:.4rem .3rem 1.4rem;
            border-bottom:1px solid rgba(255,255,255,.08);
            margin-bottom:1.2rem;
        }
        .brand-mark {
            width:52px; height:52px; display:grid; place-items:center;
            border-radius:14px;
            background:linear-gradient(135deg,#b8ff3d 0%,#65f06e 100%);
            color:#111827; font-size:1.05rem; font-weight:900;
            box-shadow:0 0 24px rgba(184,255,61,.22);
        }
        .brand-title  { color:#f9fafb; font-size:1.05rem; font-weight:800; line-height:1.05; }
        .brand-subtitle { color:#7d8793; font-size:.72rem; font-weight:700;
                          letter-spacing:.08em; text-transform:uppercase; margin-top:.12rem; }

        .nav-list { display:flex; flex-direction:column; gap:.35rem; }
        .nav-item {
            display:flex; align-items:center; gap:.8rem;
            padding:.82rem .9rem; border-radius:10px;
            color:#8b949e !important; text-decoration:none !important;
            border:1px solid transparent;
            transition:background 150ms ease, color 150ms ease, border 150ms ease;
        }
        .nav-item:hover { color:#e5e7eb !important;
            background:rgba(255,255,255,.045); border-color:rgba(255,255,255,.06); }
        .nav-item.active { color:#d7ff65 !important;
            background:rgba(184,255,61,.15); border-color:rgba(184,255,61,.12); font-weight:800; }
        .nav-icon  { width:1.35rem; text-align:center; font-size:1.05rem; }
        .nav-text  { display:flex; flex-direction:column; gap:.05rem; }
        .nav-label { font-size:.98rem; line-height:1.15; }
        .nav-description { color:#626a75; font-size:.85rem; font-weight:500; }


        /* Profile toggle button — slim secondary style */
        div[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"]:last-child .stButton button {
            background: transparent !important;
            border: none !important;
            color: #6b7280 !important;
            font-size: .75rem !important;
            padding: .1rem .5rem !important;
            min-height: unset !important;
            height: auto !important;
            margin-top: -0.5rem !important;
        }
        /* Hide profile toggle button label — only the card is visible */
        [data-testid="stSidebar"] button[kind="secondary"]:has(+ *) {
            display: none !important;
        }
        div[data-testid="stSidebar"] .stButton:nth-of-type(1) button {
            opacity: 0 !important;
            height: 0 !important;
            padding: 0 !important;
            min-height: 0 !important;
            margin: 0 !important;
            overflow: hidden;
        }

        /* Profile button at bottom of sidebar */
        .profile-btn {
            display:flex; align-items:center; gap:.75rem;
            padding:.75rem .9rem;
            border-radius:10px;
            background:rgba(255,255,255,.04);
            border:1px solid rgba(255,255,255,.08);
            cursor:pointer;
            margin-top:.5rem;
            transition:background 150ms;
        }
        .profile-btn:hover { background:rgba(255,255,255,.08); }
        .user-avatar {
            width:34px; height:34px; border-radius:50%;
            background:linear-gradient(135deg,#7c3aed,#a855f7);
            display:grid; place-items:center;
            color:#fff; font-weight:700; font-size:.9rem; flex-shrink:0;
        }
        .user-email { color:#9ca3af; font-size:.75rem;
                      overflow:hidden; text-overflow:ellipsis; white-space:nowrap; max-width:160px;}
        .user-label { color:#e5e7eb; font-size:.82rem; font-weight:600; line-height:1.2; }
    </style>

    <script>
    (function(){
        function closeSidebarOnMobile(){
            if(window.innerWidth>768) return;
            var btns=window.parent.document.querySelectorAll(
                'section[data-testid="stSidebar"] button');
            if(btns.length) btns[0].click();
        }
        function attach(){
            document.querySelectorAll('.nav-item').forEach(function(el){
                el.addEventListener('click',function(){setTimeout(closeSidebarOnMobile,80);});
            });
        }
        if(document.readyState==='complete') attach();
        else window.addEventListener('load', attach);
    })();
    </script>
    """, unsafe_allow_html=True)

    nav_links = []
    for slug, item in PAGES.items():
        active_class = " active" if slug == active_page else ""
        nav_links.append(
            f'<a class="nav-item{active_class}" href="?page={slug}" target="_self" '
            f'onclick="if(window.innerWidth<=768){{setTimeout(function(){{'
            f'var b=window.parent.document.querySelectorAll(\'section[data-testid=\\"stSidebar\\"] button\');'
            f'if(b.length)b[0].click();}},80)}}">'
            f'<span class="nav-icon">{item["icon"]}</span>'
            f'<span class="nav-text">'
            f'<span class="nav-label">{item["label"]}</span>'
            f'<span class="nav-description">{item["description"]}</span>'
            f'</span></a>'
        )

    st.sidebar.markdown(
        f'<div class="sidebar-brand">'
        f'<div class="brand-mark">AI</div>'
        f'<div><div class="brand-title">AI Career</div>'
        f'<div class="brand-subtitle">Platform</div></div></div>'
        f'<div class="nav-list">{"".join(nav_links)}</div>',
        unsafe_allow_html=True,
    )

    st.sidebar.markdown("<div style='height:80px'></div>", unsafe_allow_html=True)

    # User card + sign-out at the bottom
    st.sidebar.markdown(
        f'<div class="user-card">'
        f'<div class="user-avatar">{avatar_letter}</div>'
        f'<div style="min-width:0;flex:1;">'
        f'<div class="user-label">Signed in</div>'
        f'<div class="user-email">{user_email}</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )
    if st.sidebar.button("🚪 Sign Out", use_container_width=True):
        sign_out()
        st.rerun()


# ── Render ───────────────────────────────────────────────────────────────────
page = get_active_page()
render_sidebar(page)

if page == "home":
    from db import get_user_stats, get_latest_resume_score, get_recent_activity
    from auth import get_user_email

    email      = get_user_email() or "there"
    first_name = email.split("@")[0].capitalize()
    stats      = get_user_stats()
    latest_score = get_latest_resume_score()
    recent       = get_recent_activity(8)

    st.title("💼 AI Career Intelligence Platform")
    st.markdown(f"### Welcome back, **{first_name}**! 👋")
    st.markdown("Your personal AI-powered career assistant — here's your activity at a glance.")
    st.markdown("---")

    # ── Stats cards ──────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    resume_score_display = f"{latest_score}%" if latest_score else "—"
    c1.metric("📄 Best ATS Score",    resume_score_display,
              "View analysis" if latest_score else "Upload resume")
    c2.metric("🔍 Jobs Searched",     stats.get("job_searched", 0),
              "Find more jobs" if stats.get("job_searched", 0) else "Scrape jobs")
    c3.metric("✉️ Emails Generated",  stats.get("email_generated", 0),
              "Generate now")
    c4.metric("🛠️ Skills Analyzed",   stats.get("skill_analyzed", 0),
              "Analyze now")

    st.markdown("---")

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("🚀 Quick Actions")
        st.markdown("""
- 📄 **[Resume Analyzer](?page=resume)** — Upload your resume and get an ATS score
- 🔍 **[Job Scraper](?page=jobs)** — Find live Indian job listings
- ✉️ **[Email Generator](?page=email)** — Write cold emails to recruiters
- 📊 **[Dashboard](?page=dashboard)** — Explore job market trends
        """)

    with col_right:
        st.subheader("🕐 Recent Activity")
        if recent:
            activity_icons = {
                "resume_analyzed": "📄",
                "job_searched":    "🔍",
                "email_generated": "✉️",
                "skill_analyzed":  "🛠️",
            }
            activity_labels = {
                "resume_analyzed": "Analyzed resume",
                "job_searched":    "Searched jobs",
                "email_generated": "Generated email",
                "skill_analyzed":  "Analyzed skills",
            }
            for row in recent:
                atype = row.get("activity_type", "")
                icon  = activity_icons.get(atype, "⚡")
                label = activity_labels.get(atype, atype.replace("_", " ").title())
                meta  = row.get("metadata", {}) or {}
                ts    = (row.get("created_at") or "")[:10]

                detail = ""
                if atype == "resume_analyzed" and meta.get("score"):
                    detail = f' — Score: **{meta["score"]}**'
                elif atype == "job_searched" and meta.get("job_title"):
                    detail = f' — {meta["job_title"]}'
                elif atype == "email_generated" and meta.get("email_type"):
                    detail = f' — {meta["email_type"]}'
                elif atype == "skill_analyzed" and meta.get("role"):
                    detail = f' — {meta["role"]}'

                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:8px;'
                    f'padding:8px 12px;background:#1e1e2e;border-radius:8px;margin-bottom:6px;">'
                    f'<span style="font-size:1.1rem">{icon}</span>'
                    f'<span style="flex:1;font-size:.88rem;color:#e5e7eb;">{label}{detail}</span>'
                    f'<span style="font-size:.75rem;color:#6b7280;">{ts}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )
        else:
            st.info("No activity yet — start by analyzing your resume!")

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