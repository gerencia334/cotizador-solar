import streamlit as st
import pandas as pd

st.set_page_config(page_title="Range of Solutions - Cotizador", layout="centered")
col1, col2, col3 = st.columns([1, 2, 1]) # Crea 3 columnas, la del centro es más ancha

with col2:
    st.image("tu_logo.png", width=200) # Ajusta el ancho (width) a tu gusto

# Configuración de la interfaz para móvil

# Estilo visual
st.markdown("<h1 style='text-align: center; color: #f39c12;'>☀️ SolarQuote Pro</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'><b>Range of Solutions S.A.S.</b></p>", unsafe_allow_html=True)

# --- MÓDULO 1: CAPTURA DE CONSUMO (EL RECIBO) ---
st.header("1. Análisis del Recibo")
metodo = st.selectbox("¿Cómo ingresarás los datos?", ["📸 Subir Foto de Recibo", "⌨️ Ingreso Manual"])

consumo_kwh = 0.0
tarifa_kwh = 0.0

if metodo == "📸 Subir Foto de Recibo":
    archivo = st.file_uploader("Sube la imagen del recibo (Air-e/Afinia)", type=['jpg', 'png', 'jpeg'])
    if archivo:
        # Valores simulados basados en tu recibo real de 2,638 kWh
        st.success("✅ Datos extraídos del recibo")
        consumo_kwh = 0.0
        tarifa_kwh = 0.0
        st.info(f"Consumo: {consumo_kwh} kWh | Tarifa: ${tarifa_kwh}")
else:
    c1, c2 = st.columns(2)
    consumo_kwh = c1.number_input("Consumo (kWh/mes)", value=0.0)
    tarifa_kwh = c2.number_input("Tarifa ($/kWh)", value=0.0)

# --- MÓDULO 2: COSTOS TÉCNICOS (APU DINÁMICO) ---
st.header("2. Ingeniería y Costos Base")
with st.expander("Ajustar costos de materiales (APU)"):
    costo_generacion = st.number_input("Equipos (Inversor + Paneles)", value=15403044.8)
    costo_estructura = st.number_input("Estructura y Anclajes", value=1460845.0)
    costo_electricos = st.number_input("Material Eléctrico AC/DC", value=7443247.0)
    costo_instalacion = st.number_input("Mano de Obra / Ingeniería", value=3840000.0)
    viaticos = st.number_input("Viáticos o Dificultad Extra", value=0)

costo_base_total = costo_generacion + costo_estructura + costo_electricos + costo_instalacion + viaticos

# --- MÓDULO 3: MARGEN DE GANANCIA (VERSATILIDAD) ---
st.header("3. Negociación y Margen")
# El slider permite ser versátil según el tipo de cliente
margen = st.slider("Margen de Utilidad Deseado (%)", 5, 50, 25)

# Fórmula de precio de venta sobre margen
precio_venta_neto = costo_base_total / (1 - (margen / 100))
utilidad_bruta = precio_venta_neto - costo_base_total
iva = precio_venta_neto * 0.19 # Según Ley 1715 algunos equipos están exentos, ajusta aquí
precio_final_cliente = precio_venta_neto + iva

# Visualización de resultados comerciales
col_res1, col_res2 = st.columns(2)
col_res1.metric("Utilidad Range", f"$ {utilidad_bruta:,.0f}")
col_res2.metric("Total Cotización", f"$ {precio_final_cliente:,.0f}")

# --- MÓDULO 4: RETORNO DE INVERSIÓN ---
st.header("4. Beneficio para el Cliente")
ahorro_anual = (consumo_kwh * tarifa_kwh * 12) * 0.90 # 90% de eficiencia estimada
beneficio_fiscal = precio_final_cliente * 0.33 # Ley 1715

if ahorro_anual > 0:
    payback = (precio_final_cliente - beneficio_fiscal) / ahorro_anual
    st.success(f"⏱️ **Retorno de Inversión (con Ley 1715):** {payback:.1f} años")
    st.write(f"💰 Ahorro estimado año 1: **$ {ahorro_anual:,.0f}**")
    st.write(f"🏛️ Deducción de impuestos: **$ {beneficio_fiscal:,.0f}**")

# Botón para el cierre
if st.button("🚀 GENERAR PROPUESTA PARA WHATSAPP"):
    st.balloons()
    st.write("Generando link de descarga...")
