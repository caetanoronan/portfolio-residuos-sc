# 🌊 Análise de Resíduos Sólidos por Bacias Hidrográficas - Santa Catarina

## 📋 Sobre o Projeto

Este projeto apresenta uma análise exploratória detalhada da geração de resíduos sólidos domésticos no estado de Santa Catarina, utilizando dados do Censo Demográfico 2022 do IBGE e organizados por bacias hidrográficas.

**👤 Autor:** Ronan Armando Caetano  
**📅 Data:** Outubro de 2025  
**🎯 Objetivo:** Subsidiar políticas públicas de gestão ambiental através de visualizações interativas e análises territoriais integradas.

## 🎯 Principais Resultados

- 📊 **7.610.361** habitantes analisados
- 🏛️ **295** municípios classificados
- 🌊 **8** bacias hidrográficas mapeadas
- ♻️ **2.638.892** toneladas/ano de resíduos estimados
- ⚠️ **96,6%** dos municípios em risco BAIXO

## 📂 Estrutura do Projeto

```
analise_exploratoria/
├── analise_bacias_hidrograficas.py    # Pipeline completo de análise
├── dashboard_bacias.py                # Geração do dashboard interativo (1288 linhas)
├── migrar_bacias_ana.py              # Pipeline ANA Ottobacias (495 linhas)
├── relatorio_tecnico.html             # Relatório técnico completo
├── SC_setores_CD2022.gpkg            # Dados censitários (16.831 setores)
└── outputs/
    ├── dashboard_bacias.html          # Dashboard com 6 gráficos (0,08 MB)
    ├── mapa_bacias_hidrograficas.html # Mapa interativo (8 MB, 247 Ottobacias)
    ├── relatorio_tecnico.html         # Documentação técnica
    ├── resumo_por_bacia.csv          # Estatísticas por bacia
    ├── analise_risco_municipios.csv  # Classificação de risco
    ├── bacias_oficiais_ana_macro.gpkg # 8 macro-bacias (0,28 MB)
    ├── ottobacias_sc_atribuida.gpkg  # 247 Ottobacias classificadas
    └── sectors_with_waste_estimates.gpkg # GeoPackage completo
```

## 🗺️ Visualizações Disponíveis

### 1. Dashboard Interativo
**Arquivo:** `outputs/dashboard_bacias.html`

Contém 6 gráficos interativos Plotly:
- 📊 **Gráfico 1:** Ranking de bacias por volume de resíduos
- 👥 **Gráfico 2:** Distribuição populacional por bacia
- 📈 **Gráfico 3:** Geração per capita vs população (scatter)
- ⚠️ **Gráfico 4:** Análise de risco municipal (barras agrupadas + percentual)
- 🔄 **Gráfico 5:** Comparação população vs resíduos
- 🎯 **Gráfico 6:** Painel de indicadores-chave

**Otimizações Mobile:**
- ✅ Modo compacto automático em dispositivos móveis (<768px)
- ✅ Renderização sob demanda: Gráficos 2-6 carregam apenas após clicar em "Mostrar mais"
- ✅ Botão "Voltar ao topo" flutuante (aparece após rolar 300px)
- ✅ Toggle de modo compacto para desktop (demonstração/acessibilidade)
- ✅ Margens otimizadas e fontes reduzidas para telas pequenas
- ✅ Tamanho final: **0,08 MB** (extremamente leve)

### 2. Mapa das Bacias Hidrográficas
**Arquivo:** `outputs/mapa_bacias_hidrograficas.html`

Mapa coroplético interativo com:
- Polígonos das 8 bacias hidrográficas
- Tooltips com nome da bacia
- Popups com estatísticas detalhadas
- Legenda com códigos de cores

**Otimizações Mobile:**
- ✅ Controles MiniMap e MeasureControl ocultos em telas <768px
- ✅ LayerControl colapsado por padrão (interface mais limpa)
- ✅ Legenda responsiva com altura máxima de 40vh no mobile
- ✅ Cores ColorBrewer Set2: seguras para daltonismo (deuteranopia, protanopia, tritanopia)
- ✅ Geometrias simplificadas (tolerância 100m) - redução significativa de tamanho
- ✅ Tamanho final: **8 MB** (247 Ottobacias incluídas)

### 3. Relatório Técnico
**Arquivo:** `outputs/relatorio_tecnico.html`

Documentação completa incluindo:
- Resumo executivo
- Metodologia detalhada
- Resultados e análises
- Limitações do estudo
- Referências bibliográficas completas

## 🛠️ Tecnologias Utilizadas

### Linguagem
- **Python 3.13** - Linguagem principal

### Bibliotecas de Dados
- **Pandas 2.2.x** - Manipulação de dados tabulares
- **NumPy 1.26.x** - Computação numérica

### Bibliotecas Geoespaciais
- **GeoPandas 0.14.x** - Análise de dados geoespaciais
- **Shapely 2.0.x** - Manipulação de geometrias
- **Fiona 1.9.x** - Leitura/escrita de formatos GIS
- **Folium 0.15.x** - Mapas interativos web (Leaflet.js)

### Bibliotecas de Visualização
- **Plotly 5.18.x** - Gráficos interativos responsivos
- **ColorBrewer** - Paletas seguras para daltonismo

### Acessibilidade & UX
- **Mobile-first design** - Breakpoint 768px
- **Progressive enhancement** - Renderização condicional
- **WCAG 2.1 compliance** - Contraste adequado, touch targets 44x44px
- **Colorblind-safe palettes** - Testado com Chrome DevTools emulation

### Ferramentas de Desenvolvimento
- **Visual Studio Code** - IDE
- **Git/GitHub** - Controle de versão
- **GitHub Pages** - Hospedagem web
- **GitHub Copilot** - Assistência de IA para código

## 📊 Metodologia

### Fonte de Dados
- **Base:** Censo Demográfico 2022 (IBGE)
- **Arquivo:** SC_setores_CD2022.gpkg
- **Setores:** 16.831 setores censitários
- **Sistema de Coordenadas:** SIRGAS 2000 / UTM Zone 22S (EPSG:31982)

### Cálculo de Resíduos
```
Resíduos (t/ano) = População × 0,95 kg/hab/dia × 365 dias ÷ 1000
Geração Per Capita = 346,75 kg/hab/ano (uniforme para todo o estado)
Taxa de Reciclagem = 10% do total doméstico
```

### Classificação de Risco
- 🔴 **CRÍTICO:** > 100.000 t/ano
- 🟠 **ALTO:** 50.000 - 100.000 t/ano
- 🟡 **MÉDIO:** 10.000 - 50.000 t/ano
- 🟢 **BAIXO:** < 10.000 t/ano

## 🚀 Como Usar

### 1. Visualizar Online
Acesse os arquivos HTML diretamente pelo GitHub Pages:
```
https://caetanoronan.github.io/portfolio-residuos-sc/analise_exploratoria/outputs/dashboard_bacias.html
https://caetanoronan.github.io/portfolio-residuos-sc/analise_exploratoria/outputs/mapa_bacias_hidrograficas.html
https://caetanoronan.github.io/portfolio-residuos-sc/analise_exploratoria/outputs/relatorio_tecnico.html
```

### 2. Executar Localmente

**Requisitos:**
- Python 3.10+
- pip

**Instalação:**
```bash
# Clone o repositório
git clone https://github.com/caetanoronan/portfolio-residuos-sc.git
cd portfolio-residuos-sc/analise_exploratoria

# Crie ambiente virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Instale dependências
pip install pandas geopandas plotly folium shapely fiona

# Execute as análises
python analise_bacias_hidrograficas.py
python dashboard_bacias.py

# Abra os arquivos HTML gerados em outputs/
```

## 📈 Principais Bacias

| Bacia | População | Resíduos (t/ano) | % do Estado |
|-------|-----------|------------------|-------------|
| Outras Bacias | 3.586.011 | 1.243.449 | 47,1% |
| Litorânea Central | 1.129.756 | 391.743 | 14,8% |
| Itajaí | 859.149 | 297.910 | 11,3% |
| Litorânea Norte | 714.274 | 247.675 | 9,4% |
| Uruguai | 468.550 | 162.470 | 6,2% |
| Tubarão | 455.538 | 157.958 | 6,0% |
| Canoas | 227.852 | 79.008 | 3,0% |
| Rio do Peixe | 169.231 | 58.681 | 2,2% |

## ⚠️ Limitações

1. **Taxa Uniforme:** Todos os municípios usam 0,95 kg/hab/dia - não captura variações regionais
2. **Dados Estimados:** Baseado em população, não em coleta real
3. **Agregação "Outras Bacias":** Agrupa múltiplas bacias menores
4. **Análise Estática:** Snapshot de 2022, sem séries temporais
5. **Escopo:** Apenas resíduos domésticos (não inclui comerciais, industriais, etc.)

## 📚 Referências

### Dados
- IBGE - Instituto Brasileiro de Geografia e Estatística. **Censo Demográfico 2022**. Rio de Janeiro: IBGE, 2023.
- ANA - Agência Nacional de Águas. **Divisão Hidrográfica Nacional**. Brasília: ANA, 2023.

### Legislação
- BRASIL. **Lei nº 12.305/2010** - Política Nacional de Resíduos Sólidos
- BRASIL. **Lei nº 9.433/1997** - Política Nacional de Recursos Hídricos

### Software
- Python Software Foundation. **Python 3.13**. https://www.python.org/
- Jordahl, K. et al. **GeoPandas 0.14**. https://geopandas.org/
- McKinney, W. **pandas 2.2**. https://pandas.pydata.org/
- Plotly Technologies. **Plotly 5.18**. https://plotly.com/python/

### IA Assistiva
- GitHub, Inc. **GitHub Copilot**. https://github.com/features/copilot

## 🤝 Contribuições

Este é um projeto educacional/acadêmico. Sugestões e melhorias são bem-vindas!

## 📧 Contato

**Ronan Armando Caetano**  
GitHub: [@caetanoronan](https://github.com/caetanoronan)

## 📄 Licença

Este projeto está disponível sob licença aberta para fins educacionais e de pesquisa.

---

**Desenvolvido com 💙 para o estado de Santa Catarina**  
*Análise de Resíduos Sólidos por Bacias Hidrográficas | Outubro 2025*
