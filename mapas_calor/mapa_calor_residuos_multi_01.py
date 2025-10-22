import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import contextily as ctx
from shapely.geometry import Point
import numpy as np

# Criar dados de exemplo
def criar_dados_exemplo():
    data = {
        'Nome': ['Empresa_A', 'Empresa_B', 'Empresa_C', 'Empresa_D', 'Empresa_E', 
                'Empresa_F', 'Empresa_G', 'Empresa_H', 'Empresa_I', 'Empresa_J'],
        'Longitude': [-46.6333, -46.6415, -46.6282, -46.6350, -46.6300,
                     -46.6250, -46.6380, -46.6320, -46.6270, -46.6400],
        'Latitude': [-23.5500, -23.5489, -23.5512, -23.5450, -23.5530,
                    -23.5490, -23.5470, -23.5520, -23.5460, -23.5440],
        'Residuo': ['Plastico', 'Metal', 'Organico', 'Plastico', 'Papel',
                   'Metal', 'Organico', 'Plastico', 'Papel', 'Organico'],
        'Quantidade_kg': [150, 80, 200, 120, 60, 90, 180, 110, 70, 160]
    }
    return pd.DataFrame(data)

# Criar GeoDataFrame
df = criar_dados_exemplo()
geometry = [Point(xy) for xy in zip(df.Longitude, df.Latitude)]
gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

# Converter para Web Mercator para usar com contextily
gdf = gdf.to_crs(epsg=3857)

print("Dados carregados com sucesso!")
print(f"Total de pontos: {len(gdf)}")
print(f"Tipos de resíduos: {gdf['Residuo'].unique()}")

# AGORA o código avançado (após a definição do gdf)

# Criar subplots para cada tipo de resíduo
fig, axes = plt.subplots(2, 2, figsize=(20, 15))
axes = axes.flatten()

tipos_residuos = gdf['Residuo'].unique()

for i, residuo in enumerate(tipos_residuos):
    if i < len(axes):
        ax = axes[i]
        dados_residuo = gdf[gdf['Residuo'] == residuo]
        
        if not dados_residuo.empty:
            # Plotar pontos com tamanho proporcional à quantidade
            scatter = ax.scatter(
                dados_residuo.geometry.x,
                dados_residuo.geometry.y,
                c=dados_residuo['Quantidade_kg'],
                s=dados_residuo['Quantidade_kg'] * 3,
                cmap='YlOrRd',
                alpha=0.7,
                edgecolors='black',
                linewidth=0.5
            )
            
            # Adicionar mapa de fundo
            ctx.add_basemap(ax, crs=gdf.crs, source=ctx.providers.CartoDB.Positron)
            
            # Configurações
            ax.set_title(f'Geração de {residuo}\n(Total: {dados_residuo["Quantidade_kg"].sum()} kg)', 
                        fontsize=14, fontweight='bold')
            ax.axis('off')
            
            # Adicionar barra de cores
            plt.colorbar(scatter, ax=ax, label='Quantidade (kg)')

# Ocultar eixos vazios se houver
for i in range(len(tipos_residuos), len(axes)):
    axes[i].axis('off')

# Ajustar layout
plt.suptitle('Mapas de Calor - Geração de Resíduos por Tipo', 
             fontsize=18, fontweight='bold', y=0.95)
plt.tight_layout()
plt.savefig('mapas_residuos_por_tipo.png', dpi=300, bbox_inches='tight')
plt.show()

# Estatísticas básicas
print("\n📊 Estatísticas de Geração de Resíduos:")
estatisticas = gdf.groupby('Residuo')['Quantidade_kg'].agg(['sum', 'mean', 'count']).round(2)
print(estatisticas)