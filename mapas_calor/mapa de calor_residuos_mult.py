import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import contextily as ctx
from shapely.geometry import Point
import numpy as np

# Criar dados de exemplo (substitua com seus dados)
data = {
    'Nome': ['Empresa_A', 'Empresa_B', 'Empresa_C', 'Empresa_D', 'Empresa_E'],
    'Longitude': [-46.6333, -46.6415, -46.6282, -46.6350, -46.6300],
    'Latitude': [-23.5500, -23.5489, -23.5512, -23.5450, -23.5530],
    'Residuo': ['Plastico', 'Metal', 'Organico', 'Plastico', 'Papel'],
    'Quantidade_kg': [150, 80, 200, 120, 60]
}

df = pd.DataFrame(data)

# Converter para GeoDataFrame
geometry = [Point(xy) for xy in zip(df.Longitude, df.Latitude)]
gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

# Converter para Web Mercator para usar com contextily
gdf = gdf.to_crs(epsg=3857)

# Criar figura e eixo
fig, ax = plt.subplots(1, 1, figsize=(15, 10))

# Plotar pontos coloridos por tipo de resíduo
residuos_cores = {
    'Plastico': 'red',
    'Metal': 'blue', 
    'Organico': 'green',
    'Papel': 'orange'
}

for residuo, cor in residuos_cores.items():
    dados_residuo = gdf[gdf['Residuo'] == residuo]
    if not dados_residuo.empty:
        # Criar mapa de calor simples usando scatter plot com transparência
        ax.scatter(
            dados_residuo.geometry.x,
            dados_residuo.geometry.y,
            c=cor,
            s=dados_residuo['Quantidade_kg'] * 2,  # Tamanho proporcional à quantidade
            alpha=0.6,
            label=f'{residuo}',
            edgecolors='black',
            linewidth=0.5
        )

# Adicionar mapa de fundo
ctx.add_basemap(ax, crs=gdf.crs, source=ctx.providers.CartoDB.Positron)

# Configurações do gráfico
ax.set_title('Mapa de Calor - Geração de Resíduos por Tipo\nEmpresa/Município', 
             fontsize=16, fontweight='bold', pad=20)
ax.legend(title='Tipo de Resíduo', title_fontsize=12, fontsize=10)
ax.axis('off')

# Adicionar grade de coordenadas (opcional)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('mapa_calor_residuos.png', dpi=300, bbox_inches='tight')
plt.show()

# Estatísticas básicas
print("\n📊 Estatísticas de Geração de Resíduos:")
print(gdf.groupby('Residuo')['Quantidade_kg'].agg(['sum', 'mean', 'count']).round(2))