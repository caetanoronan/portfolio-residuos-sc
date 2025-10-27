# Copilot Instructions - Portfolio Resíduos SC

## Project Overview
Geospatial analysis portfolio for solid waste generation in Santa Catarina, Brazil. Processes Census 2022 data (16,831 sectors, 295 municipalities) to create **accessible**, **colorblind-safe** interactive maps and dashboards using watershed (bacia hidrográfica) boundaries.

**Key Outputs:** Folium web maps, Plotly dashboards, GeoPackage datasets, technical reports (all in Brazilian Portuguese)

## Architecture & Data Flow

### Core Data Pipeline Pattern
All analysis scripts follow this 5-stage pipeline:

1. **Load Census Data** → `SC_setores_CD2022.gpkg` (16,831 polygons with SIRGAS 2000 / UTM 22S, EPSG:31982)
2. **Fetch Population** → IBGE API (primary: projeções, fallback: agregados Censo 2022)
3. **Calculate Waste** → Uniform rate: 0.95 kg/hab/day × 365 days ÷ 1000 = t/year
4. **Aggregate** → Group by município/bacia/região using spatial dissolve
5. **Visualize** → Folium map + Plotly dashboard → `outputs/` directory

**Example:** See `analise_bacias_hidrograficas.py` (lines 1-250) for canonical implementation.

### Directory Structure
```
analise_exploratoria/
├── SC_setores_CD2022.gpkg        # Source: 16,831 census sectors (NEVER modify)
├── data/                          # External geodata (Ottobacias from ANA)
│   └── geoft_bho_ach_otto_nivel_05.gpkg  # Optional local file for ANA watersheds
├── outputs/                       # Generated artifacts (HTML, CSV, GPKG)
│   ├── *.html                    # Web maps & dashboards (public-facing)
│   ├── *.csv                     # Summary tables (resumo_por_bacia.csv, etc.)
│   └── *.gpkg                    # Processed geodata (sectors_with_waste_estimates.gpkg)
├── migrar_bacias_ana.py          # NEW: Downloads ANA Ottobacias via ArcGIS REST API
├── analise_bacias_hidrograficas.py  # Main analysis script (8 watersheds)
├── dashboard_bacias.py           # Plotly dashboard generator (6 charts)
└── crie_interactive_sector_maps.py) # Reusable map generator with CLI
```

**Convention:** Scripts write to `outputs/`, NEVER overwrite source `SC_setores_CD2022.gpkg`.

## Critical Developer Workflows

### Running Analysis Scripts
```powershell
# Always activate venv first (if available)
.venv\Scripts\activate

# Standard run pattern (most scripts are standalone)
python analise_exploratoria\analise_bacias_hidrograficas.py
python analise_exploratoria\dashboard_bacias.py
python analise_exploratoria\migrar_bacias_ana.py

# CLI-based scripts (created for reusability)
python "analise_exploratoria\crie_interactive_sector_maps.py)" --gpkg SC_setores_CD2022.gpkg --out-dir outputs
```

**No tests exist.** Validation is manual via browser inspection of generated HTML maps.

### Fetching External Geodata (NEW Pattern)
`migrar_bacias_ana.py` introduces **dual-source pattern** for Ottobacias:
1. **Local file first:** Checks `data/` for `.gpkg`, `.geojson`, `.shp`, `.zip` (shapefile), `.fgb`
2. **API fallback:** ArcGIS REST API (layers 0-6) with bbox clip to SC bounds
3. **Spatial join:** Assigns each Ottobacia to 1 of 8 macro-bacias by max area overlap

**Why?** ANA API is unreliable. Always include fallback to local files.

### Git Workflow
```powershell
# Task exists for committing migrar_bacias_ana.py
# Pattern: git add → commit with "Infra:" prefix → push to main
git add analise_exploratoria/migrar_bacias_ana.py
git commit -m "Infra: adiciona migrar_bacias_ana.py (pipeline para bacias oficiais ANA via ArcGIS REST)"
git push origin main
```

**Convention:** Commit messages in Portuguese, use prefixes: `Infra:`, `Feat:`, `Fix:`, `docs:`

## Project-Specific Conventions

### Accessibility is NON-NEGOTIABLE
**Every** visualization MUST be colorblind-safe:
- **Watershed boundaries:** ColorBrewer Set2 palette (8 qualitative colors: #66c2a5, #fc8d62, #8da0cb, #e78ac3, #a6d854, #ffd92f, #e5c494, #b3b3b3)
- **Domestic waste:** Blue gradient (`#d0d1e6` → `#034e7b`) - safe for all types
- **Recyclable waste:** Yellow→Orange (`#ffffcc` → `#e31a1c`) - high contrast
- **Risk levels:** `#d32f2f` (critical), `#f57c00` (high), `#fbc02d` (medium), `#388e3c` (low)

**Testing:** Chrome DevTools → Rendering → Emulate vision deficiencies (deuteranopia, protanopia, tritanopia)

**Implementation:** See `crie_interactive_sector_maps.py` (lines 180-220) for HeatMap gradient configs.

### Geospatial Patterns
1. **Always use EPSG:4326 (WGS84) for final maps** - Folium requirement
2. **Perform operations in projected CRS** (EPSG:3857 or native EPSG:31982) - accuracy
3. **Simplify geometries before export** - `simplify(100)` in EPSG:3857 reduces HTML size
4. **Use `dissolve(by='field', aggfunc='sum')` for aggregation** - GeoPandas best practice

**Example (from `migrar_bacias_ana.py` lines 290-295):**
```python
# Project → Simplify → Reproject pattern
bo_3857 = bacias_official.to_crs(3857)
bo_3857['geometry'] = bo_3857.geometry.simplify(100)  # ~100m tolerance
bacias_official = bo_3857.to_crs(4326)
```

### Folium Map Patterns
**Standard Controls Configuration:**
- **LayerControl:** `collapsed=True, position='topleft'` - mobile-friendly
- **MiniMap:** Hidden on mobile via CSS (`.leaflet-control-minimap { display: none; }` @ max-width: 768px)
- **MeasureControl:** Hidden on mobile (same CSS pattern)
- **MousePosition:** `position='topright'` - desktop only
- **Fullscreen:** Always visible
- **LocateControl:** Always visible

**Legend Injection (CRITICAL):**
```python
# CORRECT method - injects into <html> element
m.get_root().html.add_child(folium.Element(legend_html))

# WRONG method - breaks rendering
# m.get_root().add_child(folium.Element(legend_html))  # ❌ Don't use
```

**Mobile CSS Pattern:**
```css
@media (max-width: 768px) {
  .leaflet-control-minimap,
  .leaflet-control-measure { display: none; }
  
  .legend-bacias {
    max-height: 40vh;
    overflow-y: auto;
  }
}
```

### IBGE API Usage
**Pattern:** Try primary API → Fallback to alternative → Last resort: aggregate from sectors

```python
# Primary: https://servicodados.ibge.gov.br/api/v1/projecoes/populacao/municipios
# Fallback: https://servicodados.ibge.gov.br/api/v3/agregados/4714/periodos/2022/variaveis/93
# Last resort: gdf.groupby('CD_MUN')[pop_field].sum()
```

**Why 3 tiers?** IBGE APIs frequently timeout or return 500 errors.

### HTML Output Standards
All dashboards follow this structure:
1. **Header:** Gradient background (`linear-gradient(135deg, #1976d2 0%, #0d47a1 100%)`)
2. **Stats grid:** `<div class="stats-grid">` with 8 KPI cards
3. **Charts:** Plotly with `responsive: true`, mobile-friendly margins
4. **Footer:** Credits, data sources, GitHub link, "Desenvolvido com GitHub Copilot (IA)"

**Mobile-First Patterns (NEW):**
- **Render-on-demand:** Charts 2-6 hidden on mobile by default, loaded via "Mostrar mais" button
- **Progressive enhancement:** Desktop loads all charts immediately; mobile defers heavy content
- **Compact mode toggle:** Desktop has checkbox to force compact view (demo capability)
- **Back-to-top button:** Floating button appears after 300px scroll, smooth behavior
- **Mobile breakpoint:** `@media (max-width: 768px)` for all responsive overrides
- **Touch-friendly:** Minimum 44x44px touch targets, adequate spacing

**Implementation (see `dashboard_bacias.py` lines 870-1306):**
```javascript
// Conditional rendering pattern
const isMobile = window.innerWidth <= 768;
if (!isMobile && !forceCompact) {
  renderMoreCharts(); // Desktop: load all charts
} else {
  // Mobile: render on button click
  document.getElementById('more-toggle').addEventListener('click', renderMoreCharts);
}
```

## Integration Points

### External APIs
- **IBGE Projeções:** Population projections (7-digit IBGE codes)
- **IBGE Agregados:** Census 2022 raw data (fallback)
- **ANA ArcGIS REST:** Ottobacias geodata (https://geoservicos.ana.gov.br/arcgis/rest/services/BASES/OTTOBACIAS/MapServer/{layer}/query)

**Rate limits:** None documented, but implement 60s timeout on all requests.

### Dependencies (inferred from imports)
```python
# Geospatial core
geopandas  # 0.14.x
shapely    # 2.0.x
fiona      # 1.9.x

# Visualization
folium     # 0.15.x (Leaflet-based maps)
plotly     # 5.18.x (interactive charts)

# Data
pandas     # 2.2.x
requests   # HTTP API calls
```

**No `requirements.txt` exists.** Create one if dependencies need pinning.

## Common Gotchas

### 1. File Paths with Parenthesis
`crie_interactive_sector_maps.py)` has trailing `)` in filename - NOT A TYPO. Use quotes:
```powershell
python "analise_exploratoria\crie_interactive_sector_maps.py)"
```

### 2. Uniform Per-Capita Rate
All scripts use **0.95 kg/hab/day** statewide - NO regional variation. This is intentional for initial estimates but should be noted in any expansion.

### 3. "Outras Bacias" Category
Aggregates all watersheds NOT in the 7 named bacias. Contains ~47% of state population. Do NOT try to disaggregate - matches project methodology.

### 4. Output File Sizes
- Dashboard: 0.08 MB (compact with render-on-demand)
- Maps: 0.46 MB (municipal) to 8 MB (watershed with Ottobacias)
- GitHub Pages limit: 100 MB per repo - safe for now
- Simplification + render-on-demand keeps mobile performance optimal

### 5. Windows Paths in Code
Scripts use raw strings `r'outputs\file.csv'` - Windows-specific. When refactoring for cross-platform, use `os.path.join()` or `pathlib.Path`.

## Key Files to Reference

- **`migrar_bacias_ana.py`** (495 lines) - Dual-source data loading, spatial joins, multi-layer maps, mobile-optimized controls
- **`dashboard_bacias.py`** (1288 lines) - Plotly subplots, mobile-first render-on-demand, back-to-top button, compact mode toggle
- **`crie_interactive_sector_maps.py)`** (300 lines) - CLI patterns, argparse usage, accessibility standards
- **`README_BACIAS.md`** - Full technical documentation (methodology, data sources, limitations)

## When Making Changes

1. **Adding new map types:** Follow `analise_bacias_hidrograficas.py` pattern (lines 1-250)
2. **Modifying visualizations:** Check accessibility requirements first (see lines 180-220 in `crie_interactive_sector_maps.py)`)
3. **API integrations:** Implement 3-tier fallback (primary → alternative → local calculation)
4. **New outputs:** Always save to `outputs/`, use descriptive filenames in Portuguese
5. **Documentation:** Update README_BACIAS.md if methodology changes

**Testing:** Open generated HTML in browser, verify:
- Maps load correctly
- Colors pass colorblind simulation (Chrome DevTools → Rendering → Emulate vision deficiencies)
- Mobile layout works (< 768px width)
- Popups show correct data

---

**Last Updated:** October 2025 | **Language:** Brazilian Portuguese (code comments + outputs) | **Deployment:** GitHub Pages

*.gpkg
!analise_exploratoria/outputs/bacias_oficiais_ana_macro.gpkg
