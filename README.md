![Logo Grupo Procourval](logo%20grupo.JPG)
# 💱 Predicción del valor del dólar y estrategia de divisas

**Grupo Procourval**  
**Responsable del proyecto:** Cristina Puertas

Este proyecto ha sido desarrollado por el equipo de Grupo Procourval con el objetivo de optimizar la gestión de riesgos y fortalecer la toma de decisiones estratégicas en operaciones de divisas. Se implementan técnicas avanzadas de modelado predictivo y análisis de escenarios para anticipar la evolución del valor del dólar en horizontes de 1 a 3 años, en respuesta a variables macroeconómicas clave.

---

## 🎯 Objetivo General

Desarrollar un sistema predictivo capaz de estimar el valor futuro del dólar frente al euro y definir una estrategia óptima de conversión de divisas, considerando tres escenarios contrastantes:

- 🔵 **Neutro:** evolución proyectada sin shocks relevantes  
- 🔴 **Negativo:** condiciones macroeconómicas adversas (inflación, política monetaria contractiva, riesgos geopolíticos)  
- 🟢 **Positivo:** factores que fortalecen el dólar (crecimiento sostenido, política expansiva, estabilidad global)

---

## 🧠 Metodología Aplicada

1. Recolección de series temporales desde fuentes económicas oficiales  
2. Limpieza estructural y estandarización de datos  
3. Exploración visual y estadística (EDA)  
4. Modelado con algoritmos de series temporales (Prophet)  
5. Simulación de escenarios con proyecciones ajustadas  
6. Diseño estratégico según perfil de riesgo y objetivos operativos

---

## 📁 Estructura del Proyecto

| Notebook                        | Propósito                                                  |
|--------------------------------|-------------------------------------------------------------|
| `00_carga_datos.ipynb`         | Obtención de datos desde fuentes web/API                   |
| `01_exploracion_datos.ipynb`   | Limpieza, análisis exploratorio, visualización             |
| `02_modelado_predictivo.ipynb` | Entrenamiento del modelo, generación de escenarios         |
| `03_modelo_combinado.ipynb`    | Fusión de modelos para mayor precisión y estabilidad       |
| `04_estrategia_divisas.ipynb`  | Diseño de estrategia operativa según perfil de riesgo      |

---

## 📦 Entregables

- `dataset_final_economico.csv`: Dataset limpio y consolidado  
- `modelo_prophet.pkl`: Modelo entrenado con Prophet  
- `sistema_usdeur.pkl`: Modelo combinado para la app  
- App Streamlit (`app.py`) con simulación de escenarios  
- Notebooks explicativos y reproducibles  
- Informe ejecutivo en PDF  
- Dosier técnico institucional  
- Logotipo corporativo (`Logotipo grupo.JPG`)

---

## 📊 Variables Económicas Recopiladas

| Variable         | Fuente            | Frecuencia | Descripción |
|------------------|-------------------|------------|-------------|
| USD/EUR          | Yahoo Finance     | Diaria     | Tipo de cambio bilateral |
| DXY              | Yahoo Finance     | Diaria     | Índice de fortaleza del dólar |
| Inflación USA    | FRED (`CPIAUCSL`) | Mensual    | Índice de Precios al Consumidor |
| Tasa de interés  | FRED (`FEDFUNDS`) | Mensual    | Tasa de fondos federales efectiva |

---

## 🔮 Predicción y estrategia

La app permite seleccionar una fecha futura y visualizar la predicción del USD/EUR bajo tres escenarios. Para el 30 de junio de 2028, por ejemplo:

| Escenario   | Valor USD/EUR |
|-------------|----------------|
| Neutro      | 1.1569         |
| Positivo    | 1.2147         |
| Negativo    | 1.0990         |

📌 Recomendación: ante una dispersión significativa (>10%), se sugiere cobertura parcial si hay exposición al USD.

---

## 🌐 Fuentes oficiales

- [FRED – Reserva Federal](https://fredaccount.stlouisfed.org/apikey)  
- [Yahoo Finance – EUR/USD](https://finance.yahoo.com/quote/EURUSD=X)  
- [Repositorio del proyecto en GitHub](https://github.com/cpuertas-gpsc/-Predicci-n-del-valor-del-d-lar-y-estrategia-de-divisas?search=1)

---

## 🧠 Objetivo técnico

Optimizar la toma de decisiones en operaciones de divisas mediante inteligencia predictiva, simulación de escenarios y análisis financiero especializado.
