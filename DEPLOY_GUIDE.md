# 🚀 Guia de Deploy - API Resíduos SC

## Opções de Deploy Gratuito

### 1️⃣ **Render.com** (Recomendado ✅)

#### **Vantagens:**
- ✅ 750 horas grátis/mês
- ✅ Deploy automático via GitHub
- ✅ HTTPS gratuito
- ✅ Domínio personalizado
- ✅ Logs em tempo real

#### **Passo a Passo:**

1. **Criar conta:**
   - Acesse https://render.com
   - Clique em "Get Started"
   - Conecte sua conta GitHub

2. **Fazer commit dos arquivos:**
   ```powershell
   git add .
   git commit -m "Feat: adiciona API REST completa"
   git push origin main
   ```

3. **Criar Web Service:**
   - Dashboard Render → "New" → "Web Service"
   - Conecte o repositório `portfolio-residuos-sc`
   - **Name**: `api-residuos-sc`
   - **Region**: Oregon (US West)
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements-api.txt`
   - **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

4. **Deploy automático:**
   - Render fará o deploy automaticamente!
   - URL final: `https://api-residuos-sc.onrender.com`

5. **Testar API:**
   ```bash
   curl https://api-residuos-sc.onrender.com/health
   ```

6. **Acessar documentação:**
   - Swagger: https://api-residuos-sc.onrender.com/docs
   - ReDoc: https://api-residuos-sc.onrender.com/redoc

---

### 2️⃣ **Railway.app**

#### **Vantagens:**
- ✅ $5 créditos grátis/mês
- ✅ Deploy via CLI ou GitHub
- ✅ Muito fácil de usar

#### **Passo a Passo:**

1. **Instalar CLI:**
   ```powershell
   npm install -g railway
   ```

2. **Login:**
   ```powershell
   railway login
   ```

3. **Deploy:**
   ```powershell
   railway up
   ```

4. **URL gerada automaticamente!**

---

### 3️⃣ **Fly.io**

#### **Vantagens:**
- ✅ 3 VMs gratuitas
- ✅ Deploy global
- ✅ Muito rápido

#### **Passo a Passo:**

1. **Instalar CLI:**
   ```powershell
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
   ```

2. **Login:**
   ```powershell
   fly auth login
   ```

3. **Launch:**
   ```powershell
   fly launch
   ```

4. **Deploy:**
   ```powershell
   fly deploy
   ```

---

## ⚙️ Variáveis de Ambiente (Opcional)

Se precisar configurar variáveis no Render:

```env
PYTHON_VERSION=3.13.0
PORT=8000
```

---

## 🔧 Troubleshooting

### **Problema: Build falha no Render**

**Solução:**
- Verificar se `requirements-api.txt` está completo
- Adicionar `gunicorn` se necessário:
  ```
  pip install gunicorn
  pip freeze > requirements-api.txt
  ```

### **Problema: GeoPackage não encontrado**

**Solução:**
- Certifique-se de que `analise_exploratoria/SC_setores_CD2022.gpkg` está no repo
- Verificar `.gitignore` - remover se estiver excluindo `.gpkg`

### **Problema: API muito lenta no primeiro acesso**

**Explicação:**
- Render hiberna apps após 15 min de inatividade
- Primeira requisição pode demorar 30-60s (cold start)
- Requisições subsequentes são rápidas

**Solução:**
- Usar ping automático a cada 10 min:
  - https://uptimerobot.com (grátis)
  - Criar monitor HTTP para `https://api-residuos-sc.onrender.com/health`

---

## 📊 Monitoramento

### **UptimeRobot** (Recomendado)
- Monitora API 24/7
- Alerta por email se ficar offline
- Mantém API sempre "acordada"

1. Criar conta: https://uptimerobot.com
2. Add New Monitor
3. Monitor Type: HTTP(s)
4. URL: `https://api-residuos-sc.onrender.com/health`
5. Monitoring Interval: 5 minutes

---

## 🎯 Checklist de Deploy

- [ ] Commit de todos os arquivos
- [ ] Push para GitHub
- [ ] Conectar Render ao repositório
- [ ] Configurar Build Command
- [ ] Configurar Start Command
- [ ] Aguardar primeiro deploy (5-10 min)
- [ ] Testar `/health` endpoint
- [ ] Testar Swagger UI (`/docs`)
- [ ] Configurar UptimeRobot (opcional)
- [ ] Atualizar README com URL pública
- [ ] Compartilhar API! 🎉

---

## 📝 URL Final

Após deploy, sua API estará em:

```
https://api-residuos-sc.onrender.com
```

**Documentação:**
- Swagger: https://api-residuos-sc.onrender.com/docs
- ReDoc: https://api-residuos-sc.onrender.com/redoc

---

## 🔗 Links Úteis

- **Render Dashboard**: https://dashboard.render.com
- **Render Docs**: https://render.com/docs
- **FastAPI Deploy Guide**: https://fastapi.tiangolo.com/deployment/
- **UptimeRobot**: https://uptimerobot.com

---

**Boa sorte com o deploy! 🚀**
