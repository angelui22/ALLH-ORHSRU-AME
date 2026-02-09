import streamlit as st
import requests
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.set_page_config(page_title="AME-ORH Táctico", layout="wide")

# --- DOCTRINA ---
SYSTEM_PROMPT = "Actúa como Asesor AME-ORH. Prioriza PAS y MARTE. Cierre: No solo es querer salvar, sino saber salvar. ALLH-ORH:2026."

# --- FUNCIÓN EXCEL (MODO SILENCIOSO) ---
def registrar_en_excel(unidad, reporte, respuesta_ia):
    try:
        # Cargamos todo el bloque gcp_service_account como un solo diccionario
        info = dict(st.secrets["gcp_service_account"])
        # Limpiamos posibles errores de saltos de línea manuales
        info["private_key"] = info["private_key"].replace("\\n", "\n")
        
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_info(info, scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open("REGISTRO_AME_ORH").sheet1
        sheet.append_row([datetime.now().strftime("%d/%m/%Y %H:%M"), unidad, reporte, respuesta_ia[:300]])
    except Exception as e:
        # Solo avisamos en el lateral si falla, pero no detenemos la IA
        st.sidebar.warning(f"Registro en espera: {str(e)[:50]}...")

# --- FUNCIÓN IA (FORZADA) ---
def llamar_ia(texto):
    # .strip() es vital para quitar espacios invisibles que causan el 401
    raw_key = st.secrets.get("GROQ_API_KEY", "")
    key = raw_key.strip().strip('"').strip("'")
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": texto}]
    }
    try:
        r = requests.post(url, json=payload, timeout=15)
        if r.status_code == 200:
            return r.json()['choices'][0]['message']['content']
        return f"Error de IA ({r.status_code}): {r.text}"
    except Exception as e:
        return f"Falla de enlace: {e}"

# --- INTERFAZ ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("SISTEMA AME-ORH")
    if st.text_input("Clave Táctica", type="password") == "ORH2026":
        if st.button("ACCEDER"): st.session_state.auth = True; st.rerun()
    st.stop()

with st.sidebar:
    st.title("CONTROL SAR")
    u_id = st.text_input("Unidad", "SAR-01")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Unidad activa. Indique SITREP."}]

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Escriba su SITREP aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.spinner("Sincronizando..."):
        res = llamar_ia(prompt)
        registrar_en_excel(u_id, prompt, res)
        
    st.session_state.messages.append({"role": "assistant", "content": res})
    with st.chat_message("assistant"): st.markdown(res)
