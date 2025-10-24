import pandas as pd

print("Diagnóstico do CSV de regiões\n" + "="*50)

# Carregar CSV
df_regioes = pd.read_csv(r'outputs\resumo_por_regiao.csv')

print(f"\n📊 Linhas: {len(df_regioes)}")
print(f"📊 Colunas: {list(df_regioes.columns)}")
print(f"\n🔍 Tipos de dados:")
print(df_regioes.dtypes)

print(f"\n📋 Primeiras 5 linhas:")
print(df_regioes.head())

print(f"\n🔢 Estatísticas:")
print(df_regioes[['populacao', 'domestico_t_ano']].describe())

# Verificar nulos
print(f"\n⚠️ Valores nulos:")
print(df_regioes.isnull().sum())

# Converter e testar
df_regioes['populacao'] = pd.to_numeric(df_regioes['populacao'], errors='coerce')
df_regioes['domestico_t_ano'] = pd.to_numeric(df_regioes['domestico_t_ano'], errors='coerce')
regioes_validas = df_regioes.dropna(subset=['populacao', 'domestico_t_ano'])
top_regioes = regioes_validas.nlargest(10, 'domestico_t_ano')

print(f"\n✅ Após conversão e filtro:")
print(f"   Linhas válidas: {len(regioes_validas)}")
print(f"   Top 10:")
print(top_regioes[['NM_RGI', 'populacao', 'domestico_t_ano']])
