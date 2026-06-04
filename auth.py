import streamlit as st
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")


@st.cache_resource
def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def is_logged_in() -> bool:
    return st.session_state.get("user") is not None


def get_user():
    return st.session_state.get("user")


def get_user_id():
    user = get_user()
    return user["id"] if user else None


def get_user_email():
    user = get_user()
    return user["email"] if user else None


def sign_up(email: str, password: str):
    return get_supabase().auth.sign_up({"email": email, "password": password})


def sign_in(email: str, password: str):
    return get_supabase().auth.sign_in_with_password({"email": email, "password": password})


def sign_out():
    try:
        get_supabase().auth.sign_out()
    except Exception:
        pass
    for key in ["user", "access_token", "refresh_token"]:
        st.session_state.pop(key, None)


def restore_session():
    """
    Try to restore session from stored tokens on every page load.
    Called at the very top of app.py before the auth gate.
    Prevents logout on tab switch / query param navigation.
    """
    if is_logged_in():
        return  # Already loaded this run

    access_token  = st.session_state.get("access_token")
    refresh_token = st.session_state.get("refresh_token")

    if not access_token or not refresh_token:
        return

    try:
        sb  = get_supabase()
        res = sb.auth.set_session(access_token, refresh_token)
        if res and res.user:
            st.session_state["user"] = {
                "id":    res.user.id,
                "email": res.user.email,
            }
            # Rotate tokens if refreshed
            if res.session:
                st.session_state["access_token"]  = res.session.access_token
                st.session_state["refresh_token"]  = res.session.refresh_token
    except Exception:
        # Tokens expired or invalid — clear them so user sees login page
        for key in ["access_token", "refresh_token", "user"]:
            st.session_state.pop(key, None)


def show_auth_page():
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none !important; }
        .main .block-container { max-width: 100% !important; padding: 0 !important; }
    </style>
    """, unsafe_allow_html=True)

    if "auth_tab" not in st.session_state:
        st.session_state["auth_tab"] = "signin"
    if "prefill_email" not in st.session_state:
        st.session_state["prefill_email"] = ""

    _, mid, _ = st.columns([1, 1.6, 1])

    with mid:
        st.markdown("""
        <div style="text-align:center; margin-top:6vh; margin-bottom:1.4rem;">
          <div style="display:inline-flex;width:52px;height:52px;border-radius:13px;
               background:linear-gradient(135deg,#b8ff3d,#65f06e);align-items:center;
               justify-content:center;font-weight:900;font-size:1.1rem;color:#111;
               box-shadow:0 0 20px rgba(184,255,61,.25);margin-bottom:.7rem;">AI</div>
          <div style="font-size:1.35rem;font-weight:800;color:#f9fafb;">AI Career Platform</div>
          <div style="color:#6b7280;font-size:.82rem;margin-top:.2rem;">
              Your personalized AI-powered career assistant
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── SIGN IN ──────────────────────────────────────────────────────────
        if st.session_state["auth_tab"] == "signin":

            if st.session_state.get("signup_success"):
                st.success("✅ Account created! Sign in to continue.")
                st.session_state["signup_success"] = False

            st.markdown("#### 🔑 Sign In")

            with st.form("login_form"):
                email = st.text_input(
                    "Email",
                    value=st.session_state.get("prefill_email", ""),
                    placeholder="you@example.com"
                )
                password = st.text_input("Password", placeholder="Your password", type="password")
                submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")

            if submitted:
                if not email or not password:
                    st.error("Please fill in all fields.")
                else:
                    with st.spinner("Signing in..."):
                        try:
                            res = sign_in(email, password)
                            if res.user:
                                st.session_state["user"] = {
                                    "id":    res.user.id,
                                    "email": res.user.email,
                                }
                                # Store BOTH tokens so session survives navigation
                                st.session_state["access_token"]  = res.session.access_token
                                st.session_state["refresh_token"]  = res.session.refresh_token
                                st.session_state["prefill_email"] = ""
                                st.rerun()
                            else:
                                st.error("Invalid email or password.")
                        except Exception as e:
                            st.error(f"Sign-in failed: {e}")

            st.markdown("<div style='height:.8rem'></div>", unsafe_allow_html=True)
            if st.button("Don't have an account? Create one →", use_container_width=True):
                st.session_state["auth_tab"] = "signup"
                st.rerun()

        # ── SIGN UP ──────────────────────────────────────────────────────────
        else:
            st.markdown("#### ✨ Create Account")

            with st.form("signup_form"):
                new_email    = st.text_input("Email",            placeholder="you@example.com")
                new_password = st.text_input("Password",         placeholder="Min 6 characters", type="password")
                confirm_pass = st.text_input("Confirm Password", placeholder="Repeat password",  type="password")
                submitted2 = st.form_submit_button("Create Account", use_container_width=True, type="primary")

            if submitted2:
                if not new_email or not new_password:
                    st.error("Please fill in all fields.")
                elif new_password != confirm_pass:
                    st.error("Passwords do not match.")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    with st.spinner("Creating your account..."):
                        try:
                            res = sign_up(new_email, new_password)
                            if res.user:
                                st.session_state["auth_tab"]       = "signin"
                                st.session_state["prefill_email"]  = new_email
                                st.session_state["signup_success"] = True
                                st.rerun()
                            else:
                                st.error("Sign-up failed. Try a different email.")
                        except Exception as e:
                            st.error(f"Sign-up failed: {e}")

            st.markdown("<div style='height:.8rem'></div>", unsafe_allow_html=True)
            if st.button("Already have an account? Sign In →", use_container_width=True):
                st.session_state["auth_tab"] = "signin"
                st.rerun()