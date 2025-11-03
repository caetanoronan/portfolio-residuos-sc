# 🌊 API Resíduos SC - Guia Rápido

## 📋 Sumário

- [API REST](#-api-rest-pública) - Acesse os dados programaticamente
- [Deploy](#-deploy) - Hospede sua própria instância
- [Autenticação](#-autenticação-opcional) - Proteja sua API
- [Monitoramento](#-monitoramento) - Mantenha tudo funcionando

---

## 🚀 API REST Pública

### Endpoints Principais

```bash
# Health Check
GET https://api-residuos-sc.onrender.com/health

# Listar Municípios
GET https://api-residuos-sc.onrender.com/api/v1/municipios

# Detalhes de Florianópolis
GET https://api-residuos-sc.onrender.com/api/v1/municipios/4205407

# Listar Bacias Hidrográficas
GET https://api-residuos-sc.onrender.com/api/v1/bacias

# Swagger UI (Documentação Interativa)
https://api-residuos-sc.onrender.com/docs
```

### Documentação Completa
📖 [README_API.md](README_API.md) - Guia completo da API

---

## 🏗️ Deploy

### Opção 1: Render.com (Recomendado)
```bash
1. Fork este repositório
2. Conecte ao Render.com
3. Deploy automático via render.yaml
```

### Opção 2: Deploy Local
```bash
# Instalar dependências
pip install -r requirements-api.txt

# Rodar API
uvicorn api.main:app --reload --port 8000

# Acessar
http://localhost:8000/docs
```

### Guias Detalhados
- 📄 [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md) - Guia completo (Render, Railway, Fly.io)
- 🎨 [DEPLOY_INTERATIVO.html](DEPLOY_INTERATIVO.html) - Guia visual interativo

---

## 🔐 Autenticação (Opcional)

### Configuração

```bash
# .env
API_KEYS_ENABLED=true
API_KEYS=chave-secreta-1,chave-secreta-2
```

### Uso

```bash
# Com API Key
curl -H "X-API-Key: chave-secreta-1" \
     https://api-residuos-sc.onrender.com/api/v1/municipios

# Python
import requests

headers = {"X-API-Key": "chave-secreta-1"}
response = requests.get(
    "https://api-residuos-sc.onrender.com/api/v1/municipios",
    headers=headers
)
```

### Documentação
📄 [api/auth.py](api/auth.py) - Implementação completa  
📄 [api/.env.example](api/.env.example) - Exemplo de configuração

---

## 📊 Monitoramento

### UptimeRobot (Gratuito)
```
✅ 288 verificações/dia (5 min)
✅ Alertas por email
✅ Status page pública
✅ Evita cold starts
```

### Configuração Rápida
```bash
1. Criar conta: https://uptimerobot.com/signUp
2. Add Monitor → HTTP(s)
3. URL: https://api-residuos-sc.onrender.com/health
4. Intervalo: 5 minutos
```

### Guia Completo
📄 [MONITORING_GUIDE.md](MONITORING_GUIDE.md) - Monitoramento avançado

---

## 📦 Estrutura do Projeto

```
portfolio-residuos-sc/
├── api/                              # 🚀 API REST
│   ├── main.py                      # FastAPI app principal
│   ├── auth.py                      # Sistema de API Keys (opcional)
│   ├── config.py                    # Configurações
│   ├── models.py                    # Schemas Pydantic
│   ├── database.py                  # Conexão GeoPackage
│   └── endpoints/                   # Rotas da API
│       ├── municipios.py            # 295 municípios
│       ├── bacias.py                # 8 macro-bacias
│       └── setores.py               # 16.831 setores
├── tests/                           # 🧪 Testes automatizados (20+)
│   ├── test_municipios.py
│   ├── test_bacias.py
│   └── test_geral.py
├── analise_exploratoria/            # 📊 Scripts de análise
│   ├── SC_setores_CD2022.gpkg       # Dados Censo 2022
│   ├── outputs/                     # Mapas e dashboards
│   └── *.py                         # Scripts Python
├── apresentacao.html                # 🎨 Apresentação do projeto
├── README_API.md                    # 📖 Documentação API
├── DEPLOY_GUIDE.md                  # 🚀 Guia de deploy
├── DEPLOY_INTERATIVO.html           # 🎨 Deploy visual
├── MONITORING_GUIDE.md              # 📊 Guia de monitoramento
├── requirements-api.txt             # 📦 Dependências API
├── render.yaml                      # ⚙️ Config Render.com
├── Procfile                         # ⚙️ Comando startup
└── .python-version                  # 🐍 Python 3.13.0
```

---

## 🛠️ Tecnologias

### Backend
- **FastAPI 0.104.1** - Framework web moderno
- **Uvicorn 0.24.0** - ASGI server
- **Pydantic 2.5.0** - Validação de dados

### Geoespacial
- **GeoPandas 0.14.1** - Análise espacial
- **Shapely 2.0.2** - Geometrias
- **Fiona 1.9.5** - Leitura de GeoPackage

### Testing
- **Pytest 7.4.3** - Framework de testes
- **FastAPI TestClient** - Testes de API

### Deploy
- **Render.com** - Hospedagem (free tier)
- **UptimeRobot** - Monitoramento (free)

---

## 🚀 Quick Start

### 1. Clonar Repositório
```bash
git clone https://github.com/caetanoronan/portfolio-residuos-sc.git
cd portfolio-residuos-sc
```

### 2. Instalar Dependências
```bash
pip install -r requirements-api.txt
```

### 3. Rodar API
```bash
uvicorn api.main:app --reload
```

### 4. Acessar Docs
```
http://localhost:8000/docs
```

### 5. Testar Endpoint
```bash
curl http://localhost:8000/health
```

---

## 🧪 Testes

```bash
# Rodar todos os testes
pytest tests/ -v

# Teste específico
pytest tests/test_municipios.py -v

# Com coverage
pytest --cov=api tests/
```

---

## 📝 Licença

MIT License - Uso livre para fins acadêmicos e pesquisa.

---

## 👨‍💻 Autor

**Ronan Armando Caetano**  
Graduando em Ciências Biológicas - UFSC  
Técnico em Geoprocessamento - IFSC

📧 caetanoronan@example.com  
🔗 [GitHub](https://github.com/caetanoronan)

---

## 🤖 Desenvolvido com GitHub Copilot

Este projeto foi desenvolvido com auxílio de inteligência artificial (GitHub Copilot).

---

## 📚 Documentação Adicional

- [README_BACIAS.md](analise_exploratoria/README_BACIAS.md) - Análise de bacias hidrográficas
- [DATA_SOURCES.md](analise_exploratoria/DATA_SOURCES.md) - Fontes de dados
- [README_API.md](README_API.md) - API completa
- [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md) - Deploy detalhado
- [MONITORING_GUIDE.md](MONITORING_GUIDE.md) - Monitoramento avançado

---

## 🎯 Status do Projeto

✅ **API REST** - Funcional e documentada  
✅ **11 Endpoints** - Municípios, bacias, setores  
✅ **20+ Testes** - Cobertura automatizada  
✅ **Deploy Config** - Pronto para produção  
✅ **Autenticação** - Opcional com API Keys  
✅ **Monitoramento** - UptimeRobot configurado  
✅ **Documentação** - Swagger UI + guias completos

---

**Última atualização:** Novembro 2025
