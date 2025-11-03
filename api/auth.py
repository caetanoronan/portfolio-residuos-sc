"""
Sistema de Autenticação com API Keys (OPCIONAL)

Este módulo implementa autenticação simples com API Keys para proteger
endpoints específicos da API. Por padrão, a API é pública e não requer
autenticação.

Para habilitar autenticação:
1. Defina API_KEYS_ENABLED=true no ambiente
2. Configure API_KEYS no formato: "key1,key2,key3"
3. Use o decorador @require_api_key nos endpoints protegidos

Exemplo de uso:
    export API_KEYS_ENABLED=true
    export API_KEYS="seu-token-secreto-1,seu-token-secreto-2"
"""

import os
from typing import Optional
from fastapi import Header, HTTPException, Depends
from functools import wraps


class APIKeyAuth:
    """Gerenciador de autenticação com API Keys"""
    
    def __init__(self):
        # Carregar configuração do ambiente
        self.enabled = os.getenv("API_KEYS_ENABLED", "false").lower() == "true"
        
        # Carregar API keys válidas do ambiente (separadas por vírgula)
        keys_str = os.getenv("API_KEYS", "")
        self.valid_keys = set(k.strip() for k in keys_str.split(",") if k.strip())
        
        if self.enabled and not self.valid_keys:
            print("⚠️  AVISO: API_KEYS_ENABLED=true mas nenhuma chave configurada!")
            print("    Configure API_KEYS no ambiente para habilitar autenticação")
    
    def is_enabled(self) -> bool:
        """Verifica se autenticação está habilitada"""
        return self.enabled
    
    def validate_key(self, api_key: str) -> bool:
        """Valida uma API key"""
        if not self.enabled:
            return True  # Autenticação desabilitada, aceita qualquer requisição
        
        return api_key in self.valid_keys
    
    def get_stats(self) -> dict:
        """Retorna estatísticas de autenticação"""
        return {
            "autenticacao_habilitada": self.enabled,
            "total_keys_configuradas": len(self.valid_keys) if self.enabled else 0,
            "modo": "Protegida" if self.enabled else "Pública"
        }


# Instância global do gerenciador de autenticação
auth_manager = APIKeyAuth()


async def verify_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> str:
    """
    Dependency para verificar API Key no header X-API-Key
    
    Args:
        x_api_key: API Key enviada no header HTTP
    
    Returns:
        str: API Key validada
    
    Raises:
        HTTPException: 401 se autenticação habilitada e key inválida/ausente
    """
    # Se autenticação desabilitada, permite acesso
    if not auth_manager.is_enabled():
        return "public"
    
    # Se habilitada, requer API key
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail={
                "erro": "API Key obrigatória",
                "mensagem": "Esta API requer autenticação. Inclua o header 'X-API-Key' na requisição.",
                "exemplo": "curl -H 'X-API-Key: sua-chave-aqui' https://api.exemplo.com/api/v1/municipios"
            },
            headers={"WWW-Authenticate": "ApiKey"}
        )
    
    # Valida a key
    if not auth_manager.validate_key(x_api_key):
        raise HTTPException(
            status_code=403,
            detail={
                "erro": "API Key inválida",
                "mensagem": "A API Key fornecida não é válida ou foi revogada.",
            }
        )
    
    return x_api_key


def require_api_key(func):
    """
    Decorador para proteger endpoints com API Key
    
    Uso:
        @router.get("/endpoint-protegido")
        @require_api_key
        async def endpoint_protegido():
            return {"mensagem": "Acesso autorizado"}
    """
    @wraps(func)
    async def wrapper(*args, api_key: str = Depends(verify_api_key), **kwargs):
        # Chama função original com todos os argumentos
        return await func(*args, **kwargs)
    
    return wrapper


# Funções auxiliares para integração com endpoints

def get_auth_info() -> dict:
    """
    Retorna informações sobre o estado de autenticação da API
    
    Returns:
        dict: Estatísticas de autenticação
    """
    return auth_manager.get_stats()


def is_auth_enabled() -> bool:
    """
    Verifica se autenticação está habilitada
    
    Returns:
        bool: True se autenticação ativa, False caso contrário
    """
    return auth_manager.is_enabled()


# Exemplo de uso em endpoints:
"""
from fastapi import APIRouter, Depends
from api.auth import verify_api_key

router = APIRouter()

# Endpoint protegido (requer API Key se autenticação habilitada)
@router.get("/protegido")
async def endpoint_protegido(api_key: str = Depends(verify_api_key)):
    return {"mensagem": "Acesso autorizado", "api_key": api_key}

# Endpoint público (sem autenticação)
@router.get("/publico")
async def endpoint_publico():
    return {"mensagem": "Acesso público"}
"""
