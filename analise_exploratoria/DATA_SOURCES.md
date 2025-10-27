# Fontes de Dados - Portfolio Resíduos SC

Este documento lista as fontes oficiais dos arquivos de dados grandes (>100 MB) que não podem ser incluídos diretamente no repositório Git.

## Arquivos Necessários para Reproduzir as Análises

### 1. SC_setores_CD2022.gpkg (115 MB)
**Descrição:** Setores censitários de Santa Catarina do Censo 2022 com dados populacionais  
**Fonte Oficial:** IBGE - Censo Demográfico 2022  
**Download Direto:**
- **Portal IBGE:** https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais/26565-malhas-de-setores-censitarios-divisoes-intramunicipais.html
- **FTP IBGE:** https://geoftp.ibge.gov.br/recortes_para_fins_estatisticos/malha_de_setores_censitarios/censo_2022/
- Selecione: `Santa Catarina (SC)` → Formato `GeoPackage`

**Como processar:**
```python
# O arquivo baixado do IBGE precisa ser renomeado para:
# SC_setores_CD2022.gpkg
# E colocado em: analise_exploratoria/SC_setores_CD2022.gpkg
```

### 2. geoft_bho_ach_otto_nivel_05.gpkg (1.096 MB)
**Descrição:** Ottobacias Nível 5 da ANA (Agência Nacional de Águas e Saneamento Básico)  
**Fonte Oficial:** ANA - Sistema de Informações Hidrológicas  
**Download Direto:**
- **Portal ANA:** https://metadados.snirh.gov.br/geonetwork/srv/por/catalog.search#/metadata/542c18b0-79ad-44ff-830b-bae211ab70cc
- **GeoServicos ANA (API REST):** https://geoservicos.ana.gov.br/arcgis/rest/services/BASES/OTTOBACIAS/MapServer

**Alternativa - Script Automatizado:**
O script `migrar_bacias_ana.py` baixa automaticamente via API se o arquivo não existir localmente:
```bash
python analise_exploratoria/migrar_bacias_ana.py
```

**Como usar:**
```python
# Após download, coloque em: analise_exploratoria/data/geoft_bho_ach_otto_nivel_05.gpkg
# O script detectará automaticamente o arquivo local antes de tentar a API
```

### 3. sectors_with_waste_estimates.gpkg (116 MB)
**Descrição:** Arquivo GERADO pelos scripts - setores censitários com estimativas de resíduos  
**Fonte:** Processamento local a partir de `SC_setores_CD2022.gpkg`  
**Como gerar:**
```bash
# Execute o script de análise exploratória:
python analise_exploratoria/analise_exploratoria.py
# OU
python analise_exploratoria/analise_bacias_hidrograficas.py

# O arquivo será criado automaticamente em: analise_exploratoria/outputs/
```

**Conteúdo:** Todos os setores censitários com campos calculados:
- `residuos_domesticos_t_ano` - Resíduos domésticos (toneladas/ano)
- `residuos_reciclaveis_t_ano` - Resíduos recicláveis (toneladas/ano)
- Taxa per capita utilizada: **0.95 kg/hab/dia**

### 4. ottobacias_sc_atribuida.gpkg (65.68 MB)
**Descrição:** Arquivo GERADO - Ottobacias de SC com atribuição às 8 macro-bacias hidrográficas  
**Fonte:** Processamento via `migrar_bacias_ana.py`  
**Como gerar:**
```bash
python analise_exploratoria/migrar_bacias_ana.py
```

**Conteúdo:** Ottobacias com campo `macro_bacia` indicando pertencimento a:
- Bacia do Rio Iguaçu
- Bacia do Rio Itajaí
- Bacia do Rio Tubarão
- Bacia do Rio Uruguai
- Bacia Litorânea Norte
- Bacia Litorânea Centro
- Bacia Litorânea Sul
- Outras Bacias

## Arquivo Incluído no Repositório

### ✅ bacias_oficiais_ana_macro.gpkg (0.28 MB)
**Descrição:** 8 macro-bacias hidrográficas de SC (geometrias simplificadas)  
**Localização:** `analise_exploratoria/outputs/bacias_oficiais_ana_macro.gpkg`  
**Status:** ✅ Incluído no Git (tamanho adequado)

Este arquivo contém as geometrias agregadas e simplificadas das bacias principais, usado nos mapas finais.

## Ordem Recomendada de Download

Para reproduzir as análises do zero:

1. **Baixar do IBGE:** `SC_setores_CD2022.gpkg` (fonte primária - dados populacionais)
2. **Executar:** `migrar_bacias_ana.py` (baixa Ottobacias da ANA via API)
3. **Executar:** `analise_bacias_hidrograficas.py` (gera estimativas de resíduos)
4. **Executar:** `dashboard_bacias.py` (gera visualizações finais)

## Configuração do .gitignore

Os arquivos grandes já estão excluídos do Git via `.gitignore`:
```gitignore
# Arquivos grandes de dados
*.gpkg
!bacias_oficiais_ana_macro.gpkg  # Exceção para o arquivo pequeno
```

## Suporte

Para problemas com downloads ou dúvidas sobre as fontes:
- **IBGE:** https://www.ibge.gov.br/atendimento.html
- **ANA:** https://www.gov.br/ana/pt-br/assuntos/servicos-e-atendimento
- **Issues do projeto:** https://github.com/caetanoronan/portfolio-residuos-sc/issues

---

**Última atualização:** Outubro 2025  
**Autor:** Caetano Ronan  
**Licença:** Os dados são de domínio público (IBGE/ANA). O código do projeto segue a licença do repositório.
