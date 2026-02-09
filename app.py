import streamlit as st
import requests
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="AME-ORH Táctico", layout="wide")
CLAVE_INSTITUCIONAL = "ORH2026"

# --- DOCTRINA ---
SYSTEM_PROMPT = "Actúa como Asesor AME-ORH. Prioriza PAS y MARTE (Hemorragia Masiva, Vía Aérea, Respiración, Circulación, Hipotermia). Cierre: No solo es querer salvar, sino saber salvar. ALLH-ORH:2026."

# --- FUNCIÓN EXCEL (LOS BRAZOS) ---
def registrar_en_excel(unidad, reporte, respuesta_ia):
    try:
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds_info = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open("REGISTRO_AME_ORH").sheet1
        sheet.append_row([datetime.now().strftime("%d/%m/%Y %H:%M"), unidad, reporte, respuesta_ia[:300]])
        return True
    except Exception as e:
        st.sidebar.error(f"Falla Registro: {e}")
        return False

# --- FUNCIÓN IA (EL CEREBRO) ---
def llamar_ia(texto):
    key = st.secrets.get("GROQ_API_KEY", "").strip()
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
        return f"Error IA {r.status_code}: {r.text}"
    except Exception as e:
        return f"Error Conexión: {e}"

# --- INTERFAZ ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("SISTEMA AME-ORH")
    if st.text_input("Clave", type="password") == CLAVE_INSTITUCIONAL:
        if st.button("ENTRAR"): st.session_state.auth = True; st.rerun()
    st.stop()

with st.sidebar:
    st.title("CONTROL SAR")
    u_id = st.text_input("Unidad", "SAR-01")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Unidad en línea. Indique PAS/SITREP."}]

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Mensaje..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.spinner("Procesando..."):
        res = llamar_ia(prompt)
        registrar_en_excel(u_id, prompt, res)
        
    st.session_state.messages.append({"role": "assistant", "content": res})
    with st.chat_message("assistant"): st.markdown(res)
