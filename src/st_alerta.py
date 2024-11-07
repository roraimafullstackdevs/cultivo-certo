import streamlit as st
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine
import os
from datetime import datetime, timedelta


def get_db_engine():
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_name = os.getenv('DB_NAME')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')

    db_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(db_url)
    return engine


def load_data(engine):
    with engine.connect() as conn:
        query = "SELECT * FROM dados_coleta"
        df = pd.read_sql_query(query, conn)
    return df


def pagina_alertas():
    st.title("Alertas e Previsões")

    # Configuração da conexão
    engine = get_db_engine()
    df = load_data(engine)

    # Adicionar filtros interativos
    st.sidebar.title("Filtros")
    
    # Filtro de data
    st.sidebar.subheader("Filtro de Data")
    
    data_max = datetime.today().date()
    data_min_inicial = data_max - timedelta(days=60)
    data_min = data_max - timedelta(days=120)

    data_inicio, data_fim = st.sidebar.date_input(
        "Selecione o intervalo de datas:",
        value=[data_min_inicial, data_max],
        min_value=data_min,
        max_value=data_max,
        key="date_range"
    )

    # Converter a coluna 'data_coleta' para datetime
    df['data_coleta'] = pd.to_datetime(df['data_coleta']).dt.date

    df_filtrado = df[
        (df['data_coleta'] >= data_inicio) &
        (df['data_coleta'] <= data_fim)
    ]
    
    # Parâmetros de alerta
    capita_min = st.sidebar.slider("Número Mínimo de Capturas para Alerta", min_value=0, max_value=100, value=10)
    temperatura_min = st.sidebar.slider("Temperatura Mínima para Alerta", min_value=-10.0, max_value=50.0, value=10.0)
    
    # Verificar condições para gerar alertas e previsões
    alerta_capturas = not df_filtrado[df_filtrado['total_captura'] > capita_min].empty
    alerta_temp = not df_filtrado[df_filtrado['temp_min_ultimos_dias'] < temperatura_min].empty

    # Mostrar alertas
    st.subheader("Indicadores de Alerta")

    if alerta_capturas:
        st.error(f"Alerta: Capturas acima do limite ({capita_min}) detectadas nas últimas coletas!")

    if alerta_temp:
        st.error(f"Alerta: Temperaturas abaixo do limite detectadas ({temperatura_min}°C) nas últimas coletas!")

    if not alerta_capturas and not alerta_temp:
        st.success("Nenhum alerta detectado.")

    # Gráfico de Capturas ao Longo do Tempo
    st.subheader("Gráfico de Capturas com Indicadores de Alerta")
    fig = px.scatter(df_filtrado, x='data_coleta', y='total_captura', color='cidade',
                     title="Capturas ao Longo do Tempo")
    st.plotly_chart(fig)

    
