import streamlit as st
import pandas as pd
import json
import io
import urllib.parse
import re
from google import genai
from google.genai import types
from fpdf import FPDF
from pypdf import PdfReader

# --- INTENTAR IMPORTAR OPENAI DE FORMA SEGURA ---
try:
    import openai
    from openai import OpenAI
except ImportError:
    pass

# --- CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(page_title="Range of Solutions - Cotizador Pro", layout="centered", initial_sidebar_state="collapsed")

# Inicialización segura de Clientes (Gemini y OpenAI)
client_gemini = None
client_openai = None

if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"].strip():
    try:
        client_gemini = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    except Exception:
        pass

if "OPENAI_API_KEY" in st.secrets and st.secrets["OPENAI_API_KEY"].strip():
    try:
        client_openai = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    except Exception:
        pass

# Encabezado visual de la aplicación
col1, col2, col3 = st.columns(3)
with col2:
    try:
        st.image("LOGO PNG2.png", use_container_width=True)
    except Exception:
        st.markdown("<h3 style='text-align: center; color: #f39c12; margin-bottom:0;'>⚡ RANGE OF SOLUTIONS S.A.S. ⚡</h3>", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #f39c12; font-size: 24px; margin-top: 0px;'>☀️ COTIZADOR SOLAR FV INTELIGENTE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #7f8c8d; font-size: 14px;'>Ingeniería Avanzada con Arquitectura de IA Híbrida y Fallback Seguro</p>", unsafe_allow_html=True)

# --- MÓDULO 1: CAPTURA DE DATOS CON BLINDAJE MULTI-IA ---
st.header("1. Entrada de Datos de Consumo")
metodo = st.selectbox("Método de captura de datos:", ["📸 Analizar Recibo (PDF o Imagen) con IA", "⌨️ Registro Manual"])

# Variables de respaldo base (Santa Marta)
consumo_kwh = 246.69
tarifa_kwh = 920.32
lectura_exitosa = False
metodo_usado = ""

if metodo == "📸 Analizar Recibo (PDF o Imagen) con IA":
    archivo = st.file_uploader("Sube el recibo original (Air-e / Afinia)", type=['pdf', 'jpg', 'png', 'jpeg'])
    
    if archivo:
        with st.spinner("🤖 Procesando documento con motor de Inteligencia Artificial..."):
            texto_recibo = ""
            is_pdf = archivo.name.lower().endswith('.pdf')
            
            if is_pdf:
                try:
                    reader = PdfReader(archivo)
                    for page in reader.pages:
                        text = page.extract_text()
                        if text:
                            texto_recibo += text + "\n"
                except Exception as e:
                    st.error(f"Error al leer el archivo PDF: {e}")

            # --- ESTRATEGIA 1: PROCESAR CON OPENAI ---
            if client_openai and not lectura_exitosa:
                try:
                    if is_pdf and texto_recibo.strip():
                        prompt_sistema = (
                            "Eres un experto analista de facturas de energía eléctrica de Colombia. "
                            "Tu tarea es extraer el consumo del último mes en kWh y la tarifa por kWh en pesos ($/kWh). "
                            "Responde únicamente un objeto JSON válido con las llaves exactas: 'consumo' y 'tarifa'. "
                            "No incluyas texto aclaratorio ni marcas de bloques de código markdown."
                        )
                        response = client_openai.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": prompt_sistema},
                                {"role": "user", "content": f"Texto extraído del recibo:\n{texto_recibo}"}
                            ],
                            response_format={"type": "json_object"}
                        )
                        datos = json.loads(response.choices.message.content)
                        consumo_kwh = float(datos.get("consumo", 246.69))
                        tarifa_kwh = float(datos.get("tarifa", 920.32))
                        lectura_exitosa = True
                        metodo_usado = "OpenAI (GPT-4o-mini)"
                except Exception:
                    pass

            # --- ESTRATEGIA 2: FALLBACK CON GEMINI ---
            if client_gemini and not lectura_exitosa:
                for modelo in ['gemini-1.5-flash', 'gemini-2.5-flash']:
                    try:
                        if is_pdf and texto_recibo.strip():
                            prompt_ia = (
                                "Analiza el texto de un recibo de energía en Colombia. Extrae el consumo del último mes en kWh "
                                "y la tarifa por kWh en pesos. Devuelve ESTRICTAMENTE un JSON con las llaves exactas 'consumo' y 'tarifa'. "
                                f"Texto:\n{texto_recibo}"
                            )
                            response = client_gemini.models.generate_content(
                                model=modelo,
                                contents=prompt_ia,
                                config=types.GenerateContentConfig(response_mime_type="application/json"),
                            )
                        elif not is_pdf:
                            archivo.seek(0)
                            file_bytes = archivo.read()
                            prompt_ia = (
                                "Analiza la imagen de este recibo de energía de Colombia. Extrae el consumo del último mes en kWh "
                                "y la tarifa por kWh en pesos. Devuelve un JSON con las llaves exactas: 'consumo' y 'tarifa'."
                            )
                            response = client_gemini.models.generate_content(
                                model=modelo,
                                contents=[
                                    types.Part.from_bytes(data=file_bytes, mime_type="image/jpeg"),
                                    prompt_ia
                                ],
                                config=types.GenerateContentConfig(response_mime_type="application/json"),
                            )
                        
                        datos = json.loads(response.text)
                        consumo_kwh = float(datos.get("consumo", 246.69))
                        tarifa_kwh = float(datos.get("tarifa", 920.32))
                        lectura_exitosa = True
                        metodo_usado = f"Google Gemini ({modelo})"
                        break
                    except Exception:
                        continue

            # --- ESTRATEGIA 3: EXPRESIONES REGULARES ---
            if not lectura_exitosa and texto_recibo.strip():
                try:
                    match_consumo = re.search(r'(?:consumo|activo|mes|facturado)[\s\D]*(\d+[\.,]\d+|\d+)\s*(?:kwh)', texto_recibo, re.IGNORECASE)
                    match_tarifa = re.search(r'(?:tarifa|precio|costo|cuv|$/kwh)[\s\D]*(\d+[\.,]\d+|\d+)', texto_recibo, re.IGNORECASE)
                    
                    if match_consumo:
                        consumo_kwh = float(match_consumo.group(1).replace(',', '.'))
                    if match_tarifa:
                        tarifa_kwh = float(match_tarifa.group(1).replace(',', '.'))
                    
                    lectura_exitosa = True
                    metodo_usado = "Extracción Algorítmica Local (Regex)"
                except Exception:
                    pass

            if lectura_exitosa:
                st.success(f"✅ Documento analizado con éxito vía {metodo_usado}: {consumo_kwh:,.2f} kWh/mes a ${tarifa_kwh:,.2f}/kWh")
            else:
                st.warning("⚠️ Los servicios de IA no pudieron extraer los datos. Se cargaron los valores base editables.")

    with st.expander("✏️ Verificar y Ajustar Valores Extraídos", expanded=True):
        c1, c2 = st.columns(2)
        consumo_kwh = c1.number_input("Consumo Final Evaluado (kWh/mes)", min_value=0.0, step=10.0, value=consumo_kwh)
        tarifa_kwh = c2.number_input("Tarifa Final Evaluada ($/kWh)", min_value=0.0, step=1.0, value=tarifa_kwh)

else:
    c1, c2 = st.columns(2)
    consumo_kwh = c1.number_input("Consumo Mensual (kWh/mes)", min_value=0.0, step=10.0, value=246.69)
    tarifa_kwh = c2.number_input("Tarifa del Servicio ($/kWh)", min_value=0.0, step=1.0, value=920.32)


# --- MÓDULO 2: APU Y COSTOS DE INGENIERÍA ---
st.header("2. Ingeniería Económica y Costos Base")
with st.expander("🛠️ Desglose del APU de Materiales y Mano de Obra (Modificable)"):
    costo_generacion = st.number_input("Equipos (Paneles Tier 1 + Inversores)", value=15403044.8, step=50000.0)
    costo_estructura = st.number_input("Estructura de Aluminio Al6005-T5 y Anclajes", value=1460845.0, step=10000.0)
    costo_electricos = st.number_input("Protecciones AC/DC y Cableado Solar", value=7443247.0, step=20000.0)
    costo_instalacion = st.number_input("Mano de Obra Certificada, Trámites y Diseños", value=3840000.0, step=50000.0)
    viaticos = st.number_input("Logística, Viáticos y Traslados", value=0, step=10000)

costo_base_total = costo_generacion + costo_estructura + costo_electricos + costo_instalacion + viaticos

# --- MÓDULO 3: MARGENES COMERCIALES ---
st.header("3. Estructuración Comercial")
margen = st.slider("Margen de Utilidad Deseado para Range S.A.S. (%)", 5, 50, 25)

precio_venta_neto = costo_base_total / (1 - (margen / 100))
utilidad_bruta = precio_venta_neto - costo_base_total

porcentaje_servicio = costo_instalacion / costo_base_total
precio_venta_servicio = precio_venta_neto * porcentaje_servicio
iva_ingenieria = precio_venta_servicio * 0.19
precio_final_cliente = precio_venta_neto + iva_ingenieria

col_m1, col_m2 = st.columns(2)
col_m1.metric("Margen Bruto Obtenido", f"$ {utilidad_bruta:,.0f}")
