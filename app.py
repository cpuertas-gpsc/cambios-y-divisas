import streamlit as st
import pandas as pd
import requests
import joblib
from datetime import datetime
import io


# 🎨 Configuración visual corporativa
st.set_page_config(page_title="Predicción USD/EUR", layout="wide")

# ✅ Fondo con imagen corporativa difuminada y repetida
st.markdown("""
    <style>
    .stApp {
        background-image: url("https://raw.githubusercontent.com/cpuertas-gpsc/-Predicci-n-del-valor-del-d-lar-y-estrategia-de-divisas/main/consturcciones-felipe-castellano-edificio-moderno-1500x630.jpg");
        background-size: cover;
        background-repeat: repeat-y;
        background-attachment: fixed;
    }
    .overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(255, 255, 255, 0.2);
        z-index: -1;
    }
    </style>
    <div class="overlay"></div>
    """, unsafe_allow_html=True)


# ✅ Estilos personalizados
st.markdown("""
    <style>
    body {
        background-color: #f5f7fa;
        font-family: 'Segoe UI', sans-serif;
    }
    h1, h2, h3 {
        color: #0b6cb7;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    div[data-testid="stSidebar"] {
        background-color: #e6f2ff;
    }
    .logo {
        position: fixed;
        top: 20px;
        left: 20px;
        z-index: 100;
    }
    </style>
    """, unsafe_allow_html=True)

# ✅ Logo institucional fijo
st.markdown("""
    <style>
    .logo {
        position: fixed;
        top: 20px;
        left: 20px;
        z-index: 100;
    }
    </style>
    <img class="logo" src="https://raw.githubusercontent.com/cpuertas-gpsc/-Predicci-n-del-valor-del-d-lar-y-estrategia-de-divisas/main/logo%20grupo.JPG" width="240">
    """, unsafe_allow_html=True)


# ✅ Título institucional
st.title("Sistema Predictivo USD/EUR Grupo Procourval")

# 🔗 Función robusta para obtener datos desde FRED
def obtener_serie_dolar_fred(api_key: str) -> pd.DataFrame:
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": "DEXUSEU",
        "api_key": api_key,
        "file_type": "json",
        "sort_order": "asc",
        "limit": 10000
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        st.error(f"Error al obtener datos de FRED: {e}")
        return pd.DataFrame(columns=["ds", "valor_real"])

    fechas, valores = [], []
    for obs in data.get("observations", []):
        try:
            valor = float(obs["value"])
            fecha = pd.to_datetime(obs["date"])
            fechas.append(fecha)
            valores.append(valor)
        except ValueError:
            continue

    df = pd.DataFrame({"ds": fechas, "valor_real": valores})
    return df


## 🔑 Clave API FRED
api_key = "e408dc9ed32f1616614069090f08be8c"
serie_fred = obtener_serie_dolar_fred(api_key)
valor_dolar = serie_fred["valor_real"].iloc[-1]
fecha_dato = serie_fred["ds"].iloc[-1]

# 📆 Formatear fecha como Año-Mes
fecha_formateada = pd.to_datetime(fecha_dato).strftime("%Y-%m")

# 💬 Mostrar valor actual con protagonismo
st.markdown(f"""
<div style='
    background-color:#e6f2ff;
    padding:25px;
    border-radius:10px;
    border-left:8px solid #0b6cb7;
    color:#0b6cb7;
    text-align:center;
'>
    <div style='font-size:26px; font-weight:bold;'>Valor del dólar HOY</div>
    <div style='font-size:14px; margin-bottom:10px;'>Fecha: {fecha_formateada}</div>
    <div style='font-size:48px; font-weight:bold;'>{round(valor_dolar, 4)}</div>
    <div style='font-size:14px; margin-top:10px;'>
        Fuente: <a href="https://fred.stlouisfed.org/series/DEXUSEU" target="_blank" style='color:#0b6cb7;'>FRED - Reserva Federal</a>
    </div>
</div>
""", unsafe_allow_html=True)


# 📦 Cargar modelo Prophet entrenado y forecast actualizado
import numpy as np
# Cargar modelo multivariable y datos de test
modelo = joblib.load("modelo_eurusd_multivariable.pkl")
df_test = pd.read_csv("test_multivariable.csv", parse_dates=["date"])
X_test = df_test.drop(columns=["EURUSD", "date"])
y_test = df_test["EURUSD"]

# Cargar predicciones de escenarios
y_pred_neu = modelo.predict(X_test)

# Simular escenarios positivo y negativo (ajustando variables clave)
def crear_escenario(X_base, tipo='neutro', variacion=0.02):
    X_mod = X_base.copy()
    if tipo == 'positivo':
        X_mod['DXY'] *= (1 + variacion)
        X_mod['CPI'] *= (1 - variacion)
        X_mod['FEDFUNDS'] *= (1 - variacion)
        X_mod['GDP'] *= (1 + variacion)
    elif tipo == 'negativo':
        X_mod['DXY'] *= (1 - variacion)
        X_mod['CPI'] *= (1 + variacion)
        X_mod['FEDFUNDS'] *= (1 + variacion)
        X_mod['GDP'] *= (1 - variacion)
    return X_mod

X_test_pos = crear_escenario(X_test, 'positivo')
X_test_neg = crear_escenario(X_test, 'negativo')
y_pred_pos = modelo.predict(X_test_pos)
y_pred_neg = modelo.predict(X_test_neg)


# 📅 Selector de fecha (ahora con rango extendido de 3 años)
st.markdown("### Predicción futura del USD/EUR")
fecha_seleccionada = st.date_input(
    "Selecciona una fecha para ver los tres escenarios:",
    value=forecast["ds"].max().date(),
    min_value=forecast["ds"].min().date(),
    max_value=forecast["ds"].max().date()
)

st.markdown(f"<div style='color:#0b6cb7; font-size:14px;'>Rango disponible: <strong>{forecast['ds'].min().date()}</strong> a <strong>{forecast['ds'].max().date()}</strong></div>", unsafe_allow_html=True)


# 🔍 Buscar la fecha más cercana
fecha_objetivo = pd.to_datetime(fecha_seleccionada)
fecha_mas_cercana = forecast["ds"].iloc[(forecast["ds"] - fecha_objetivo).abs().argsort()[0]]
prediccion = forecast[forecast["ds"] == fecha_mas_cercana]

if not prediccion.empty:
    neutro = round(prediccion["yhat"].values[0], 4)
    positivo = round(prediccion["yhat_upper"].values[0], 4)
    negativo = round(prediccion["yhat_lower"].values[0], 4)

    st.markdown(f"""
    <div style='background-color:#ffffffcc; padding:20px; border-left:6px solid #0b6cb7; border-radius:10px; color:#0b6cb7;'>
        <h3>📈 Predicción para {fecha_mas_cercana.strftime('%Y-%m-%d')}</h3>
        <ul style='list-style:none; padding-left:0; font-size:16px;'>
            <li>🔵 Escenario base: <strong>{neutro}</strong></li>
            <li>🟢 Escenario optimista: <strong>{positivo}</strong></li>
            <li>🔴 Escenario pesimista: <strong>{negativo}</strong></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("No se encontró ninguna predicción cercana.")

# Mostrar predicción para la última fecha de test
st.markdown("### Predicción multivariable EUR/USD (última fecha de test)")
ultima_fecha = df_test["date"].iloc[-1]
neutro = round(y_pred_neu[-1], 4)
positivo = round(y_pred_pos[-1], 4)
negativo = round(y_pred_neg[-1], 4)

st.markdown(f"""
<div style='background-color:#ffffffcc; padding:20px; border-left:6px solid #0b6cb7; border-radius:10px; color:#0b6cb7;'>
    <h3>📈 Predicción para {ultima_fecha.strftime('%Y-%m-%d')}</h3>
    <ul style='list-style:none; padding-left:0; font-size:16px;'>
        <li>🔵 Escenario base: <strong>{neutro}</strong></li>
        <li>🟢 Escenario optimista: <strong>{positivo}</strong></li>
        <li>🔴 Escenario pesimista: <strong>{negativo}</strong></li>
    </ul>
</div>
""", unsafe_allow_html=True)
# 📊 Gráfico con escenarios + valor real desde la API
datos_reales_filtrados = serie_fred[serie_fred["ds"].isin(forecast["ds"])]
import plotly.graph_objects as go


# 📊 Gráfico con escenarios Prophet + valor real desde la API
fig = go.Figure()
fig.add_trace(go.Scatter(x=forecast["ds"], y=forecast["yhat"], mode='lines', name='Base', line=dict(color='blue')))
fig.add_trace(go.Scatter(x=forecast["ds"], y=forecast["yhat_upper"], mode='lines', name='Optimista', line=dict(color='green', dash='dot')))
fig.add_trace(go.Scatter(x=forecast["ds"], y=forecast["yhat_lower"], mode='lines', name='Pesimista', line=dict(color='red', dash='dot')))
fig.add_trace(go.Scatter(x=datos_reales_filtrados["ds"], y=datos_reales_filtrados["valor_real"], mode='lines', name='Valor real', line=dict(color='gold', width=2, dash='dot')))

fig.update_layout(
    title="Proyección USD/EUR por escenarios Prophet vs. valor real",
    xaxis_title="Fecha",
    yaxis_title="Valor USD/EUR",
    template="plotly_white",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)


# 📊 Comparativa con valor real
valor_real_fila = datos_reales_filtrados[datos_reales_filtrados["ds"] == fecha_mas_cercana]

if not valor_real_fila.empty:
    valor_real = round(valor_real_fila["valor_real"].values[0], 4)
    dif_base = round((neutro - valor_real) / valor_real * 100, 2)
    dif_optimista = round((positivo - valor_real) / valor_real * 100, 2)
    dif_pesimista = round((negativo - valor_real) / valor_real * 100, 2)

    st.markdown("### Comparativa con valor real")
    comparativa = pd.DataFrame({
        "Escenario": ["Real", "Base", "Optimista", "Pesimista"],
        "Valor USD/EUR": [valor_real, neutro, positivo, negativo],
        "Diferencia (%) vs. Real": [0.0, dif_base, dif_optimista, dif_pesimista]
    })
    st.dataframe(comparativa.style.format({"Valor USD/EUR": "{:.4f}", "Diferencia (%) vs. Real": "+{:.2f}%"}))

    # 💬 Recomendación financiera profesional
    if dif_optimista > 1.5:
        st.success(f"""💼 <strong>Recomendación:</strong> Se proyecta una apreciación del dólar frente al euro. 
        <br>Desde una perspectiva financiera, <strong>conviene esperar</strong> para vender, ya que el escenario optimista sugiere una mejora en el tipo de cambio.""", unsafe_allow_html=True)
    elif dif_pesimista < -1.5:
        st.error(f"""💼 <strong>Recomendación:</strong> El escenario pesimista indica una posible depreciación del dólar. 
        <br>Desde un enfoque conservador, <strong>conviene vender ahora</strong> para evitar pérdidas futuras.""", unsafe_allow_html=True)
    else:
        st.info(f"""💼 <strong>Recomendación:</strong> Las proyecciones muestran variaciones moderadas. 
        <br>Desde una perspectiva de estabilidad, <strong>puede mantenerse la posición</strong> o realizar la venta según necesidades de liquidez.""", unsafe_allow_html=True)

else:
    st.markdown("### Predicción")
    comparativa = pd.DataFrame({
        "Escenario": ["Base", "Optimista", "Pesimista"],
        "Valor USD/EUR": [neutro, positivo, negativo]
    })
    st.dataframe(comparativa.style.format({"Valor USD/EUR": "{:.4f}"}))


# 📤 Convertir tabla a CSV
csv_buffer = io.StringIO()
comparativa.to_csv(csv_buffer, index=False)
csv_data = csv_buffer.getvalue()

# 📥 Botón de descarga
st.download_button(
    label="📥 Descargar tabla como CSV",
    data=csv_data,
    file_name="comparativa_usdeur.csv",
    mime="text/csv"
)


# 📊 Resumen de la predicción
st.markdown("### Resumen de la predicción")
st.markdown(f"""
<div style='background-color:#e6f2ff; padding:20px; border-radius:10px; color:#0b6cb7; font-size:16px;'>

<strong>Fecha proyectada:</strong> {fecha_mas_cercana.strftime('%Y-%m-%d')}<br><br>

🔵 Escenario base: <strong>{neutro}</strong><br>
🟢 Escenario optimista: <strong>{positivo}</strong><br>
🔴 Escenario pesimista: <strong>{negativo}</strong><br><br>

<strong>Análisis experto:</strong><br>
• Rango total entre escenarios: <strong>{round(positivo - negativo, 4)}</strong><br>
• Desviación estimada: <strong>{round(((positivo - negativo)/2), 4)}</strong><br>
• Distancia al base → Optimista: <strong>{round(positivo - neutro, 4)}</strong> / Pesimista: <strong>{round(neutro - negativo, 4)}</strong><br><br>

<strong>Recomendación estratégica:</strong><br>
{f"📈 El modelo muestra una dispersión significativa (>10%), lo que sugiere alta volatilidad. Se recomienda cobertura parcial si hay exposición al USD." if (positivo - negativo) > 0.1 else "📉 La dispersión es moderada. Puede mantenerse la posición actual, pero se recomienda monitoreo activo."}

</div>
""", unsafe_allow_html=True)

# 📘 Valores predichos manuales (para simulación)
neutro = 1.1569
positivo = 1.2147
negativo = 1.0990
valor_actual = 1.1555
fecha_mas_cercana = datetime(2028, 6, 30)

# 📐 Cálculos de dispersión y riesgo
rango = round(positivo - negativo, 4)
desviacion = round(rango / 2, 4)
dist_pos = round(positivo - neutro, 4)
dist_neg = round(neutro - negativo, 4)
riesgo = "Alto" if rango > 0.1 else "Moderado" if rango > 0.05 else "Bajo"

# 📘 Metodología del modelo
st.markdown("### Metodología del modelo")
st.markdown(f"""
<div style='background-color:#f0f8ff; padding:20px; border-radius:10px; color:#0b6cb7; font-size:16px;'>

<strong>Variables utilizadas:</strong><br>
• USD/EUR: tipo de cambio diario<br>
• DXY: índice de fortaleza del dólar<br>
• Inflación USA: IPC<br>
• Tasa de interés Fed: fondos federales efectivos<br><br>

<strong>Modelo aplicado:</strong><br>
• Prophet entrenado desde 2010<br>
• Simulación de tres escenarios<br>
• Análisis de dispersión y riesgo<br><br>

<strong>Fuentes oficiales:</strong><br>
• <a href="https://fred.stlouisfed.org/series/DEXUSEU" target="_blank">FRED - Reserva Federal</a><br>
• <a href="https://finance.yahoo.com/quote/EURUSD=X" target="_blank">Yahoo Finance</a><br><br>

<strong>Repositorio del proyecto:</strong><br>
• <a href="https://github.com/cpuertas-gpsc/-Predicci-n-del-valor-del-d-lar-y-estrategia-de-divisas" target="_blank">Grupo Procourval – GitHub</a>

</div>
""", unsafe_allow_html=True)


# 📊 Diagnóstico del modelo
st.markdown("### Diagnóstico del modelo Prophet (actualizado)")
st.markdown(f"""
<div style='background-color:#f0f8ff; padding:20px; border-radius:10px; color:#0b6cb7; font-size:16px;'>

<strong>Dispersión proyectada:</strong><br>
• Rango entre escenarios: <strong>{round(positivo - negativo, 4)}</strong> puntos USD/EUR<br>
• Desviación media: <strong>{round((positivo - negativo)/2, 4)}</strong> puntos desde el base<br><br>

<strong>Métricas de fiabilidad (último mes):</strong><br>
• MAE: <strong>{comparacion['y'].sub(comparacion['yhat']).abs().mean():.5f}</strong><br>
• RMSE: <strong>{((comparacion['y'] - comparacion['yhat'])**2).mean()**0.5:.5f}</strong><br>
{f"• Porcentaje de aciertos en agosto (<0.01): <strong>{comparacion_agosto['acierto'].mean()*100:.2f}%</strong><br>• Desviación estándar del error en agosto: <strong>{comparacion_agosto['error'].std():.5f}</strong>" if comparacion_agosto is not None and not comparacion_agosto.empty else ''}
<br>
<strong>Interpretación técnica:</strong><br>
Este rango representa la amplitud entre los extremos proyectados por el modelo. Refleja la sensibilidad del tipo de cambio ante factores macroeconómicos y permite identificar ventanas de incertidumbre relevantes para la toma de decisiones.<br><br>

<strong>Lectura analítica:</strong><br>
La amplitud observada sugiere un entorno de volatilidad relevante. Este comportamiento puede estar asociado a expectativas de política monetaria, tensiones geopolíticas o variaciones en indicadores clave como el DXY o la inflación. Se recomienda evaluar la exposición al USD en función del perfil de riesgo y horizonte temporal de cada operación.

</div>
""", unsafe_allow_html=True)

# 📚 Contexto histórico y fuentes complementarias
st.markdown("### Antecedentes y análisis complementario")
st.markdown("""
<div style='background-color:#f5f7fa; padding:20px; border-left:6px solid #0b6cb7; border-radius:10px; font-size:16px; color:#0b6cb7;'>

Para enriquecer la interpretación del modelo, se recomienda consultar fuentes especializadas:
<ul style='padding-left:20px;'>
<li><a href="https://es.investing.com/currencies/eur-usd-historical-data" target="_blank">Histórico EUR/USD – Investing.com</a></li>
<li><a href="https://www.fxstreet.es/rates-charts/eurusd/forecast" target="_blank">Previsión de expertos – FXStreet</a></li>
<li><a href="https://tradersunion.com/es/currencies/forecast/eur-usd/" target="_blank">Pronóstico técnico – TradersUnion</a></li>
<li><a href="https://coincodex.com/es/forex/usd-eur/forecast/" target="_blank">Proyección a largo plazo – CoinCodex</a></li>
</ul>

</div>
""", unsafe_allow_html=True)

# 📬 Firma institucional
st.markdown("---")
col1, col2 = st.columns([1, 5])
with col1:
    st.image("logo mail.jpg", width=120)
with col2:
    st.markdown("""
    <div style='font-size: 15px; color: #666;'>
        Aplicación desarrollada por Cristina Puertas<br>
        Departamento de Análisis de Datos<br>
        <a href='mailto:cpuertas@gpsc.es' style='color: #666;'>cpuertas@gpsc.es</a>
    </div>
    """, unsafe_allow_html=True)

