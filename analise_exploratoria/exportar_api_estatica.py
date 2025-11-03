"""
Exporta uma "API estática" para o GitHub Pages (docs/api/v1)
Sem dependências externas: usa apenas csv/json/os.

Fontes de dados:
- outputs/analise_risco_municipios.csv
- analise_exploratoria/outputs/resumo_por_bacia.csv

Gera:
- docs/api/v1/stats.json
- docs/api/v1/municipios.json
- docs/api/v1/bacias.json

Observações:
- Deduplicação por município: mantém a primeira ocorrência por nome (linhas repetidas no CSV são ignoradas)
- Taxa per capita padronizada do projeto: 0.95 kg/hab/dia
"""
from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from collections import OrderedDict

BASE = Path(__file__).resolve().parents[1]
DOCS_API = BASE / "docs" / "api" / "v1"
DOCS_API.mkdir(parents=True, exist_ok=True)

CSV_MUN = BASE / "outputs" / "analise_risco_municipios.csv"
CSV_BACIA = BASE / "analise_exploratoria" / "outputs" / "resumo_por_bacia.csv"

TAXA_PER_CAPITA_KG_DIA = 0.95


def _clean_key(key: str) -> str:
    # Remove BOM, espaços e mantém o caso original (colunas vêm em maiúsculas)
    return key.lstrip("\ufeff").strip()


def ler_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        cleaned_rows = []
        for row in reader:
            cleaned = { _clean_key(k): v for k, v in row.items() }
            cleaned_rows.append(cleaned)
        return cleaned_rows


def parse_float(v):
    try:
        return float(v)
    except Exception:
        return None


def exportar_municipios(rows: list[dict]) -> list[dict]:
    vistos = set()
    municipios = []
    for r in rows:
        nome = r.get("NM_MUN")
        if not nome or nome in vistos:
            continue
        vistos.add(nome)
        municipios.append({
            "nome": nome,
            "bacia": r.get("bacia"),
            "populacao": parse_float(r.get("populacao")),
            "residuos_domestico_t_ano": parse_float(r.get("domestico_t_ano")),
            "residuos_reciclavel_t_ano": parse_float(r.get("reciclavel_t_ano")),
            "risco": r.get("risco"),
        })
    return sorted(municipios, key=lambda x: (x["nome"] or ""))


def exportar_bacias(rows: list[dict]) -> list[dict]:
    bacias = []
    for r in rows:
        bacias.append({
            "bacia": r.get("bacia"),
            "populacao": parse_float(r.get("populacao")),
            "residuos_domestico_t_ano": parse_float(r.get("domestico_t_ano")),
            "residuos_reciclavel_t_ano": parse_float(r.get("reciclavel_t_ano")),
        })
    return bacias


def salvar_json(path: Path, data: dict | list):
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    if not CSV_MUN.exists():
        raise FileNotFoundError(f"Não encontrado: {CSV_MUN}")
    if not CSV_BACIA.exists():
        raise FileNotFoundError(f"Não encontrado: {CSV_BACIA}")

    mun_rows = ler_csv(CSV_MUN)
    bac_rows = ler_csv(CSV_BACIA)

    municipios = exportar_municipios(mun_rows)
    bacias = exportar_bacias(bac_rows)

    total_municipios = len(municipios)
    total_populacao = sum((m.get("populacao") or 0) for m in municipios)
    total_domestico = sum((m.get("residuos_domestico_t_ano") or 0) for m in municipios)
    total_reciclavel = sum((m.get("residuos_reciclavel_t_ano") or 0) for m in municipios)

    stats = OrderedDict([
        ("estado", "Santa Catarina"),
        ("sigla", "SC"),
        ("municipios", total_municipios),
        ("populacao", round(total_populacao)),
        ("residuos_totais_ton_ano", round(total_domestico, 2)),
        ("residuos_reciclaveis_ton_ano", round(total_reciclavel, 2)),
        ("residuos_per_capita_kg_dia", TAXA_PER_CAPITA_KG_DIA),
        ("fonte", "CSV gerados pelo pipeline do portfólio"),
        ("observacao", "Valores agregados; sem geometrias. API estática para GitHub Pages."),
    ])

    salvar_json(DOCS_API / "municipios.json", {"total": total_municipios, "municipios": municipios})
    salvar_json(DOCS_API / "bacias.json", {"total": len(bacias), "bacias": bacias})
    salvar_json(DOCS_API / "stats.json", stats)

    # Índice simples
    salvar_json(DOCS_API / "index.json", {
        "endpoints": [
            "/api/v1/stats.json",
            "/api/v1/municipios.json",
            "/api/v1/bacias.json",
        ]
    })

    print("✅ API estática exportada em docs/api/v1/")


if __name__ == "__main__":
    main()
