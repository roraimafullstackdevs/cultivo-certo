from dotenv import load_dotenv

from google.oauth2 import service_account
from langchain_openai import AzureChatOpenAI
from langchain_google_vertexai import ChatVertexAI, HarmBlockThreshold, HarmCategory
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


import logging
import os
import pprint

# Load variables
load_dotenv()

# Use logger
logger = logging.getLogger(__name__)

# Force the Load Google Credentials
credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
credentials = service_account.Credentials.from_service_account_file(credentials_path)


# Load database
def load_db():
    try:
        db_uri = f'postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}'
        
        # # Crie o engine de conexão
        # engine = create_engine(db_uri)
        
        # # Crie uma sessão
        # Session = sessionmaker(bind=engine)
        # session = Session()
        
        db = SQLDatabase.from_uri(db_uri)
        return db
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco de dados: {e}")

        


def load_context():
    try:
        with open('files/context.txt', 'r', encoding='utf-8') as f:
            template = f.read()
            return template
    except FileNotFoundError:
        logger.error("Arquivo context.txt não encontrado.")        
    except Exception as e:
        logger.error(f"Erro ao ler o arquivo context.txt: {e}")
        
    
class ModelsLoad():
    # Carrega o modelo da LLM Google
    def load_llm_vertex():
        try:
            model = ChatVertexAI(
                model_name="gemini-1.5-flash-002", 
                temperature=1,
                max_tokens=8192,
                max_retries=6,
                stop=None,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                },
                streaming=True
            )
            logger.info("Modelo Gemini configurado com sucesso.")
            return model
        except Exception as e:
            logger.error(f"Erro ao configurar modelo: {e}")
            return None
        
    def load_llm_azure():
        try:
            llm = AzureChatOpenAI(
                temperature=1,
                max_retries=3, 
                streaming=True, 
                max_tokens=2000,
                verbose=True
                )       
            
            logger.info("Modelo AZURE configurado com sucesso.")
            return llm
        except Exception as e:
            logger.error(f"Erro ao configurar modelo Azure: {e}")
            return None
        

def agente_alive():
    try:
        llm = ModelsLoad.load_llm_azure()
        
        db = load_db()
        
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)

        sql_tools = toolkit.get_tools()

        #pprint.pprint(sql_tools)

        template = load_context()
        
        # prompt_template = ChatPromptTemplate.from_template(template)
        prompt_template = SystemMessage(content=template)
        
        #formated_prompt = prompt_template.format(input="PostgreSQL", top_k=5)

        sql_agent = create_react_agent(llm, sql_tools, state_modifier=prompt_template)
        
        return sql_agent
    
    except Exception as e:
        logger.error(f"Erro ao configurar agente: {e}")
        return None

def few_shot():
    try:
        
        examples = [
            {"input": "2+2", "output": "4"},
            {"input": "2+3", "output": "5"},
        ]

        example_prompt = ChatPromptTemplate.from_messages(
            [('human', '{input}'), ('ai', '{output}')]
        )

        few_shot_prompt = FewShotChatMessagePromptTemplate(
            examples=examples,
            # This is a prompt template used to format each individual example.
            example_prompt=example_prompt,
        )

        final_prompt = ChatPromptTemplate.from_messages(
            [
                ('system', 'You are a helpful AI Assistant'),
                few_shot_prompt,
                ('human', '{input}'),
            ]
        )
        final_prompt.format(input="What is 4+4?")
        
    except Exception as e:
        logger.error(f"Erro ao configurar agente: {e}")
        return None


        