#!/bin/bash
# Script de build para Render.com
# Instala GDAL e dependências geoespaciais antes do pip install

echo "📦 Instalando dependências do sistema..."

# Instalar GDAL e bibliotecas geoespaciais
apt-get update
apt-get install -y gdal-bin libgdal-dev

# Definir variável de ambiente para compilação
export GDAL_CONFIG=/usr/bin/gdal-config

echo "✅ GDAL instalado! Versão:"
gdal-config --version

echo "📦 Instalando dependências Python..."
pip install -r requirements-api.txt

echo "✅ Build concluído!"
