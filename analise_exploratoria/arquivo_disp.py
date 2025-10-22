import os
import geopandas as gpd

# Listar todos os arquivos no diretório atual
print("📁 Arquivos no diretório atual:")
for file in os.listdir('.'):
    if file.endswith('.gpkg') or file.endswith('.shp'):
        print(f"📍 {file}")

# Listar também em subdiretórios comuns
possible_paths = [
    '.',
    './data',
    './dados',
    './shapefiles',
    '../',
    'C:/Users/caetanoronan/OneDrive - UFSC/Área de Trabalho/Portifolio'
]

print("\n🔍 Procurando arquivos GPKG em diretórios comuns:")
for path in possible_paths:
    if os.path.exists(path):
        for file in os.listdir(path):
            if file.endswith('.gpkg'):
                print(f"✅ Encontrado: {os.path.join(path, file)}")