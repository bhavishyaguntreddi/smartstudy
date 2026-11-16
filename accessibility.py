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