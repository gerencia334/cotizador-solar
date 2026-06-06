import streamlit as st
import pandas as pd
import json
import io
import urllib.parse
from google import genai
from google.genai import types
from fpdf import FPDF
from pypdf import PdfReader

# --- CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(page_title="Range of Solutions - Cotizador Pro Gemini", layout="centered", initial_sidebar_state="collapsed")

# Inicialización del nuevo cliente nativo de Google GenAI
try:
    client_gemini = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    client_gemini = None

# Configuración de las columnas principales
col1, col2, col3 = st.columns()
with col2:
    try:
        st.image("LOGO PNG2.png", use_container_width=True)
    except:
        st.markdown("<h3 style='text-align: center; color: #f39c12; margin-bottom:0;'>⚡ RANGE OF SOLUTIONS S.A.S. ⚡</h3>", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #f39c12; font-size: 24px; margin-top: 0px;'>☀️ COTIZADOR SOLAR FV INTELIGENTE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #7f8c8d; font-size: 14px;'>Ingeniería Avanzada y Lectura Nativa de PDF con Google Gemini</p>", unsafe_allow_html=True)

# --- MÓDULO 1: CAPTURA DE DATOS (LECTURA INTELIGENTE O MANUAL) ---
st.header("1. Entrada de Datos de Consumo")
metodo = st.selectbox("Método de captura de datos:", ["📸 Analizar Recibo (PDF o Imagen) con IA", "⌨️ Registro Manual"])

# Variables globales con valores de respaldo reales extraídos de tu recibo de Air-e
consumo_kwh = 246.69
tarifa_kwh = 920.32

if metodo == "📸 Analizar Recibo (PDF o Imagen) con IA":
    archivo = st.file_uploader("Sube el recibo original (Air-e / Afinia)", type=['pdf', 'jpg', 'png', 'jpeg'])
    
    if archivo:
        if client_gemini is None:
            st.warning("⚠️ Modo demostración activo (GEMINI_API_KEY no detectada). Cargando datos de prueba.")
            consumo_kwh = 246.69
            tarifa_kwh = 920.32
        else:
            with st.spinner("🤖 Analizando la estructura del documento de forma segura... Por favor espera."):
                try:
                    if archivo.name.lower().endswith('.pdf'):
                        reader = PdfReader(archivo)
                        texto_recibo = ""
                        for page in reader.pages:
                            texto_recibo += page.extract_text() + "\n"
                        
                        prompt_ia = (
                            "Analiza el siguiente texto extraído de un recibo de energía de la empresa Air-e o Afinia in Colombia. "
                            "Identifica y extrae exactamente los siguientes dos valores numéricos: "
                            "1. El consumo de energía activa del último mes en kWh. "
                            "2. El valor o costo cobrada por cada kWh ($/kWh). "
                            "Devuelve estrictamente un objeto JSON válido con las llaves exactas: 'consumo' y 'tarifa'. "
                            "No agregues texto explicativo, notas ni bloques de código markdown.\n\n"
                            f"Texto del recibo:\n{texto_recibo}"
                        )
                        
                        response = client_gemini.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=prompt_ia,
                            config=types.GenerateContentConfig(
                                response_mime_type="application/json",
                            ),
                        )
                    else:
                        file_bytes = archivo.read()
                        prompt_ia = (
                            "Analiza la imagen de este recibo de energía de Colombia. Extrae el consumo del último mes en kWh "
                            "y la tarifa por kWh en pesos. Devuelve un JSON con las llaves exactas: 'consumo' y 'tarifa'."
                        )
                        response = client_gemini.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=[
                                types.Part.from_bytes(data=file_bytes, mime_type="image/jpeg"),
                                prompt_ia
                            ],
                            config=types.GenerateContentConfig(
                                response_mime_type="application/json",
                            ),
                        )
                    
                    datos = json.loads(response.text)
                    consumo_kwh = float(datos.get("consumo", 246.69))
                    tarifa_kwh = float(datos.get("tarifa", 920.32))
                    st.success(f"✅ Documento analizado con éxito por la IA: {consumo_kwh:,.2f} kWh/mes a ${tarifa_kwh:,.2f}/kWh")
                    
                except Exception as e:
                    st.error(f"Error en la lectura del documento: {e}. Se cargaron los datos de respaldo automáticos.")
                    consumo_kwh = 246.69
                    tarifa_kwh = 920.32
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
col_m2.metric("Precio de Venta (Con IVA)", f"$ {precio_final_cliente:,.0f}")

# --- MÓDULO 4: ENTORNO FINANCIERO DIDÁCTICO E INTERACTIVO (ROI) ---
st.header("4. Análisis de Recuperación de Inversión")

inflacion_energia = 0.06      
degradacion_paneles = 0.005   
eficiencia_sistema = 0.90     

ahorro_mes_inicial = consumo_kwh * tarifa_kwh * eficiencia_sistema

años = list(range(1, 26))
ahorros_anuales = []
flujo_caja_acumulado = []

beneficio_fiscal_ley1715 = precio_final_cliente * 0.33
saldo_acumulado = -precio_final_cliente + beneficio_fiscal_ley1715

for a in años:
    ahorro_año = (ahorro_mes_inicial * 12) * ((1 + inflacion_energia) ** (a - 1)) * ((1 - degradacion_paneles) ** (a - 1))
    ahorros_anuales.append(ahorro_año)
    saldo_acumulado += ahorro_año
    flujo_caja_acumulado.append(saldo_acumulado)

payback_exacto = 0.0
for idx, saldo in enumerate(flujo_caja_acumulado):
    if saldo >= 0:
        if idx == 0:
            payback_exacto = (precio_final_cliente - beneficio_fiscal_ley1715) / ahorros_anuales
        else:
            prev_saldo = flujo_caja_acumulado[idx-1]
            payback_exacto = idx + (abs(prev_saldo) / ahorros_anuales[idx])
        break
if payback_exacto == 0.0:
    payback_exacto = (precio_final_cliente - beneficio_fiscal_ley1715) / (ahorro_mes_inicial * 12)

tab1, tab2 = st.tabs(["💡 Para Todo Público (Didáctico)", "📊 Para Expertos (Matriz Técnica)"])

with tab1:
    st.success(f"⏱️ **¡Tu sistema se paga solo en {payback_exacto:.1f} años!** Posterior a esto, disfrutas de energía solar completamente gratuita.")
    col_v1, col_v2 = st.columns(2)
    col_v1.metric("Tu Ahorro Estimado Año 1", f"$ {ahorros_anuales:,.0f}")
    col_v2.metric("Alivio Tributario (Ley 1715)", f"$ {beneficio_fiscal_ley1715:,.0f}")
    
    st.markdown(f"""
    ### ¿Por qué dar el paso con Range of Solutions?
    * **Freno inmediato a los abusos tarifarios**: Reduces el **{eficiencia_sistema*100:.0f}%** de la energía que le compras a operadores como Air-e o Afinia de forma garantizada.
    * **Beneficios tributarios de Ley 1715**: El estado colombiano te premia permitiéndote deducir el **33% de la inversión** directamente de tu impuesto de renta.
    * **Sostenibilidad ambiental**: Dejas de emitir aproximadamente **{(consumo_kwh * 12 * eficiencia_sistema * 0.4) / 1000:.1f} toneladas de CO2 al año**, lo que equivale al impacto positivo de sembrar **{int(consumo_kwh * 0.12)} árboles maduros**.
    """)

with tab2:
    st.caption("Evolución Detallada del Flujo de Caja Descontado y Pérdida de Eficiencia Mínima")
    
    # MODIFICACIÓN DE FUERZA BRUTA: Cambiamos la variable a listas independientes
    # para que la caché de Streamlit Cloud se limpie obligatoriamente y no busque más la línea vieja
    columnas_tabla = ["Año", "Ahorro del Periodo ($)", "Flujo Acumulado ($)"]
    valores_tabla = [list(años), list(ahorros_anuales), list(flujo_caja_acumulado)]
    
    tabla_final_pro = pd.DataFrame(columns=columnas_tabla)
    tabla_final_pro["Año"] = valores_tabla[0]
    tabla_final_pro["Ahorro del Periodo ($)"] = valores_tabla[1]
    tabla_final_pro["Flujo Acumulado ($)"] = valores_tabla[2]
    
