"""
Configurações da API
Paths, constantes e configurações gerais
"""

import os
from pathlib import Path

# Diretórios
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "analise_exploratoria"
GPKG_PATH = DATA_DIR / "SC_setores_CD2022.gpkg"

# Validar se arquivo existe
if not GPKG_PATH.exists():
    raise FileNotFoundError(
        f"GeoPackage não encontrado: {GPKG_PATH}\n"
        "Certifique-se de que o arquivo SC_setores_CD2022.gpkg está em analise_exploratoria/"
    )

# Taxas e constantes
TAXA_PER_CAPITA_KG_DIA = 0.95  # ABRELPE 2022
DIAS_POR_ANO = 365

# Cache (em memória para desenvolvimento)
CACHE_ENABLED = True
CACHE_TTL_SECONDS = 3600  # 1 hora

# CORS
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://caetanoronan.github.io",
    "*"  # Em produção, remover * e especificar domínios
]

# Informações da API
API_TITLE = "API Resíduos SC"
API_VERSION = "1.0.0"
API_DESCRIPTION = "API REST para análise de resíduos sólidos em Santa Catarina"
CONTACT_EMAIL = "caetanoronan@example.com"
GITHUB_URL = "https://github.com/caetanoronan/portfolio-residuos-sc"

# Host e Porta (para desenvolvimento local)
API_HOST = "0.0.0.0"
API_PORT = 8000
