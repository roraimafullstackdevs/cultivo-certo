import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import streamlit as st
import os
from sqlalchemy import create_engine
from datetime import date, timedelta
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor


# Função para configurar a conexão com o banco de dados
def get_db_engine():
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_name = os.getenv('DB_NAME')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')

    db_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    try:
        engine = create_engine(db_url)
        return engine
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Função para carregar os dados do banco de dados
def load_data(engine):
    if engine is None:
        return None
    try:
        query = "SELECT * FROM dados_coleta"
        df = pd.read_sql_query(query, engine)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return None


# Função para pré-processar os dados
def preprocess_data(df):
    if df is None:
        return None

    try:
        df['data_coleta'] = pd.to_datetime(df['data_coleta'])
        df = df.sort_values('data_coleta')
        df['dias'] = (df['data_coleta'] - df['data_coleta'].min()).dt.days
        return df
    except Exception as e:
        st.error(f"Erro no pré-processamento dos dados: {e}")
        return None


def preprocess_data(df):
    if df is None:
        return None
    try:
        df['data_coleta'] = pd.to_datetime(df['data_coleta'])
        df = df.sort_values('data_coleta')
        df['dias'] = (df['data_coleta'] - df['data_coleta'].min()).dt.days

        # Engenharia de recursos
        df['mes'] = df['data_coleta'].dt.month
        df['dia_do_ano'] = df['data_coleta'].dt.dayofyear
        df['sin_dia_ano'] = np.sin(2 * np.pi * df['dia_do_ano'] / 365)
        df['cos_dia_ano'] = np.cos(2 * np.pi * df['dia_do_ano'] / 365)

         # One-hot encoding para 'tipo_armadilha'
        df = pd.get_dummies(df, columns=['tipo_armadilha'], drop_first=True, dummy_na=False)

        return df
    except Exception as e:
        st.error(f"Erro no pré-processamento dos dados: {e}")
        return None
    
def train_model(df):
    if df is None:
        return None

    try:
        features = ['dias', 'mes', 'sin_dia_ano', 'cos_dia_ano', 'temp_media_ultimos_dias', 'precipitacao_acumulada']  # Remove 'tipo_armadilha' das features
        X = df[features]
        y = df['total_captura']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        return model, features

    except Exception as e:
        st.error(f"Erro no treinamento do modelo: {e}")
        return None

def predict_future(model, df, features, days_to_predict=60):
    if df is None or model is None:
        return None

    try:
        ultima_data = df['data_coleta'].max()
        future_dates = [ultima_data + timedelta(days=i) for i in range(1, days_to_predict + 1)]

        # Criar DataFrame para as previsões futuras com as mesmas colunas que X
        future_df = pd.DataFrame({'data_coleta': future_dates})
        future_df['dias'] = (future_df['data_coleta'] - df['data_coleta'].min()).dt.days
        future_df['mes'] = future_df['data_coleta'].dt.month
        future_df['dia_do_ano'] = future_df['data_coleta'].dt.dayofyear
        future_df['sin_dia_ano'] = np.sin(2 * np.pi * future_df['dia_do_ano'] / 365)
        future_df['cos_dia_ano'] = np.cos(2 * np.pi * future_df['dia_do_ano'] / 365)
        future_df['temp_media_ultimos_dias'] = df['temp_media_ultimos_dias'].mean()
        future_df['precipitacao_acumulada'] = df['precipitacao_acumulada'].mean()

        X_future = future_df[features]
        future_predictions = model.predict(X_future)

        future_df['total_captura_previsto'] = future_predictions
        return future_df[['data_coleta', 'total_captura_previsto']]

    except Exception as e:
        st.error(f"Erro na previsão: {e}")
        return None

# Função para exibir a página de previsões no Streamlit
def pagina_previsoes():
    st.title("Previsão de Capturas de Moscas")

    # Configuração da conexão com o banco de dados
    engine = get_db_engine()

    # Carregamento dos dados
    df = load_data(engine)
    if df is None:
        return

    # Pré-processamento dos dados
    df = preprocess_data(df)
    if df is None:
        return


    model, features = train_model(df)  # Obter o modelo E as features
    if model is None:
        return

    # Número de dias para prever (configurável pelo usuário)
    days_to_predict = st.slider("Dias para Prever", min_value=1, max_value=365, value=60)

    # Previsões
    future_df = predict_future(model, df, features, days_to_predict)
    if future_df is None:
        return

    st.subheader(f"Previsão para os Próximos {days_to_predict} Dias")
    st.write(future_df)

    # Gráfico de previsões
    st.subheader("Gráfico de Previsões")
    fig = px.line(future_df, x='data_coleta', y='total_captura_previsto', title="Previsão de Capturas de Moscas")
    st.plotly_chart(fig)