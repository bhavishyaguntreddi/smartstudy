# accessibility.py - sidebar settings used by every page:
# high contrast, large text, plain English, plus a read-aloud button. Nothing here is stored.
import json
import streamlit as st
import streamlit.components.v1 as components

HIGH_CONTRAST_CSS = """
.stApp, [data-testid="stSidebar"], [data-testid="stHeader"] { background: #000 !important; }
.stApp *, [data-testid="stSidebar"] * { color: #fff !important; }
.stApp a { color: #ffff00 !important; text-decoration: underline !important; }
.stApp button, .stApp input, .stApp textarea, .stApp [data-baseweb="select"] > div {
    background: #000 !important; border: 2px solid #fff !important; }
[data-testid="stAlert"], [data-testid="stExpander"], [data-testid="stForm"] {
    background: #000 !important; border: 2px solid #fff !important; }
[data-testid="stTable"] th, [data-testid="stTable"] td {
    background: #000 !important; border: 1px solid #fff !important; }
*:focus-visible { outline: 4px solid #ffff00 !important; outline-offset: 2px !important; }
[data-testid="stAlert"], [data-testid="stAlert"] *,
[data-testid="stAlertContainer"], [data-testid="stAlertContainer"] * {
    background: #000 !important; background-color: #000 !important; color: #fff !important; }
[data-testid="stAlert"], [data-testid="stAlertContainer"] {
    border: 3px solid #fff !important; border-radius: 6px !important; }
[data-testid="stException"], [data-testid="stException"] * {
    background: #000 !important; background-color: #000 !important; color: #fff !important; }
[data-testid="stException"] { border: 3px solid #fff !important; }
"""
LARGE_TEXT_CSS = "html { font-size: 125% !important; }"   # scales text that uses rem units

def apply_settings():
    """Show the Settings controls, apply the look, and return the choices."""
    st.sidebar.header("Settings")
    # value=... remembers the choice when moving between pages
    contrast = st.sidebar.checkbox("High contrast", value=st.session_state.get("s_contrast", False))
    large = st.sidebar.checkbox("Large text", value=st.session_state.get("s_large", False))
    plain = st.sidebar.checkbox("Plain English", value=st.session_state.get("s_plain", False))
    st.session_state.s_contrast, st.session_state.s_large, st.session_state.s_plain = contrast, large, plain
    st.sidebar.caption("These settings apply to this browser tab only. Nothing is stored.")

    css = (HIGH_CONTRAST_CSS if contrast else "") + (LARGE_TEXT_CSS if large else "")
    if css:   # our own fixed text only, no user input, so this is safe
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    return {"contrast": contrast, "large": large, "plain": plain}

def read_aloud(text, label="Read aloud", contrast=False):
    """A Read aloud button + Stop button, using the browser's own speech. Text stays on screen too."""
    clean = text.replace("**", "")                                  # don't read out markdown stars
    safe = json.dumps(clean).replace("</", "<\\/")                  # safe to put inside a script
    bg, fg, border = ("#000", "#fff", "#fff") if contrast else ("#fff", "#262730", "#999")
    style = (f"padding:8px 14px;font-size:16px;cursor:pointer;background:{bg};color:{fg};"
             f"border:2px solid {border};border-radius:6px;margin-right:8px")
    html = """
    <div style="font-family:sans-serif">
      <button id="say" style="__STYLE__">__LABEL__</button>
      <button id="stop" style="__STYLE__">Stop</button>
      <span id="msg" role="status" style="color:__FG__"></span>
    </div>
    <script>
      const text = __TEXT__;
      const say = document.getElementById('say'), stop = document.getElementById('stop');
      const msg = document.getElementById('msg');
      if (!('speechSynthesis' in window)) {
        say.disabled = true; stop.disabled = true;
        msg.textContent = 'Read aloud is not available in this browser. The text is shown on the page.';
      }
      say.onclick = () => {
        window.speechSynthesis.cancel();
        const u = new SpeechSynthesisUtterance(text);
        u.lang = 'en-GB';
        u.onend = () => { msg.textContent = ''; };
        msg.textContent = 'Reading aloud...';
        window.speechSynthesis.speak(u);
      };
      stop.onclick = () => { window.speechSynthesis.cancel(); msg.textContent = 'Stopped.'; };
    </script>"""
    html = (html.replace("__STYLE__", style).replace("__LABEL__", label)
                .replace("__FG__", fg).replace("__TEXT__", safe))
    components.html(html, height=60)