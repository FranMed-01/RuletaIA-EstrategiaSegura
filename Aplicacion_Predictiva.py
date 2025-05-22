# Archivo: Aplicacion_Predictiva_WEB.py

import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import accuracy_score

# --- Configuración general ---
st.set_page_config(page_title="Ruleta IA (Web)", layout="wide")
st.title("🎰 Estrategia Segura - Web")

# --- Estado inicial ---
if 'historial' not in st.session_state:
    st.session_state.historial = ["32", "15", "19", "23", "8", "14", "3", "26", "0", "32"]

# --- Datos de entrenamiento ---
def column_of_number(n):
    if n == 0: return None
    return 1 if n % 3 == 1 else 2 if n % 3 == 2 else 3

def obtener_color(n):
    NUMEROS_ROJOS = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
    NUMEROS_NEGROS = {2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35}
    if n == 0: return "green"
    if n in NUMEROS_ROJOS: return "red"
    if n in NUMEROS_NEGROS: return "black"
    return "gray"

def preparar_datos_ml(historial, ventana=3):
    datos = []
    for i in range(len(historial) - ventana):
        fila = {}
        for j in range(ventana):
            n = int(historial[i + j])
            fila[f'n{j+1}'] = n
            fila[f'col{j+1}'] = column_of_number(n)
            fila[f'color{j+1}'] = obtener_color(n)
        siguiente = int(historial[i + ventana])
        target = column_of_number(siguiente)
        if target is not None:
            fila['col_target'] = target
            datos.append(fila)
    return pd.DataFrame(datos)

def entrenar_modelo_rf(df):
    X = df.drop('col_target', axis=1)
    y = df['col_target']
    cat_features = [col for col in X.columns if 'color' in col]
    num_features = [col for col in X.columns if col not in cat_features]

    preprocessor = ColumnTransformer([
        ('num', 'passthrough', num_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), cat_features)
    ])

    model = Pipeline([
        ('prep', preprocessor),
        ('clf', RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    model.fit(X, y)
    return model

def predecir_columna(model, historial):
    entrada = {}
    for j in range(3):
        n = int(historial[j])
        entrada[f'n{j+1}'] = n
        entrada[f'col{j+1}'] = column_of_number(n)
        entrada[f'color{j+1}'] = obtener_color(n)
    df_fila = pd.DataFrame([entrada])
    predicho = model.predict(df_fila)[0]
    return predicho

# --- Entrenamiento y predicción ---
historial = st.session_state.historial
if len(historial) < 10:
    st.warning("🔄 Se requieren al menos 10 números para hacer predicciones.")
else:
    df = preparar_datos_ml(historial)
    model = entrenar_modelo_rf(df)
    pred = predecir_columna(model, historial)
    st.success(f"🎯 Columna sugerida por IA: **Columna {pred}**")

# --- Mostrar historial actual ---
st.markdown("### 🎲 Historial de resultados")
st.write(", ".join(historial))

nuevo = st.text_input("🔢 Ingresar nuevo número (1-36, sin 0)")
if st.button("➕ Agregar al historial"):
    if nuevo.isdigit() and 1 <= int(nuevo) <= 36:
        st.session_state.historial.insert(0, nuevo)
        st.rerun()
    else:
        st.error("Por favor ingresa un número válido entre 1 y 36.")
