import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib
import requests

st.title('Entrenamiento y guardado del modelo EUR/USD')

API_KEY = st.text_input('Introduce tu API Key de FRED', value='e408dc9ed32f1616614069090f08be8c')
START_DATE = st.text_input('Fecha de inicio de datos', value='2010-01-01')

VARIABLES_FRED = {
    'EURUSD': 'DEXUSEU',
    'DXY': 'DTWEXBGS',
    'CPI': 'CPIAUCSL',
    'FEDFUNDS': 'FEDFUNDS',
    'GDP': 'GDP',
}

def descargar_fred(serie_id, api_key, start_date='2000-01-01'):
    url = f'https://api.stlouisfed.org/fred/series/observations?series_id={serie_id}&api_key={api_key}&file_type=json&observation_start={start_date}'
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()['observations']
        df = pd.DataFrame(data)[['date', 'value']]
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        return df
    else:
        st.error(f'Error descargando {serie_id}: {r.status_code}')
        return pd.DataFrame()

if st.button('Entrenar y guardar modelo'):
    st.info('Descargando datos y entrenando modelo...')
    dfs = []
    for nombre, serie_id in VARIABLES_FRED.items():
        df = descargar_fred(serie_id, API_KEY, START_DATE)
        df = df.rename(columns={'value': nombre})
        dfs.append(df)
    df_merged = pd.concat(dfs, axis=1)
    df_limpio = df_merged.asfreq('D').interpolate(method='linear')
    lags = [1, 2, 3]
    df_features = df_limpio.copy()
    for var in df_features.columns:
        for lag in lags:
            df_features[f'{var}_lag{lag}'] = df_features[var].shift(lag)
    df_features = df_features.dropna()
    target = 'EURUSD'
    predictors = [col for col in df_features.columns if col != target]
    X = df_features[predictors]
    y = df_features[target]
    split_idx = int(len(df_features) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    modelo = RandomForestRegressor(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)
    joblib.dump(modelo, 'modelo_eurusd_multivariable.pkl')
    st.success('Modelo entrenado y guardado como modelo_eurusd_multivariable.pkl en el entorno de Streamlit.')
