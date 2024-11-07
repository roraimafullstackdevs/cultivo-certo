import streamlit as st
import plotly.express as px
import pandas as pd
import psycopg2
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


def pagina_analise_dados():
    st.title("Análise de Dados")

    # Configuração da conexão
    engine = get_db_engine()
    df = load_data(engine)

    st.write("DataFrame carregado do banco de dados:")
    st.dataframe(df)
    
    # Adicionar filtros interativos
    st.sidebar.title("Filtros")
    
    cidades = df['cidade'].unique()
    cidade_selecionada = st.sidebar.multiselect("Selecione a Cidade:", cidades, default=cidades)

    tipos_armadilha = df['tipo_armadilha'].unique()
    tipo_armadilha_selecionado = st.sidebar.multiselect("Selecione o Tipo de Armadilha:", tipos_armadilha, default=tipos_armadilha)

    tipos_ambiente = df['tipo_ambiente'].unique()
    tipo_ambiente_selecionado = st.sidebar.multiselect("Selecione o Tipo de Ambiente:", tipos_ambiente, default=tipos_ambiente)

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

    df['data_coleta'] = pd.to_datetime(df['data_coleta']).dt.date

    df_filtrado = df[
        (df['cidade'].isin(cidade_selecionada)) &
        (df['tipo_armadilha'].isin(tipo_armadilha_selecionado)) &
        (df['tipo_ambiente'].isin(tipo_ambiente_selecionado)) &
        (df['data_coleta'] >= data_inicio) &
        (df['data_coleta'] <= data_fim)
    ]
    
    # Gráfico de Barras
    st.subheader("Gráfico de Barras")
    fig_bar = px.bar(df_filtrado, x='cidade', y='total_captura', color='tipo_armadilha', title="Total de Capturas por Cidade e Tipo de Armadilha")
    st.plotly_chart(fig_bar)
    
    # Gráfico de Pizza
    st.subheader("Gráfico de Pizza")
    fig_pie = px.pie(df_filtrado, names='cidade', values='total_captura', title="Distribuição de Capturas por Cidade")
    st.plotly_chart(fig_pie)
    
    # Médias e Estatísticas
    st.subheader("Estatísticas Descritivas")
    
    media_capturas = df_filtrado['total_captura'].mean()
    mediana_capturas = df_filtrado['total_captura'].median()
    desvio_padrao_capturas = df_filtrado['total_captura'].std()
    minimo_capturas = df_filtrado['total_captura'].min()
    maximo_capturas = df_filtrado['total_captura'].max()
    
    st.write(f"Média das capturas: {media_capturas}")
    st.write(f"Mediana das capturas: {mediana_capturas}")
    st.write(f"Desvio padrão das capturas: {desvio_padrao_capturas}")
    st.write(f"Valor mínimo das capturas: {minimo_capturas}")
    st.write(f"Valor máximo das capturas: {maximo_capturas}")
    
    # Histograma
    st.subheader("Histograma")
    fig_hist = px.histogram(df_filtrado, x='total_captura', nbins=10, title="Histograma das Capturas")
    st.plotly_chart(fig_hist)
    
    # Box Plot
    st.subheader("Box Plot")
    fig_box = px.box(df_filtrado, y='total_captura', title="Box Plot das Capturas")
    st.plotly_chart(fig_box)
    
    # Tabela de Estatísticas Descritivas
    st.subheader("Tabela de Estatísticas Descritivas")
    estatisticas_descritivas = df_filtrado['total_captura'].describe()
    st.write(estatisticas_descritivas)

