import streamlit as st
import pandas as pd
import base64
import json
import io
import urllib.parse
from openai import OpenAI
from fpdf import FPDF

# --- CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(page_title="Range of Solutions - Cotizador Pro IA", layout="centered", initial_sidebar_state="collapsed")

# Inicialización segura del cliente OpenAI con st.secrets (para cuando configures tu llave de IA)
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    client = None

# Encabezado e Imagen Corporativa adaptada a móviles
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        st.image("LOGO PNG2.png", use_container_width=True)
    except:
        st.markdown("<h3 style='text-align: center; color: #f39c12; margin-bottom:0;'>⚡ RANGE OF SOLUTIONS S.A.S. ⚡</h3>", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #f39c12; font-size: 24px; margin-top: 0px;'>☀️ COTIZADOR SOLAR FV INTELIGENTE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #7f8c8d; font-size: 14px;'>Ingeniería Avanzada, Automatización e Impacto Financiero</p>", unsafe_allow_html=True)

# --- MÓDULO 1: CAPTURA DE DATOS (LECTURA INTELIGENTE O MANUAL) ---
st.header("1. Entrada de Datos de Consumo")
metodo = st.selectbox("Método de captura de datos:", ["📸 Escaneo de Recibo con IA", "⌨️ Registro Manual"])

consumo_kwh = 0.0
tarifa_kwh = 0.0

if metodo == "📸 Escaneo de Recibo con IA":
    archivo = st.file_uploader("Sube la imagen del recibo (Air-e / Afinia)", type=['jpg', 'png', 'jpeg'])
    if archivo:
        if client is None:
            # SOLUCOINADO: Si no hay IA configurada, asigna los datos simulados reales del recibo para que no dé 0.0
            st.warning("⚠️ Modo demostración activo (API de OpenAI no conectada). Cargando datos simulados del recibo.")
            consumo_kwh = 2638.0
            tarifa_kwh = 1100.0
            st.success(f"✅ Datos cargados: {consumo_kwh:,.0f} kWh/mes a ${tarifa_kwh:,.1f}/kWh")
        else:
            with st.spinner("🤖 IA analizando variables, consumo y costos en el recibo..."):
                try:
                    bytes_data = archivo.read()
                    base64_image = base64.b64encode(bytes_data).decode('utf-8')
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Extrae de este recibo de energía en Colombia el consumo del último mes en kWh y la tarifa por kWh en pesos. Devuelve estrictamente un JSON válido con las llaves exactas: \"consumo\" y \"tarifa\". No agregues markdown ni introducciones."},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                            ]
                        }],
                        response_format={"type": "json_object"}
                    )
                    datos = json.loads(response.choices.message.content)
                    consumo_kwh = float(datos.get("consumo", 0.0))
                    tarifa_kwh = float(datos.get("tarifa", 0.0))
                    st.success(f"✅ Extraído con éxito: {consumo_kwh:,.0f} kWh/mes a ${tarifa_kwh:,.1f}/kWh")
                except Exception as e:
                    st.error(f"Error de lectura IA: {e}. Cargando datos de respaldo.")
                    consumo_kwh = 2638.0
                    tarifa_kwh = 1100.0
else:
    c1, c2 = st.columns(2)
    consumo_kwh = c1.number_input("Consumo Mensual (kWh/mes)", min_value=0.0, step=10.0, value=2638.0)
    tarifa_kwh = c2.number_input("Tarifa del Servicio ($/kWh)", min_value=0.0, step=1.0, value=1100.0)

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

# CORRECCIÓN DE LEY 1715: Paneles/Inversores exentos de IVA. Se grava solo la porción del servicio / instalación y su margen proporcional.
porcentaje_servicio = costo_instalacion / costo_base_total
precio_venta_servicio = precio_venta_neto * porcentaje_servicio
iva_ingenieria = precio_venta_servicio * 0.19
precio_final_cliente = precio_venta_neto + iva_ingenieria

col_m1, col_m2 = st.columns(2)
col_m1.metric("Margen Bruto Obtenido", f"$ {utilidad_bruta:,.0f}")
col_m2.metric("Precio de Venta (Con IVA)", f"$ {precio_final_cliente:,.0f}")

# --- MÓDULO 4: ENTORNO FINANCIERO DIDÁCTICO E INTERACTIVO (ROI) ---
st.header("4. Análisis de Recuperación de Inversión")

# Variables de simulación a 25 años
inflacion_energia = 0.06      # 6% incremento anual de tarifa estimado en Colombia
degradacion_paneles = 0.005   # 0.5% pérdida de potencia anual del sistema
eficiencia_sistema = 0.90     # Sustitución estimada del 90% del recibo

# Validación de seguridad para evitar multiplicaciones por cero
if consumo_kwh <= 0.0 or tarifa_kwh <= 0.0:
    consumo_calculo = 2638.0
    tarifa_calculo = 1100.0
else:
    consumo_calculo = consumo_kwh
    tarifa_calculo = tarifa_kwh

ahorro_mes_inicial = consumo_calculo * tarifa_calculo * eficiencia_sistema

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

# Cálculo matemático exacto del Payback
payback_exacto = 0.0
for idx, saldo in enumerate(flujo_caja_acumulado):
    if saldo >= 0:
        if idx == 0:
            payback_exacto = (precio_final_cliente - beneficio_fiscal_ley1715) / ahorros_anuales[0]
        else:
            prev_saldo = flujo_caja_acumulado[idx-1]
            payback_exacto = idx + (abs(prev_saldo) / ahorros_anuales[idx])
        break
if payback_exacto == 0.0:
    payback_exacto = (precio_final_cliente - beneficio_fiscal_ley1715) / (ahorro_mes_inicial * 12)

# Pestañas adaptativas (Didáctica vs Técnica)
tab1, tab2 = st.tabs(["💡 Para Todo Público (Didáctico)", "📊 Para Expertos (Matriz Técnica)"])

with tab1:
    st.success(f"⏱️ **¡Tu sistema se paga solo en {payback_exacto:.1f} años!** Posterior a esto, disfrutas de energía solar completamente gratuita.")
    col_v1, col_v2 = st.columns(2)
    col_v1.metric("Tu Ahorro Estimado Año 1", f"$ {ahorros_anuales[0]:,.0f}")
    col_v2.metric("Alivio Tributario (Ley 1715)", f"$ {beneficio_fiscal_ley1715:,.0f}")
    
    st.markdown(f"""
    ### ¿Por qué dar el paso con Range of Solutions?
    * **Freno inmediato a los abusos tarifarios**: Reduces el **{eficiencia_sistema*100:.0f}%** de la energía que le compras a operadores como Air-e o Afinia de forma garantizada.
    * **Beneficios tributarios de Ley 1715**: El estado colombiano te premia permitiéndote deducir el **33% de la inversión** directamente de tu impuesto de renta.
    * **Sostenibilidad ambiental**: Dejas de emitir aproximadamente **{(consumo_calculo * 12 * eficiencia_sistema * 0.4) / 1000:.1f} toneladas de CO2 al año**, lo que equivale al impacto positivo de sembrar **{int(consumo_calculo * 0.12)} árboles maduros**.
    """)

with tab2:
    st.caption("Evolución Detallada del Flujo de Caja Descontado y Pérdida de Eficiencia Mínima")
    df_financiero = pd.DataFrame({
        "Año": años,
        "Ahorro del Periodo ($)": ahorros_anuales,
        "Flujo Acumulado ($)": flujo_caja_acumulado
    })
    st.dataframe(df_financiero.style.format({"Ahorro del Periodo ($)": "$ {:,.0f}", "Flujo Acumulado ($)": "$ {:,.0f}"}), use_container_width=True)
    st.line_chart(df_financiero.set_index("Año")["Flujo Acumulado ($)"])

# --- MÓDULO 5: MOTOR DE EXPORTACIÓN Y CIERRE COMERCIAL ---
st.header("5. Entregables y Cierre de Venta")

# Estructura limpia para PDF Corporativo
class CotizadorSolarPDF(FPDF):
    def header(self):
        self.set_fill_color(243, 156, 18) # Naranja corporativo
        self.rect(0, 0, 210, 15, 'F')
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(255, 255, 255)
        self.cell(0, -2, "RANGE OF SOLUTIONS S.A.S. - INFORME ENERGÉTICO", align='C')
        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(127, 138, 143)
        self.cell(0, 10, f"Página {self.page_no()} | Propuesta generada automáticamente por Range Solutions", align='C')

def generar_propuesta_pdf():
    pdf = CotizadorSolarPDF()
    pdf.add_page()
    pdf.set_margins(15, 20, 15)
    
    pdf.set_y(25)
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(44, 62, 80)
    pdf.cell(0, 10, "ESTUDIO DE FACTIBILIDAD Y OFERTA SOLAR FV", ln=True)
    
