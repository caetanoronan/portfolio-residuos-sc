# 🗺️ Análise Geoespacial de Resíduos em Santa Catarina

[![GitHub Pages](https://img.shields.io/badge/GitHub-Pages-blue?logo=github)](https://SEU_USUARIO.github.io/portfolio-residuos-sc/)
[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)](https://www.python.org/)
[![Accessibility](https://img.shields.io/badge/Acessibilidade-Daltonismo-green)](https://www.w3.org/WAI/)

## 📋 Descrição

Análise espacial completa da geração de resíduos sólidos (domésticos e recicláveis) nos 295 municípios de Santa Catarina, utilizando dados do Censo 2022 e estimativas per capita. O projeto inclui mapas interativos com design acessível para pessoas com daltonismo.

## 🎯 Objetivos

- Estimar a geração de resíduos domésticos e recicláveis por setor censitário
- Visualizar dados espacialmente através de mapas interativos
- Fornecer análises agregadas por município
- Garantir acessibilidade visual para pessoas com daltonismo

## 📊 Dados

- **Setores Censitários:** 16.831 setores de Santa Catarina (IBGE)
- **População:** Projeções municipais via API IBGE
- **Estimativas:** 0.95 kg/hab/dia (doméstico), 10% reciclável

## 🛠️ Tecnologias

- **Python 3.13**
- **GeoPandas** - Análise geoespacial
- **Folium** - Mapas interativos
- **Pandas** - Manipulação de dados
- **Matplotlib** - Visualizações estáticas

## 🚀 Como Usar

### Pré-requisitos

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install geopandas matplotlib folium requests
```

### Executar Análise

```bash
# Análise exploratória básica
python analise_exploratoria/analise_dados_01.py

# Gerar mapas interativos
python "analise_exploratoria/crie_interactive_sector_maps.py)" --gpkg analise_exploratoria/SC_setores_CD2022.gpkg --out-dir analise_exploratoria/outputs
```

## ♿ Acessibilidade

- ✅ Paletas seguras para daltonismo
- ✅ Alto contraste
- ✅ Ícones e símbolos
- ✅ Legenda descritiva

## 🔗 Links

- 🌐 [Ver Mapa Interativo](https://SEU_USUARIO.github.io/portfolio-residuos-sc/analise_exploratoria/outputs/interactive_waste_map.html)
- 📄 [Página do Projeto](https://SEU_USUARIO.github.io/portfolio-residuos-sc/)

---

Desenvolvido com 💙 como parte do portfólio de análise geoespacial
