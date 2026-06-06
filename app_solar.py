# --- MÓDULO 4: ENTORNO FINANCIERO (ROI) - CORREGIDO ---
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
            # CORRECCIÓN: Usamos el índice [0] para dividir por el valor numérico del primer año
            payback_exacto = (precio_final_cliente - beneficio_fiscal_ley1715) / ahorros_anuales[0]
        else:
            payback_exacto = idx + (abs(flujo_caja_acumulado[idx-1]) / ahorros_anuales[idx])
        break
else:
    payback_exacto = 25.0

col_r1, col_r2, col_r3 = st.columns(3)
col_r1.metric("Ahorro Primer Año", f"$ {ahorros_anuales[0]:,.0f}") # CORRECCIÓN AQUÍ TAMBIÉN
col_r2.metric("Ley 1715 (Deducción 33%)", f"$ {beneficio_fiscal_ley1715:,.0f}")
col_r3.metric("Tiempo de Retorno", f"{payback_exacto:.1f} Años")

df_financiero = pd.DataFrame({
    "Año": años,
    "Flujo Acumulado ($)": flujo_caja_acumulado
})
st.line_chart(df_financiero.set_index("Año")["Flujo Acumulado ($)"])
