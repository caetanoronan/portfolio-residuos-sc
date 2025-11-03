"""
API REST - Análise Geoespacial de Resíduos Sólidos em Santa Catarina
Autor: Ronan Armando Caetano
Graduando em Ciências Biológicas - UFSC | Técnico em Geoprocessamento - IFSC
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os

# Importar routers
from api.endpoints import municipios, bacias, setores
from api.auth import get_auth_info, is_auth_enabled

# Metadata da API
app = FastAPI(
    title="API Resíduos SC",
    description="""
    ## 🌊 API REST para Análise de Resíduos Sólidos em Santa Catarina
    
    Esta API fornece acesso programático aos dados de geração de resíduos sólidos 
    em Santa Catarina, organizados por:
    - **Municípios** (295)
    - **Bacias Hidrográficas** (8 macro-bacias + 247 Ottobacias)
    - **Setores Censitários** (16.831 setores - Censo 2022)
    
    ### 📊 Fonte de Dados
    - IBGE Censo 2022
    - ANA - Agência Nacional de Águas (Ottobacias)
    - Estimativas: 0,95 kg/hab/dia (ABRELPE)
    
    ### 🚀 Tecnologias
    - FastAPI + Uvicorn
    - GeoPandas + Shapely
    - GeoPackage (.gpkg)
    
    ### 📝 Licença
    Dados públicos - Uso livre para fins acadêmicos e pesquisa
    """,
    version="1.0.0",
    contact={
        "name": "Ronan Armando Caetano",
        "url": "https://github.com/caetanoronan/portfolio-residuos-sc",
        "email": "caetanoronan@example.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc (alternativa ao Swagger)
)

# Configurar CORS para permitir acesso público
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rota raiz - Informações da API
@app.get("/", tags=["Informações"])
async def root():
    """
    **Página inicial da API**
    
    Retorna informações básicas e links úteis.
    """
    return {
        "message": "🌊 API Resíduos SC - Análise Geoespacial",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "endpoints": {
            "municipios": "/api/v1/municipios",
            "bacias": "/api/v1/bacias",
            "estatisticas": "/api/v1/stats"
        },
        "autor": "Ronan Armando Caetano",
        "github": "https://github.com/caetanoronan/portfolio-residuos-sc"
    }

# Health Check
@app.get("/health", tags=["Informações"])
async def health_check():
    """
    **Health Check**
    
    Verifica se a API está funcionando corretamente.
    """
    auth_info = get_auth_info()
    return {
        "status": "healthy",
        "message": "API está funcionando! ✅",
        "version": "1.0.0",
        "autenticacao": auth_info["modo"],
        "ambiente": os.getenv("ENVIRONMENT", "development")
    }

# Status da API (informações detalhadas)
@app.get("/api/v1/status", tags=["Informações"])
async def api_status():
    """
    **Status Detalhado da API**
    
    Retorna informações sobre configuração, autenticação e recursos disponíveis.
    """
    auth_info = get_auth_info()
    return {
        "api": {
            "nome": "API Resíduos SC",
            "versao": "1.0.0",
            "ambiente": os.getenv("ENVIRONMENT", "development"),
            "status": "online"
        },
        "autenticacao": {
            "habilitada": auth_info["autenticacao_habilitada"],
            "modo": auth_info["modo"],
            "instrucoes": "Inclua header 'X-API-Key: sua-chave' se autenticação habilitada" if auth_info["autenticacao_habilitada"] else "API pública - sem autenticação necessária"
        },
        "recursos": {
            "municipios": 295,
            "bacias": 8,
            "setores": 16831
        },
        "cache": {
            "habilitado": os.getenv("CACHE_ENABLED", "true").lower() == "true",
            "tipo": "lru_cache (memória)"
        },
        "cors": {
            "origens_permitidas": os.getenv("ALLOWED_ORIGINS", "*")
        },
        "documentacao": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json"
        }
    }

# Estatísticas Gerais de Santa Catarina
@app.get("/api/v1/stats", tags=["Estatísticas"])
async def get_statistics():
    """
    **Estatísticas Gerais de Santa Catarina**
    
    Retorna números consolidados do estado:
    - População total
    - Municípios
    - Setores censitários
    - Estimativa total de resíduos (t/ano)
    - Bacias hidrográficas
    """
    return {
        "estado": "Santa Catarina",
        "sigla": "SC",
        "populacao": 7600524,
        "municipios": 295,
        "setores_censitarios": 16831,
        "residuos_totais_ton_ano": 2649378,
        "residuos_per_capita_kg_dia": 0.95,
        "macro_bacias": 8,
        "ottobacias_nivel_5": 247,
        "fonte_dados": {
            "censo": "IBGE Censo 2022",
            "bacias": "ANA - Ottobacias Nível 5",
            "taxa_residuos": "ABRELPE 2022"
        }
    }

# Incluir routers
app.include_router(municipios.router, prefix="/api/v1", tags=["Municípios"])
app.include_router(bacias.router, prefix="/api/v1", tags=["Bacias Hidrográficas"])
app.include_router(setores.router, prefix="/api/v1", tags=["Setores Censitários"])

# Executar com: uvicorn api.main:app --reload
if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",  # Permite acesso externo
        port=8000,
        reload=True  # Auto-reload em desenvolvimento
    )
