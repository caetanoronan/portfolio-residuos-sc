import os
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

# Configurar o diretório de trabalho
diretorio = r"C:\Users\caetanoronan\OneDrive - UFSC\Área de Trabalho\Portifolio\analise_exploratoria"
os.chdir(diretorio)

print("📁 Conteúdo da pasta analise_exploratoria:")
print("=" * 50)

# Listar todos os arquivos
arquivos = os.listdir('.')
for i, arquivo in enumerate(arquivos, 1):
    tamanho = os.path.getsize(arquivo) / (1024*1024)  # Tamanho em MB
    print(f"{i:2d}. {arquivo} ({tamanho:.2f} MB)")

# Procurar especificamente por arquivos GPKG
arquivos_gpkg = [f for f in arquivos if f.endswith('.gpkg')]
arquivos_shp = [f for f in arquivos if f.endswith('.shp')]

print("\n🔍 Arquivos geopackage encontrados:")
if arquivos_gpkg:
    for arquivo in arquivos_gpkg:
        print(f"📍 {arquivo}")
else:
    print("❌ Nenhum arquivo .gpkg encontrado")

print("\n🔍 Arquivos shapefile encontrados:")
if arquivos_shp:
    for arquivo in arquivos_shp:
        print(f"📍 {arquivo}")
else:
    print("❌ Nenhum arquivo .shp encontrado")