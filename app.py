import streamlit as st
import requests
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="SISTEMA AME-ORH 2026", layout="wide")

# --- DOCTRINA TÁCTICA ---
CLAVE_INSTITUCIONAL = "ORH2026"
SYSTEM_PROMPT = """Actúa como Asesor Experto AME-ORH. 
Tus respuestas deben ser técnicas, precisas y basadas en protocolos PAS y MARTE.
Al final de cada respuesta, incluye siempre la frase: 'No solo es querer salvar, sino saber salvar. ALLH-ORH:2026.'"""

# --- CONEXIÓN A EXCEL (REGISTRO TÁCTICO) ---
def registrar_en_excel(unidad, reporte, respuesta_ia):
    try:
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        # Cargar credenciales desde secrets
        creds_info = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        
        # Abre la hoja por nombre
        sheet = client.open("REGISTRO_AME_ORH").sheet1
        
        # Prepara la fila
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        sheet.append_row([timestamp, unidad, reporte, respuesta_ia[:500]])
        return True
    except Exception as e:
        # No bloqueamos la app si falla el Excel, solo avisamos en el lateral
        st.sidebar.warning(f"Aviso: Error de registro en Excel (Posible API bloqueada)")
        return False

# --- MOTOR DE INTELIGENCIA (GROQ) ---
def llamar_ia(texto_usuario):
    # Extraer y limpiar llave
    api_key = st.secrets.get("GROQ_API_KEY", "").strip().replace('"', '')
    
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
        "temperature": 0.7
    }

    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        elif response.status_code == 401:
            return "ERROR 401: La API Key de Groq es inválida o ha expirado."
        else:
            return f"Error del Servidor ({response.status_code}): {response.text}"
    except Exception as e:
        return f"Error de conexión: {str(e)}"

# --- INTERFAZ DE USUARIO ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🛡️ ACCESO SISTEMA AME-ORH")
    password = st.text_input("Ingrese Clave de Unidad:", type="password")
    if st.button("DESBLOQUEAR"):
        if password == CLAVE_INSTITUCIONAL:
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Clave incorrecta. Acceso denegado.")
    st.stop()

# --- PANEL PRINCIPAL ---
st.title("🚑 ASESORÍA TÁCTICA AME-ORH")

with st.sidebar:
    st.header("CONFIGURACIÓN")
    unidad = st.text_input("Identificación de Unidad:", value="SAR-ALPHA")
    if st.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

# Historial de Chat
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Entrada de usuario
if prompt := st.chat_input("Describa la situación o SITREP..."):
    # Mostrar mensaje del usuario
    st.session_state.mensajes.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generar respuesta
    with st.spinner("IA procesando protocolos..."):
        respuesta = llamar_ia(prompt)
        # Intentar registro en Excel de fondo
        registrar_en_excel(unidad, prompt, respuesta)

    # Mostrar respuesta de IA
    st.session_state.mensajes.append({"role": "assistant", "content": respuesta})
    with st.chat_message("assistant"):
        st.markdown(respuesta)
