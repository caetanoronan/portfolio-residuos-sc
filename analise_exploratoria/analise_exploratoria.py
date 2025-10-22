import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

# Carregar seu GPKG
gdf_setores = gpd.read_file("seu_arquivo.gpkg")

# Explorar os dados
print("📊 Informações do arquivo:")
print(f"Formato: {gdf_setores.shape}")
print(f"Colunas: {gdf_setores.columns.tolist()}")
print(f"Sistema de coordenadas: {gdf_setores.crs}")
print(f"Amostra dos dados:\n{gdf_setores.head(3)}")

# Ver estatísticas básicas
print("\n📈 Estatísticas:")
print(gdf_setores.describe())

# Plotar mapa básico para visualizar
fig, ax = plt.subplots(1, 1, figsize=(12, 8))
gdf_setores.plot(ax=ax, alpha=0.5, edgecolor='black')
plt.title("Setores Censitários - Visualização Inicial")
plt.axis('off')
plt.show()