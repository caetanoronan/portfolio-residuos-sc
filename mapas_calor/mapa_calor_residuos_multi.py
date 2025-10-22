import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx

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

# Ajustar layout
plt.suptitle('Mapas de Calor - Geração de Resíduos por Tipo', 
             fontsize=18, fontweight='bold', y=0.95)
plt.tight_layout()
plt.savefig('mapas_residuos_por_tipo.png', dpi=300, bbox_inches='tight')
plt.show()