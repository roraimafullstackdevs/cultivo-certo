import random
import pandas as pd
from datetime import datetime, timedelta
import string
import geopy.geocoders
from geopy.geocoders import Nominatim
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
from time import sleep
from sqlalchemy import create_engine
from sqlalchemy.types import Date, Time

geolocator = Nominatim(user_agent="geo_app")

from weather_api import get_openmeteo_data

def gerar_coordenadas_aleatorias(municipio, coordenadas_dict, num_coordenadas=1):
    try:
        if municipio not in coordenadas_dict:
            print(f"Município não encontrado no dicionário: {municipio}")
            return []

        latitude, longitude = coordenadas_dict[municipio]

        raio = 0.1

        coordenadas = []
        for _ in range(num_coordenadas):
            lat_aleatoria = random.uniform(latitude - raio, latitude + raio)
            lon_aleatoria = random.uniform(longitude - raio, longitude + raio)
            coordenadas.append((lat_aleatoria, lon_aleatoria))

        return coordenadas

    except Exception as e:
        print(f"Erro ao gerar coordenadas para {municipio}: {e}")
        return []

def random_string(length=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def random_name():
    first_names = ["João", "Maria", "José", "Ana", "Paulo", "Juliana", "Carlos", "Patrícia", "Antônio", "Lucas"]
    last_names = ["Silva", "Souza", "Oliveira", "Santos", "Pereira", "Costa", "Rodrigues", "Almeida"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"

def random_date(start, end):
    delta = end - start
    int_delta = delta.days
    random_day = random.randrange(int_delta)
    return start + timedelta(days=random_day)

def random_time():
    return f"{random.randint(8, 17):02}:{random.randint(0, 59):02}"

tecnicos = [random_name() for _ in range(20)]

roraima_cidades = {
    "Boa Vista": (2.846118, -60.717620),
    "Rorainópolis": (0.939066, -60.433802),
    "Caracaraí": (1.821933, -61.133069),
    "Alto Alegre": (2.988025, -61.308563),
    "Mucajaí": (2.449871, -60.929298)
}

# Função para gerar os dados
def gerar_dados(index):
    cidade = random.choice(list(roraima_cidades.keys()))
    la_lo = gerar_coordenadas_aleatorias(cidade, roraima_cidades)
    latitude = la_lo[0][0]
    longitude = la_lo[0][1]
    tecnico = random.choice(tecnicos)
    tipo_armadilha = random.choice(["Jackson", "McPhail"])
    total_captura = random.randint(0, 10) 
    acao_tomada = random.sample(
        ["Determinar perímetro de quarentena", "Controle Mecânico",
         "Controle Biológico", "Controle Químico", "Coleta de Amostras"],
        k=random.randint(1, 3)
    )
    data_coleta = random_date(datetime(2020, 1, 1), datetime(2024, 11, 7)).date()
    hora_coleta = random_time()

    climate_data = get_openmeteo_data(latitude, longitude, data_coleta - timedelta(days=7), data_coleta)
    
    temp_media_ultimos_dias = climate_data["avg_temperature_mean"]
    temp_max_ultimo_dias = climate_data["avg_temperature_max"]
    temp_min_ultimos_dias = climate_data["avg_temperature_min"]
    precipitacao_acumulada = climate_data["avg_rain_sum"]

    tipo_de_isca = random.choice(["Metil eugenol", "Cue-lure"])
    tempo_exposição_armadilha = random.randint(4, 15)
    tipo_ambiente = random.choice(["Pomar Comercial", "Quintal Residencial", "Área Silvestre"])

    if tipo_ambiente == "Pomar Comercial":
        proximidade_arvores_frutiferas = True
    else:
        proximidade_arvores_frutiferas = random.choice([True, False])

    if proximidade_arvores_frutiferas:
        hospedeiros = random.choice(["Primário", "Secundário"])
    else:
        hospedeiros = random.choice(["Primário", "Secundário", "Nenhum"])

    return [
        cidade, tecnico, tipo_armadilha, total_captura, 
        latitude, longitude, ','.join(acao_tomada), data_coleta, hora_coleta,
        temp_media_ultimos_dias, temp_max_ultimo_dias, temp_min_ultimos_dias,
        precipitacao_acumulada, tipo_de_isca, tempo_exposição_armadilha,
        tipo_ambiente, proximidade_arvores_frutiferas, hospedeiros
    ]

num_records = 100000
batch_size = 900
columns = [
    "cidade", "tecnico", "tipo_armadilha", "total_captura", 
    "latitude", "longitude", "acao_tomada", "data_coleta",
    "hora_coleta", "temp_media_ultimos_dias", "temp_max_ultimo_dias",
    "temp_min_ultimos_dias", "precipitacao_acumulada", "tipo_de_isca",
    "tempo_exposição_armadilha", "tipo_ambiente",
    "proximidade_arvores_frutiferas", "hospedeiros"
]

# Configurações da conexão com o banco de dados PostgreSQL
host = 'localhost'
db = 'expoferr'
user = 'postgres'
password = '123456'
port = '5432'

# Cria uma conexão usando o SQLAlchemy
engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

# Nome da tabela onde os dados serão inseridos
nome_da_tabela = 'dados_coleta'
    
    
df_list = []
with ProcessPoolExecutor() as executor:
    for i in range(0, num_records, batch_size):
        end = min(num_records, i + batch_size)
        batch_futures = [executor.submit(gerar_dados, index) for index in range(i, end)]
        for future in tqdm(as_completed(batch_futures), total=len(batch_futures), desc="Gerando dados"):
            df_list.append(future.result())
        
        # Converte a lista de dados do batch atual em um DataFrame
        batch_df = pd.DataFrame(df_list, columns=columns)
        
        # Insere o DataFrame do batch atual no banco de dados
        try:
            batch_df.to_sql(nome_da_tabela, engine, if_exists='append', index=False, dtype={'data_coleta': Date(), 'hora_coleta': Time()})
            print("Dados do batch inseridos com sucesso!")
        except Exception as e:
            print(f"Ocorreu um erro ao inserir os dados do batch: {e}")
        
        # Limpa a lista df_list para o próximo batch
        df_list.clear()
        
        if end != num_records:
            print("Aguardando 1 minuto para evitar sobrecarga de solicitações...")
            sleep(60)