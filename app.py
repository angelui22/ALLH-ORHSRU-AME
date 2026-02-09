import streamlit as st
import requests
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="SISTEMA AME-ORH 2026", page_icon="🚑", layout="wide")

# --- DOCTRINA TÁCTICA ---
CLAVE_INSTITUCIONAL = "ORH2026"
SYSTEM_PROMPT = """Actúa como Asesor Experto AME-ORH. 
Tus respuestas deben ser técnicas, precisas y basadas en protocolos PAS y MARTE.
Al final de cada respuesta, incluye siempre la frase: 'No solo es querer salvar, sino saber salvar. ALLH-ORH:2026.'"""

# --- FUNCIÓN DE REGISTRO EN GOOGLE SHEETS ---
def registrar_en_excel(unidad, reporte, respuesta_ia):
    try:
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds_info = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        
        # Debe coincidir exactamente con el nombre de tu archivo
        sheet = client.open("REGISTRO_AME_ORH").sheet1
        
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        sheet.append_row([timestamp, unidad, reporte, respuesta_ia[:1000]]) # Aumentado a 1000 caracteres
        return True
    except Exception as e:
        st.sidebar.error(f"Error de Registro: {e}")
        return False

# --- FUNCIÓN DE INTELIGENCIA ARTIFICIAL (CON LIMPIEZA AGRESIVA) ---
def llamar_ia(texto_usuario):
    try:
        # 1. Extraer la llave de Secrets
        raw_key = st.secrets.get("GROQ_API_KEY", "")
        
        # 2. LIMPIEZA TÁCTICA: Elimina espacios, comillas de todo tipo y saltos de línea
        api_key = raw_key.strip().replace('"', '').replace("'", "").replace("\n", "").replace("\r", "")
        
        if not api_key:
            return "ERROR: No se encontró la GROQ_API_KEY en los Secrets de Streamlit."

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": texto_usuario}
            ],
