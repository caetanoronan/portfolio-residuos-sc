import os
import sys
import geopandas as gpd
import matplotlib.pyplot as plt

def carregar_e_analisar_dados():
    """
    Carrega e analisa arquivos geoespaciais da pasta
    """
    # Tentar carregar arquivos GPKG primeiro
    for arquivo in os.listdir('.'):
        if arquivo.endswith('.gpkg'):
            try:
                print(f"\n📂 Tentando carregar: {arquivo}")
                gdf = gpd.read_file(arquivo)
                print(f"✅ SUCESSO! Arquivo carregado: {arquivo}")
                return gdf, arquivo
            except Exception as e:
                print(f"❌ Erro ao carregar {arquivo}: {e}")
                continue

    # Se não encontrar GPKG, tentar shapefiles
    for arquivo in os.listdir('.'):
        if arquivo.endswith('.shp'):
            try:
                print(f"\n📂 Tentando carregar: {arquivo}")
                gdf = gpd.read_file(arquivo)
                print(f"✅ SUCESSO! Arquivo carregado: {arquivo}")
                return gdf, arquivo
            except Exception as e:
                print(f"❌ Erro ao carregar {arquivo}: {e}")
                continue

    print("\n❌ Nenhum arquivo geoespacial pôde ser carregado.")
    return None, None

# Executar a carga de dados
gdf, nome_arquivo = carregar_e_analisar_dados()

if gdf is not None:
    print(f"\n🎉 DADOS CARREGADOS COM SUCESSO!")
    print("=" * 60)

    # Análise exploratória
    print(f"📊 INFORMAÇÕES GERAIS:")
    print(f"Arquivo: {nome_arquivo}")
    print(f"Formato: {gdf.shape[0]} feições x {gdf.shape[1]} atributos")
    print(f"Sistema de coordenadas: {gdf.crs}")
    print(f"Extensão geográfica: {gdf.total_bounds}")

    print(f"\n📋 LISTA DE COLUNAS:")
    print("-" * 40)
    for i, coluna in enumerate(gdf.columns):
        tipo = gdf[coluna].dtype
        print(f"{i+1:2d}. {coluna} ({tipo})")

    print(f"\n📈 ESTATÍSTICAS DOS ATRIBUTOS NUMÉRICOS:")
    print("-" * 50)
    colunas_numericas = gdf.select_dtypes(include=['number']).columns
    if len(colunas_numericas) > 0:
        print(gdf[colunas_numericas].describe())
    else:
        print("Nenhuma coluna numérica encontrada")

    print(f"\n🔍 AMOSTRA DOS DADOS (primeiras 3 linhas):")
    print("-" * 50)
    print(gdf.head(3))

    # Visualizações
    print(f"\n🗺️ CRIANDO VISUALIZAÇÕES...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))

    gdf.plot(ax=ax1, alpha=0.7, edgecolor='black', linewidth=0.3)
    ax1.set_title(f"Visualização dos Setores\n{os.path.basename(nome_arquivo)}", fontweight='bold')
    ax1.axis('off')

    if len(colunas_numericas) > 0:
        coluna_para_mapear = colunas_numericas[0]
        gdf.plot(column=coluna_para_mapear, ax=ax2, legend=True,
                 cmap='viridis', alpha=0.7, edgecolor='black', linewidth=0.3)
        ax2.set_title(f"Mapa de {coluna_para_mapear}", fontweight='bold')
        ax2.axis('off')
    else:
        gdf.plot(ax=ax2, alpha=0.7, edgecolor='red', linewidth=0.3)
        ax2.set_title("Visualização Alternativa", fontweight='bold')
        ax2.axis('off')

    plt.tight_layout()
    plt.savefig('analise_exploratoria_setores.png', dpi=300, bbox_inches='tight')
    plt.show()

    print(f"\n💾 Visualização salva como 'analise_exploratoria_setores.png'")

    with open('resumo_analise.txt', 'w', encoding='utf-8') as f:
        f.write("RESUMO DA ANÁLISE EXPLORATÓRIA\n")
        f.write("=" * 40 + "\n")
        f.write(f"Arquivo: {nome_arquivo}\n")
        f.write(f"Feições: {gdf.shape[0]}\n")
        f.write(f"Atributos: {gdf.shape[1]}\n")
        f.write(f"SRC: {gdf.crs}\n\n")
        f.write("COLUNAS:\n")
        for coluna in gdf.columns:
            f.write(f"- {coluna}\n")

    print(f"📄 Resumo salvo como 'resumo_analise.txt'")

else:
    diretorio = os.getcwd()
    print("\n🚨 NENHUM ARQUIVO GEOESPACIAL ENCONTRADO")
    print("\n📝 AÇÕES SUGERIDAS:")
    print("1. Verifique se o arquivo GPKG ou SHP está na pasta:")
    print(f"   {diretorio}")
    print("2. Se estiver em subpasta, me informe o nome completo")
    print("3. Ou arraste o arquivo para esta pasta")

print(f"\n💻 INFORMAÇÕES DO SISTEMA:")
print(f"Diretório atual: {os.getcwd()}")
print(f"Python: {sys.version}")
print(f"GeoPandas: {gpd.__version__}")