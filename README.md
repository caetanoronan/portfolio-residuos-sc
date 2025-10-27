# 🌊 Portfolio - Análise Geoespacial de Resíduos Sólidos em Santa Catarina# 🗺️ Análise Geoespacial de Resíduos em Santa Catarina



[![GitHub Pages](https://img.shields.io/badge/GitHub-Pages-blue?logo=github)](https://caetanoronan.github.io/portfolio-residuos-sc/)[![GitHub Pages](https://img.shields.io/badge/GitHub-Pages-blue?logo=github)](https://SEU_USUARIO.github.io/portfolio-residuos-sc/)

[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)](https://www.python.org/)[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)](https://www.python.org/)

[![Accessibility](https://img.shields.io/badge/Acessibilidade-WCAG_2.1-green)](https://www.w3.org/WAI/)[![Accessibility](https://img.shields.io/badge/Acessibilidade-Daltonismo-green)](https://www.w3.org/WAI/)

[![Mobile First](https://img.shields.io/badge/Design-Mobile_First-orange)](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)

## 📋 Descrição

**Autor:** Ronan Armando Caetano  

**Instituição:** Universidade Federal de Santa Catarina (UFSC)  Análise espacial completa da geração de resíduos sólidos (domésticos e recicláveis) nos 295 municípios de Santa Catarina, utilizando dados do Censo 2022 e estimativas per capita. O projeto inclui mapas interativos com design acessível para pessoas com daltonismo.

**Desenvolvido com:** GitHub Copilot (IA)  

**Última Atualização:** Outubro 2025## 🎯 Objetivos



---- Estimar a geração de resíduos domésticos e recicláveis por setor censitário

- Visualizar dados espacialmente através de mapas interativos

## 📋 Sobre o Projeto- Fornecer análises agregadas por município

- Garantir acessibilidade visual para pessoas com daltonismo

Portfolio acadêmico de **análise geoespacial** para estimativa de geração de resíduos sólidos domésticos no estado de Santa Catarina, Brasil. Combina dados do **Censo Demográfico 2022 (IBGE)** com divisões territoriais por **bacias hidrográficas** para criar visualizações interativas acessíveis.

## 📊 Dados

### 🎯 Objetivos

- **Setores Censitários:** 16.831 setores de Santa Catarina (IBGE)

1. **Estimar** geração de resíduos sólidos por setor censitário (16.831 setores)- **População:** Projeções municipais via API IBGE

2. **Agregar** dados por município (295), região e bacia hidrográfica (8 macro-bacias)- **Estimativas:** 0.95 kg/hab/dia (doméstico), 10% reciclável

3. **Visualizar** através de mapas e dashboards interativos mobile-first

4. **Garantir** acessibilidade universal (daltonismo, WCAG 2.1)## 🛠️ Tecnologias

5. **Subsidiar** políticas públicas de gestão ambiental integrada

- **Python 3.13**

---- **GeoPandas** - Análise geoespacial

- **Folium** - Mapas interativos

## 🌟 Destaques do Projeto- **Pandas** - Manipulação de dados

- **Matplotlib** - Visualizações estáticas

### ✅ Análise por Bacias Hidrográficas

- **8 macro-bacias** mapeadas (Itajaí, Tubarão, Araranguá, Uruguai, Iguaçu, Itapocu, Tijucas, Outras)## 🚀 Como Usar

- **247 Ottobacias** (Nível 5 - ANA) integradas via ArcGIS REST API

- **2.638.892 toneladas/ano** de resíduos estimados### Pré-requisitos

- **7.610.361 habitantes** analisados

```bash

### ✅ Design Mobile-Firstpython -m venv .venv

- 📱 **Render sob demanda** - Gráficos carregam progressivamente.venv\Scripts\activate  # Windows

- 📱 **Modo compacto** automático em telas <768pxpip install geopandas matplotlib folium requests

- 📱 **Controles responsivos** - MiniMap/MeasureControl ocultos mobile```

- 📱 **Botão "Voltar ao topo"** flutuante

- 📱 **Tamanho otimizado** - Dashboard: 0,08 MB | Mapas: até 8 MB### Executar Análise



### ✅ Acessibilidade Universal```bash

- ♿ **ColorBrewer Set2** - Paleta de 8 cores seguras para daltonismo# Análise exploratória básica

- ♿ **Testado** com emulação Chrome DevTools (deuteranopia, protanopia, tritanopia)python analise_exploratoria/analise_dados_01.py

- ♿ **Touch targets** 44x44px mínimos

- ♿ **WCAG 2.1** - Alto contraste, legendas descritivas# Gerar mapas interativos

python "analise_exploratoria/crie_interactive_sector_maps.py)" --gpkg analise_exploratoria/SC_setores_CD2022.gpkg --out-dir analise_exploratoria/outputs

---```



## 📊 Principais Resultados## ♿ Acessibilidade



| Indicador | Valor |- ✅ Paletas seguras para daltonismo

|-----------|-------|- ✅ Alto contraste

| **População Total** | 7.610.361 habitantes |- ✅ Ícones e símbolos

| **Municípios** | 295 |- ✅ Legenda descritiva

| **Setores Censitários** | 16.831 |

| **Resíduos Totais** | 2.638.892 t/ano |## 🔗 Links

| **Geração Per Capita** | 0,95 kg/hab/dia |

| **Municípios Risco BAIXO** | 96,6% (285) |- 🌐 [Ver Mapa Interativo](https://SEU_USUARIO.github.io/portfolio-residuos-sc/analise_exploratoria/outputs/interactive_waste_map.html)

| **Bacias Hidrográficas** | 8 macro-bacias |- 📄 [Página do Projeto](https://SEU_USUARIO.github.io/portfolio-residuos-sc/)

| **Ottobacias (ANA)** | 247 microbacias |

---

---

Desenvolvido com 💙 como parte do portfólio de análise geoespacial

## 🗂️ Estrutura do Projeto

```
portfolio-residuos-sc/
├── README.md                          # 👈 Este arquivo
├── index.html                         # Página inicial GitHub Pages
├── GUIA_GITHUB_PAGES.md              # Instruções de deploy
│
├── .github/
│   └── copilot-instructions.md       # Padrões técnicos do projeto
│
└── analise_exploratoria/
    ├── README_BACIAS.md              # 📘 Documentação técnica completa
    ├── DATA_SOURCES.md               # Fontes de dados
    │
    ├── SC_setores_CD2022.gpkg        # 🗄️ Dados fonte (16.831 setores)
    │
    ├── data/                          # Geodados externos
    │   └── geoft_bho_ach_otto_nivel_05.gpkg  # Ottobacias ANA
    │
    ├── outputs/                       # 🎨 Visualizações geradas
    │   ├── dashboard_bacias.html     # Dashboard principal (0,08 MB)
    │   ├── mapa_bacias_hidrograficas.html  # Mapa bacias (8 MB)
    │   ├── relatorio_tecnico.html    # Relatório técnico
    │   ├── resumo_por_bacia.csv      # Estatísticas por bacia
    │   ├── analise_risco_municipios.csv  # Classificação risco
    │   └── *.gpkg                    # GeoPackages processados
    │
    └── scripts Python:
        ├── analise_bacias_hidrograficas.py  # Pipeline principal
        ├── dashboard_bacias.py         # Gerador dashboard (1288 linhas)
        ├── migrar_bacias_ana.py        # Download Ottobacias ANA (495 linhas)
        └── crie_interactive_sector_maps.py)  # Gerador mapas CLI
```

---

## 🌐 Visualizações Online

### 📊 Dashboard Interativo (Recomendado)
**[🔗 Dashboard - Análise por Bacias Hidrográficas](https://caetanoronan.github.io/portfolio-residuos-sc/analise_exploratoria/outputs/dashboard_bacias.html)**

6 gráficos interativos Plotly:
- Ranking de bacias por volume de resíduos
- Distribuição populacional
- Geração per capita vs população (scatter)
- Análise de risco municipal
- Comparação população vs resíduos
- Painel de indicadores-chave (KPIs)

**Mobile:** Carrega apenas KPIs + Gráfico 1, demais sob demanda via "Mostrar mais"

---

### 🗺️ Mapas Interativos

#### Mapa Principal - Bacias Hidrográficas + Ottobacias
**[🔗 Mapa das Bacias Hidrográficas](https://caetanoronan.github.io/portfolio-residuos-sc/analise_exploratoria/outputs/mapa_bacias_hidrograficas.html)**

- 8 macro-bacias com cores ColorBrewer Set2
- 247 Ottobacias (Nível 5 - ANA)
- Popups com estatísticas detalhadas
- Legenda interativa e responsiva
- Controles: Fullscreen, LocateControl, LayerControl (collapsed)

**Mobile:** MiniMap e MeasureControl ocultos automaticamente

---

#### Outros Mapas Disponíveis
- **[Mapa de Setores Censitários](https://caetanoronan.github.io/portfolio-residuos-sc/analise_exploratoria/outputs/interactive_waste_map.html)** - 16.831 setores
- **[Mapa por Município](https://caetanoronan.github.io/portfolio-residuos-sc/analise_exploratoria/outputs/mapa.html)** - 295 municípios
- **[Mapa por Região](https://caetanoronan.github.io/portfolio-residuos-sc/analise_exploratoria/outputs/mapa_regioes.html)** - Regiões geográficas

---

### 📄 Relatório Técnico
**[🔗 Relatório Técnico Completo](https://caetanoronan.github.io/portfolio-residuos-sc/analise_exploratoria/outputs/relatorio_tecnico.html)**

Documentação HTML com:
- Resumo executivo
- Metodologia detalhada
- Resultados e análises
- Limitações do estudo
- Referências bibliográficas

---

## 🛠️ Tecnologias Utilizadas

### Linguagem & Ambiente
- **Python 3.13** - Linguagem principal
- **VS Code** - IDE com GitHub Copilot
- **Git/GitHub** - Controle de versão
- **GitHub Pages** - Hospedagem web estática

### Bibliotecas Geoespaciais
```python
geopandas==0.14.x    # Análise de dados geoespaciais
shapely==2.0.x       # Manipulação de geometrias
fiona==1.9.x         # Leitura/escrita GIS
folium==0.15.x       # Mapas interativos (Leaflet.js)
```

### Bibliotecas de Visualização
```python
plotly==5.18.x       # Gráficos interativos responsivos
pandas==2.2.x        # Manipulação de dados tabulares
numpy==1.26.x        # Computação numérica
```

### Padrões de Design
- **Mobile-First** - Breakpoint 768px
- **Progressive Enhancement** - Renderização condicional
- **ColorBrewer Set2** - Paletas acessíveis
- **WCAG 2.1** - Acessibilidade web

---

## 📖 Metodologia

### 1. Fonte de Dados
- **Base:** Censo Demográfico 2022 (IBGE)
- **Geometrias:** 16.831 setores censitários
- **Sistema de Coordenadas:** SIRGAS 2000 / UTM 22S (EPSG:31982)
- **População:** API IBGE Projeções (fallback: Agregados 2022)

### 2. Cálculo de Resíduos
```
Taxa uniforme: 0,95 kg/habitante/dia

Resíduos (t/ano) = População × 0,95 × 365 ÷ 1000
```

**Nota:** Taxa estadual uniforme - não considera variações regionais, urbano/rural

### 3. Agregação Territorial
```python
# Pipeline padrão (GeoPandas)
1. Carregar setores censitários
2. Fetch população (IBGE API)
3. Calcular resíduos por setor
4. Dissolve por município/bacia/região
5. Gerar visualizações (Folium/Plotly)
```

### 4. Integração de Bacias Hidrográficas
- **Fonte:** ANA - Agência Nacional de Águas
- **Método:** ArcGIS REST API (dual-source: local file → API fallback)
- **Níveis:** Ottobacias Nível 5 (247 microbacias)
- **Atribuição:** Spatial join por área máxima de overlap

---

## 🚀 Como Usar Localmente

### Pré-requisitos

```powershell
# Clone o repositório
git clone https://github.com/caetanoronan/portfolio-residuos-sc.git
cd portfolio-residuos-sc

# Crie ambiente virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Instale dependências
pip install geopandas shapely fiona folium plotly pandas numpy requests
```

### Executar Análises

```powershell
# Ativar ambiente virtual
.venv\Scripts\activate

# Pipeline completo - Bacias Hidrográficas
python analise_exploratoria\analise_bacias_hidrograficas.py

# Dashboard interativo
python analise_exploratoria\dashboard_bacias.py

# Download Ottobacias ANA + mapa
python analise_exploratoria\migrar_bacias_ana.py

# Mapa de setores (CLI)
python "analise_exploratoria\crie_interactive_sector_maps.py)" --gpkg analise_exploratoria/SC_setores_CD2022.gpkg --out-dir analise_exploratoria/outputs
```

**Outputs:** Arquivos HTML gerados em `analise_exploratoria/outputs/`

---

## ♿ Compromisso com Acessibilidade

### Testes Realizados

✅ **Chrome DevTools → Rendering → Emulate vision deficiencies**
- Deuteranopia (daltonismo vermelho-verde)
- Protanopia (ausência de receptores vermelhos)
- Tritanopia (daltonismo azul-amarelo)

### Paleta ColorBrewer Set2 (8 cores)
```
#66c2a5  #fc8d62  #8da0cb  #e78ac3
#a6d854  #ffd92f  #e5c494  #b3b3b3
```

### Princípios Aplicados
- ✅ Contraste mínimo 4.5:1 (WCAG AA)
- ✅ Touch targets ≥ 44x44px
- ✅ Legendas descritivas textuais
- ✅ Navegação por teclado funcional
- ✅ Semântica HTML5 adequada

---

## 📚 Documentação Adicional

- **[📘 README_BACIAS.md](analise_exploratoria/README_BACIAS.md)** - Documentação técnica completa
- **[🔧 copilot-instructions.md](.github/copilot-instructions.md)** - Padrões de desenvolvimento
- **[📦 DATA_SOURCES.md](analise_exploratoria/DATA_SOURCES.md)** - Fontes de dados detalhadas
- **[🚀 GUIA_GITHUB_PAGES.md](GUIA_GITHUB_PAGES.md)** - Deploy no GitHub Pages

---

## ⚠️ Limitações do Estudo

1. **Taxa Uniforme:** 0,95 kg/hab/dia aplicada a todo estado (não considera variações regionais)
2. **Dados Agregados:** Setores censitários grandes podem mascarar variações internas
3. **Estimativas:** Valores calculados, não medições diretas de campo
4. **Temporalidade:** População base 2022 (projeções IBGE)
5. **Ottobacias:** Atribuição por área máxima pode gerar imprecisões em setores multi-bacia

**Uso recomendado:** Planejamento preliminar, priorização territorial, visualização de padrões espaciais

---

## 📚 Referências

### Dados
- **IBGE** - Instituto Brasileiro de Geografia e Estatística. *Censo Demográfico 2022*. Rio de Janeiro, 2023.
- **ANA** - Agência Nacional de Águas. *Divisão Hidrográfica Nacional - Ottobacias Nível 5*. Brasília, 2023.

### Legislação
- BRASIL. *Lei nº 12.305/2010* - Política Nacional de Resíduos Sólidos (PNRS)
- BRASIL. *Lei nº 9.433/1997* - Política Nacional de Recursos Hídricos

### Software & Bibliotecas
- Python Software Foundation. *Python 3.13*. https://www.python.org/
- Jordahl, K. et al. *GeoPandas 0.14*. https://geopandas.org/
- McKinney, W. *pandas 2.2*. https://pandas.pydata.org/
- Plotly Technologies. *Plotly 5.18*. https://plotly.com/python/
- ColorBrewer. *Color Advice for Maps*. https://colorbrewer2.org/

### Ferramentas de IA
- GitHub, Inc. *GitHub Copilot*. https://github.com/features/copilot

---

## 🤝 Contribuições

Este é um projeto educacional/acadêmico desenvolvido na UFSC. Sugestões, melhorias e feedback são bem-vindos!

**Como contribuir:**
1. Fork o repositório
2. Crie uma branch (`git checkout -b feature/melhoria`)
3. Commit suas mudanças (`git commit -m 'Adiciona funcionalidade X'`)
4. Push para a branch (`git push origin feature/melhoria`)
5. Abra um Pull Request

---

## 📧 Contato

**Ronan Armando Caetano**  
📧 Email: [Disponível no perfil GitHub]  
🐙 GitHub: [@caetanoronan](https://github.com/caetanoronan)  
🎓 Instituição: Universidade Federal de Santa Catarina (UFSC)

---

## 📄 Licença

Este projeto está disponível sob licença aberta para fins **educacionais e de pesquisa**.

**Citação sugerida:**
```
CAETANO, R. A. Análise Geoespacial de Resíduos Sólidos em Santa Catarina 
por Bacias Hidrográficas. Portfolio Acadêmico. Florianópolis: UFSC, 2025. 
Disponível em: https://github.com/caetanoronan/portfolio-residuos-sc
```

---

## 🙏 Agradecimentos

- **IBGE** - Pela disponibilização de dados censitários de qualidade
- **ANA** - Pelos dados hidrográficos via API pública
- **GitHub Copilot** - Assistência de IA no desenvolvimento
- **Comunidade open-source** - GeoPandas, Folium, Plotly
- **UFSC** - Apoio institucional

---

<div align="center">

**Desenvolvido com 💙 para o estado de Santa Catarina**  
*Análise Geoespacial de Resíduos Sólidos | Outubro 2025*

[![GitHub](https://img.shields.io/badge/GitHub-Portfolio-181717?logo=github)](https://github.com/caetanoronan/portfolio-residuos-sc)
[![Pages](https://img.shields.io/badge/GitHub-Pages-222222?logo=github)](https://caetanoronan.github.io/portfolio-residuos-sc/)

</div>
