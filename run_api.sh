#!/bin/bash
# Script para rodar API localmente

echo "🚀 Iniciando API Resíduos SC..."
echo ""

# Verificar se está no ambiente virtual
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Ambiente virtual não ativado!"
    echo "   Execute: source .venv/bin/activate (Linux/Mac)"
    echo "   Execute: .venv\\Scripts\\activate (Windows)"
    echo ""
    exit 1
fi

# Verificar se dependências estão instaladas
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📦 Instalando dependências..."
    pip install -r requirements-api.txt
    echo ""
fi

# Rodar API
echo "✅ Iniciando servidor..."
echo "📍 Swagger UI: http://localhost:8000/docs"
echo "📍 ReDoc: http://localhost:8000/redoc"
echo "📍 Health: http://localhost:8000/health"
echo ""
echo "Pressione Ctrl+C para parar o servidor"
echo ""

uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
