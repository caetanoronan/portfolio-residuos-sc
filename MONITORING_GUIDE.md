# 📊 Guia de Monitoramento - API Resíduos SC

## Por que Monitorar?

O monitoramento garante que sua API esteja:
- ✅ **Online 24/7** - Detecta quedas imediatamente
- ⚡ **Rápida** - Identifica lentidão
- 🔄 **Sem Cold Starts** - Requisições periódicas mantém API "quente" no Render
- 📧 **Com Alertas** - Notifica você se algo der errado

---

## 🤖 UptimeRobot (Recomendado - GRATUITO)

### Características
- ✅ **100% Gratuito** - Até 50 monitores
- ✅ **Intervalo de 5 minutos** - 288 verificações/dia
- ✅ **Alertas Email/SMS** - Notificação instantânea
- ✅ **Histórico 90 dias** - Relatórios de uptime
- ✅ **Status Page Público** - Compartilhe status com usuários

### Configuração Passo a Passo

#### 1. Criar Conta
```
🔗 https://uptimerobot.com/signUp
- Email
- Senha
- Verificar email
```

#### 2. Adicionar Monitor
```
Dashboard → Add New Monitor

Tipo: HTTP(s)
Nome: API Resíduos SC - Health Check
URL: https://api-residuos-sc.onrender.com/health
Intervalo: 5 minutos
```

#### 3. Configurar Alertas
```
Alert Contacts → Add Alert Contact

Tipo: Email
Email: seu-email@exemplo.com

Depois, no monitor:
Alert Contacts → Selecionar seu email
```

#### 4. Adicionar Mais Endpoints (Opcional)
```
Monitor 2:
Nome: API Resíduos SC - Municípios
URL: https://api-residuos-sc.onrender.com/api/v1/municipios?limit=1

Monitor 3:
Nome: API Resíduos SC - Docs
URL: https://api-residuos-sc.onrender.com/docs
```

---

## 📈 Alternativas de Monitoramento

### 1. **Render.com Dashboard** (Built-in)
```
✅ Métricas incluídas no Render
- CPU usage
- Memory usage
- Bandwidth
- Deploy history
- Logs em tempo real

🔗 https://dashboard.render.com/
```

### 2. **Better Uptime** (14 dias grátis, depois $10/mês)
```
Funcionalidades extras:
- SSL monitoring
- Domain expiration alerts
- Incident management
- Status pages customizadas

🔗 https://betteruptime.com/
```

### 3. **Pingdom** (Trial gratuito)
```
Funcionalidades profissionais:
- Real User Monitoring (RUM)
- Transaction monitoring
- Root cause analysis
- Global monitoring locations

🔗 https://www.pingdom.com/
```

### 4. **StatusCake** (Free tier limitado)
```
Free tier:
- 10 monitores
- Intervalo de 5 minutos
- Email alerts

🔗 https://www.statuscake.com/
```

---

## 🔥 Evitando Cold Starts no Render

O Render Free tier tem **cold starts** (~30 segundos) após 15 minutos de inatividade.

### Solução: Keep-Alive com UptimeRobot

```
✅ UptimeRobot faz requisições a cada 5 minutos
✅ Mantém API "quente" 24/7
✅ Zero configuração adicional

Resultado: Cold starts apenas após quedas, não por inatividade!
```

### Alternativa: Cron Job Externo

```bash
# Script em servidor próprio ou GitHub Actions
*/5 * * * * curl https://api-residuos-sc.onrender.com/health
```

---

## 📊 Status Page Pública (UptimeRobot)

### Criar Status Page

```
Dashboard → Add Status Page

Nome: Status API Resíduos SC
URL: api-residuos-sc (slug)
Monitores: Selecionar todos

Resultado: https://stats.uptimerobot.com/api-residuos-sc
```

### Embedar no Site

```html
<!-- Adicionar em apresentacao.html -->
<iframe 
    src="https://stats.uptimerobot.com/api-residuos-sc" 
    width="100%" 
    height="400" 
    frameborder="0">
</iframe>
```

---

## 🚨 Configurando Alertas Avançados

### Email + Webhook (Slack, Discord, etc.)

#### Slack:
```
1. Criar Incoming Webhook no Slack
   https://api.slack.com/messaging/webhooks

2. UptimeRobot → Alert Contacts → Webhook
   Webhook URL: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
   
3. POST Data:
   {"text": "*monitor_name* is *monitor_alert_type*"}
```

#### Discord:
```
1. Discord Server → Settings → Integrations → Webhooks

2. UptimeRobot → Alert Contacts → Webhook
   Webhook URL: https://discord.com/api/webhooks/YOUR_WEBHOOK
   
3. POST Data (JSON):
   {
     "content": "🚨 **API Resíduos SC** está *monitor_alert_type*",
     "username": "UptimeRobot"
   }
```

---

## 📱 Monitoramento Mobile

### Apps UptimeRobot

```
📱 iOS: https://apps.apple.com/app/uptime-robot/id1104878581
🤖 Android: https://play.google.com/store/apps/details?id=com.uptimerobot.app

Funcionalidades:
- Push notifications
- Ver status de todos os monitores
- Histórico de incidentes
- Gerenciar pausas
```

---

## 🔍 Logs e Debugging

### Ver Logs no Render

```bash
# No Dashboard Render:
1. Selecionar serviço
2. Aba "Logs"
3. Filtrar por erro/warning

# Via Render CLI:
render logs api-residuos-sc --tail
```

### Adicionar Logging Estruturado na API

```python
# api/main.py
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@app.middleware("http")
async def log_requests(request, call_next):
    start = datetime.now()
    response = await call_next(request)
    duration = (datetime.now() - start).total_microseconds / 1000
    
    logging.info(f"{request.method} {request.url.path} - {response.status_code} - {duration}ms")
    return response
```

---

## 📈 Métricas Importantes

### O que Monitorar

1. **Uptime** 🎯 Objetivo: > 99.5%
   ```
   Monitorar: /health endpoint
   Alerta: Se down > 2 minutos
   ```

2. **Response Time** ⚡ Objetivo: < 500ms
   ```
   Monitorar: Tempo de resposta médio
   Alerta: Se > 2000ms
   ```

3. **Error Rate** ❌ Objetivo: < 1%
   ```
   Monitorar: Status codes 5xx
   Alerta: Se > 5 erros/hora
   ```

4. **Cold Starts** 🧊 Objetivo: < 10/dia
   ```
   Monitorar: Logs "Starting instance"
   Solução: Keep-alive com UptimeRobot
   ```

---

## 🎯 Checklist de Monitoramento

### Configuração Inicial
- [ ] UptimeRobot conta criada
- [ ] Monitor para `/health` adicionado (5 min)
- [ ] Email alert configurado
- [ ] Status page criada (opcional)

### Monitoramento Avançado (Opcional)
- [ ] Monitor para `/api/v1/municipios`
- [ ] Monitor para `/api/v1/bacias`
- [ ] Webhook para Slack/Discord
- [ ] App mobile instalado

### Manutenção
- [ ] Verificar relatórios semanalmente
- [ ] Revisar logs de erro mensalmente
- [ ] Atualizar alertas se necessário

---

## 🆘 Troubleshooting

### API está down
```bash
1. Verificar status no Render Dashboard
2. Ver logs: render logs api-residuos-sc --tail
3. Verificar se deploy falhou
4. Testar localmente: uvicorn api.main:app
```

### Cold starts frequentes
```bash
1. Confirmar UptimeRobot está ativo
2. Verificar intervalo (deve ser 5 min)
3. Adicionar segundo monitor como backup
```

### Alertas falsos
```bash
1. Verificar se API realmente está online
2. Ajustar timeout no UptimeRobot (padrão 30s)
3. Verificar se não é manutenção programada
```

---

## 📚 Recursos Adicionais

- [UptimeRobot Documentation](https://uptimerobot.com/help/)
- [Render Monitoring](https://render.com/docs/monitoring)
- [FastAPI Logging](https://fastapi.tiangolo.com/tutorial/logging/)
- [Better Uptime Guide](https://docs.betteruptime.com/)

---

## ✅ Resultado Esperado

Após configurar monitoramento:

```
✅ API online 99.9% do tempo
✅ Notificação instantânea se cair
✅ Zero cold starts por inatividade
✅ Logs estruturados para debugging
✅ Relatórios semanais de uptime
✅ Status público para usuários
```

---

**Desenvolvido por:** Ronan Armando Caetano  
**Projeto:** Portfolio Resíduos SC  
**UFSC 2025** | Desenvolvido com GitHub Copilot 🤖
