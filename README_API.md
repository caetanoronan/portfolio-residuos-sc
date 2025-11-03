# 🌊 API REST - Resíduos Sólidos Santa Catarina

**API pública para consulta de dados de geração de resíduos sólidos em Santa Catarina, organizada por municípios e bacias hidrográficas.**

## 📋 Visão Geral

Esta API fornece acesso programático aos dados do projeto **Análise Geoespacial de Resíduos Sólidos em SC**, permitindo consultas via HTTP/REST para:

- **295 municípios** de Santa Catarina
- **16.831 setores censitários** (Censo 2022)
- **8 macro-bacias hidrográficas**
- **247 Ottobacias** (ANA - Nível 5)

### 🎯 Casos de Uso

- Integração com dashboards externos
- Aplicações mobile/web de gestão ambiental
- Análises customizadas em Python/R/JavaScript
- Projetos acadêmicos e pesquisas
- Sistemas municipais de planejamento

---

## 🚀 Início Rápido

### 1️⃣ Instalação

```powershell
# Ativar ambiente virtual (se existir)
.venv\Scripts\activate

# Instalar dependências
pip install -r requirements-api.txt
```

### 2️⃣ Executar API

```powershell
# Opção 1: Usando Uvicorn diretamente
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Opção 2: Executar o script Python
python -m api.main
```

### 3️⃣ Acessar Documentação Interativa

Após iniciar a API, abra no navegador:

- **Swagger UI** (recomendado): http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Root**: http://localhost:8000/

---

## 📡 Endpoints Disponíveis

### 🏠 **Informações Gerais**

#### `GET /`
Página inicial com informações da API

```bash
curl http://localhost:8000/
```

#### `GET /health`
Health check - verifica se API está ativa

```bash
curl http://localhost:8000/health
```

#### `GET /api/v1/stats`
Estatísticas consolidadas de Santa Catarina

```bash
curl http://localhost:8000/api/v1/stats
```

**Resposta:**
```json
{
  "estado": "Santa Catarina",
  "populacao": 7600524,
  "municipios": 295,
  "setores_censitarios": 16831,
  "residuos_totais_ton_ano": 2649378,
  "residuos_per_capita_kg_dia": 0.95
}
```

---

### 🏙️ **Municípios**

#### `GET /api/v1/municipios`
Lista todos os 295 municípios de SC

**Parâmetros Query:**
- `limit` (opcional): Limitar número de resultados (1-295)
- `offset` (opcional): Pular N primeiros resultados (paginação)

**Exemplo:**
```bash
# Listar primeiros 10 municípios
curl "http://localhost:8000/api/v1/municipios?limit=10&offset=0"
```

**Resposta:**
```json
{
  "total": 295,
  "municipios": [
    {
      "codigo_ibge": "4200051",
      "nome": "Abdon Batista",
      "sigla_uf": "SC"
    },
    ...
  ]
}
```

#### `GET /api/v1/municipios/{codigo_ibge}`
Detalhes de um município específico

**Exemplo:**
```bash
# Florianópolis
curl http://localhost:8000/api/v1/municipios/4205407
```

**Resposta:**
```json
{
  "codigo_ibge": "4205407",
  "nome": "Florianópolis",
  "sigla_uf": "SC",
  "area_km2": 675.41,
  "setores_censitarios": 312,
  "centroide": {
    "latitude": -27.5954,
    "longitude": -48.5480
  },
  "bounding_box": {
    "min_lat": -27.8493,
    "max_lat": -27.3117,
    "min_lon": -48.5776,
    "max_lon": -48.3556
  }
}
```

#### `GET /api/v1/municipios/{codigo_ibge}/residuos`
Estimativa de resíduos de um município

**Exemplo:**
```bash
# Resíduos de Florianópolis
curl http://localhost:8000/api/v1/municipios/4205407/residuos
```

**Resposta:**
```json
{
  "codigo_ibge": "4205407",
  "nome": "Florianópolis",
  "sigla_uf": "SC",
  "area_km2": 675.41,
  "residuos": {
    "populacao": 537211,
    "taxa_per_capita_kg_dia": 0.95,
    "residuos_kg_dia": 510350.45,
    "residuos_ton_ano": 186277.91
  }
}
```

---

## 🐍 Exemplos de Integração

### Python (Requests)

```python
import requests

# Listar municípios
response = requests.get('http://localhost:8000/api/v1/municipios')
municipios = response.json()['municipios']

for mun in municipios[:5]:
    print(f"{mun['nome']} - {mun['codigo_ibge']}")

# Obter resíduos de Florianópolis
floripa = requests.get('http://localhost:8000/api/v1/municipios/4205407/residuos')
dados = floripa.json()

print(f"\n{dados['nome']}")
print(f"População: {dados['residuos']['populacao']:,}")
print(f"Resíduos/ano: {dados['residuos']['residuos_ton_ano']:,.2f} toneladas")
```

### JavaScript (Fetch)

```javascript
// Listar municípios
fetch('http://localhost:8000/api/v1/municipios')
  .then(response => response.json())
  .then(data => {
    console.log(`Total: ${data.total} municípios`);
    data.municipios.slice(0, 5).forEach(mun => {
      console.log(`${mun.nome} - ${mun.codigo_ibge}`);
    });
  });

// Obter resíduos de Florianópolis
fetch('http://localhost:8000/api/v1/municipios/4205407/residuos')
  .then(response => response.json())
  .then(dados => {
    console.log(`\n${dados.nome}`);
    console.log(`População: ${dados.residuos.populacao.toLocaleString()}`);
    console.log(`Resíduos/ano: ${dados.residuos.residuos_ton_ano.toLocaleString()} toneladas`);
  });
```

### R (httr + jsonlite)

```r
library(httr)
library(jsonlite)

# Listar municípios
response <- GET("http://localhost:8000/api/v1/municipios")
municipios <- fromJSON(content(response, "text", encoding = "UTF-8"))

head(municipios$municipios)

# Obter resíduos de Florianópolis
floripa <- GET("http://localhost:8000/api/v1/municipios/4205407/residuos")
dados <- fromJSON(content(floripa, "text", encoding = "UTF-8"))

cat(paste0("\n", dados$nome, "\n"))
cat(paste0("População: ", format(dados$residuos$populacao, big.mark = ","), "\n"))
cat(paste0("Resíduos/ano: ", format(dados$residuos$residuos_ton_ano, big.mark = ","), " toneladas\n"))
```

---

## 📦 Estrutura do Projeto

```
api/
├── __init__.py           # Inicialização do pacote
├── main.py               # FastAPI app principal (rodar este arquivo)
├── config.py             # Configurações (paths, constantes)
├── models.py             # Schemas Pydantic (validação de dados)
├── database.py           # Conexão com GeoPackage + queries
├── endpoints/
│   ├── __init__.py
│   ├── municipios.py     # Rotas de municípios
│   └── bacias.py         # Rotas de bacias (futuro)
└── utils/
    ├── __init__.py
    └── calculations.py   # Cálculos de resíduos
```

---

## 🛠️ Desenvolvimento

### Adicionar Novo Endpoint

1. Criar arquivo em `api/endpoints/meu_endpoint.py`
2. Definir router:
```python
from fastapi import APIRouter
router = APIRouter()

@router.get("/meu-endpoint")
async def minha_funcao():
    return {"message": "Funcionou!"}
```

3. Registrar no `main.py`:
```python
from api.endpoints import meu_endpoint
app.include_router(meu_endpoint.router, prefix="/api/v1", tags=["Minha Tag"])
```

### Executar Testes

```powershell
# Instalar pytest
pip install pytest httpx

# Executar testes (criar depois)
pytest tests/
```

---

## 🌐 Deploy na Nuvem

### Opção 1: **Render.com** (Recomendado - Grátis)

1. Criar conta em https://render.com
2. Conectar repositório GitHub
3. Criar novo **Web Service**
4. Configurações:
   - **Build Command**: `pip install -r requirements-api.txt`
   - **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3.13
5. Deploy automático!

**URL final**: `https://seu-app.onrender.com`

### Opção 2: **Railway.app** (Grátis + Fácil)

```bash
# Instalar Railway CLI
npm install -g railway

# Login
railway login

# Deploy
railway up
```

### Opção 3: **Fly.io** (Grátis até 3 apps)

```bash
# Instalar Fly CLI
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"

# Login
fly auth login

# Deploy
fly launch
```

---

## 📊 Metodologia

### Fonte de Dados
- **IBGE Censo 2022**: População por setor censitário
- **ANA Ottobacias**: Divisão hidrográfica oficial (Nível 5)
- **ABRELPE 2022**: Taxa per capita de 0,95 kg/hab/dia

### Cálculo de Resíduos
```
Resíduos (t/ano) = População × 0,95 kg/hab/dia × 365 dias ÷ 1000
```

### Limitações
- Taxa uniforme (não considera variação urbano/rural)
- Dados de 2022 (snapshot temporal)
- Não detalha composição gravimétrica (orgânicos vs recicláveis)

---

## 📝 Licença

**MIT License** - Dados públicos para uso acadêmico e pesquisa.

---

## 👨‍💻 Autor

**Ronan Armando Caetano**
- Graduando em Ciências Biológicas - UFSC
- Técnico em Geoprocessamento - IFSC
- GitHub: [@caetanoronan](https://github.com/caetanoronan)
- Portfólio: https://caetanoronan.github.io/portfolio-residuos-sc/

---

## 🤝 Contribuições

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Commit: `git commit -m "Feat: adiciona nova funcionalidade"`
4. Push: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

---

## 📧 Suporte

- **Issues**: https://github.com/caetanoronan/portfolio-residuos-sc/issues
- **Documentação**: http://localhost:8000/docs (Swagger UI)
- **Email**: caetanoronan@example.com

---

**Desenvolvido com ❤️ e GitHub Copilot (IA)**
