# 🚀 GUIA: Como Publicar no GitHub Pages

## ✅ O que já foi feito:
- ✓ Repositório Git inicializado
- ✓ Arquivos adicionados e commitados
- ✓ Branch renomeado para `main`
- ✓ Página index.html criada
- ✓ README.md profissional
- ✓ .gitignore configurado

## 📝 PRÓXIMOS PASSOS:

### 1️⃣ Criar Repositório no GitHub

1. Acesse: **https://github.com/new**

2. Preencha:
   - **Repository name:** `portfolio-residuos-sc` (ou outro nome de sua preferência)
   - **Description:** `Análise geoespacial de resíduos em Santa Catarina com mapas interativos acessíveis`
   - Marque: **Public** ✅
   - **NÃO marque** "Add a README file" (já temos um)
   - Clique em **"Create repository"**

### 2️⃣ Conectar Repositório Local ao GitHub

Após criar o repositório, copie os comandos que aparecem na tela:

```powershell
cd "c:\Users\caetanoronan\OneDrive - UFSC\Área de Trabalho\Portifolio"

# Substitua SEU_USUARIO pelo seu username do GitHub
git remote add origin https://github.com/SEU_USUARIO/portfolio-residuos-sc.git

git push -u origin main
```

**Exemplo:** Se seu usuário for `joaosilva`, use:
```powershell
git remote add origin https://github.com/joaosilva/portfolio-residuos-sc.git
```

### 3️⃣ Ativar GitHub Pages

1. No seu repositório no GitHub, vá em **Settings** (⚙️)

2. No menu lateral esquerdo, clique em **Pages**

3. Em **"Source"**, selecione:
   - Branch: `main`
   - Folder: `/ (root)`

4. Clique em **Save**

5. Aguarde 1-2 minutos e **atualize a página**

6. Você verá uma mensagem:
   ```
   ✅ Your site is published at https://SEU_USUARIO.github.io/portfolio-residuos-sc/
   ```

### 4️⃣ Atualizar Links no README e index.html

Depois de obter seu URL, atualize os links:

1. Abra `README.md` e `index.html`
2. Substitua `SEU_USUARIO` pelo seu username real
3. Faça commit e push:

```powershell
git add README.md index.html
git commit -m "docs: Atualiza links com username correto"
git push
```

## 🌐 URLs que você terá:

- **Página inicial:** `https://SEU_USUARIO.github.io/portfolio-residuos-sc/`
- **Mapa interativo:** `https://SEU_USUARIO.github.io/portfolio-residuos-sc/analise_exploratoria/outputs/interactive_waste_map.html`

## 💡 DICAS:

### Adicionar ao LinkedIn/Currículo:
```
🗺️ Projeto: Análise Geoespacial de Resíduos - SC
📊 16.831 setores censitários analisados
♿ Design acessível para daltonismo
🔗 https://SEU_USUARIO.github.io/portfolio-residuos-sc/
💻 GitHub: github.com/SEU_USUARIO/portfolio-residuos-sc
```

### Compartilhar em redes sociais:
```
Acabei de publicar minha análise geoespacial de resíduos em Santa Catarina! 🗺️

✨ Destaques:
- 16.831 setores censitários
- Mapas interativos e acessíveis
- Design inclusivo para daltonismo
- Python + GeoPandas + Folium

Confira: https://SEU_USUARIO.github.io/portfolio-residuos-sc/

#Geoprocessamento #Python #Acessibilidade #DataScience
```

## 🔧 Comandos Úteis Git:

```powershell
# Ver status
git status

# Adicionar mudanças
git add .

# Fazer commit
git commit -m "sua mensagem"

# Enviar para GitHub
git push

# Ver histórico
git log --oneline
```

## ❓ Problemas Comuns:

### "Permission denied" ao fazer push:
```powershell
# Use token de acesso pessoal (não senha)
# Gere um em: https://github.com/settings/tokens
# Ao fazer push, use o token como senha
```

### Mapa não aparece:
- Aguarde 2-3 minutos após ativar GitHub Pages
- Limpe cache do navegador (Ctrl + Shift + R)
- Verifique se o arquivo HTML está na pasta correta

### Links quebrados:
- Certifique-se de usar caminhos relativos
- Não use `file:///` ou `C:\`
- Use `/` (barra) e não `\` (barra invertida)

## 📞 Precisa de Ajuda?

Se encontrar problemas, me avise e posso ajudar a resolver! 🚀

---

**Boa sorte com seu portfólio! 🎉**
