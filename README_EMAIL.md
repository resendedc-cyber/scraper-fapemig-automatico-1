# 📧 Configuração de Email para Scrapers

Este documento explica como configurar o envio automático de emails com os resultados dos scrapers.

## 🎯 **Por que você não está recebendo emails?**

O workflow principal não estava configurado para enviar emails. Agora implementamos essa funcionalidade!

## 🔧 **Configuração Necessária**

### **1️⃣ GitHub Secrets (Obrigatório)**

Você precisa configurar os seguintes secrets no seu repositório:

1. Vá para: `Settings` → `Secrets and variables` → `Actions`
2. Clique em `New repository secret`
3. Adicione cada um dos secrets abaixo:

| **Secret Name** | **Value** | **Descrição** |
|-----------------|-----------|---------------|
| `SMTP_SERVER` | `smtp.gmail.com` | Servidor SMTP do Gmail |
| `SMTP_PORT` | `587` | Porta SMTP (TLS) |
| `EMAIL_USER` | `ccjota51@gmail.com` | Seu email Gmail |
| `EMAIL_PASS` | `[SENHA_DE_16_CARACTERES]` | Senha de aplicativo Gmail |
| `EMAIL_FROM` | `ccjota51@gmail.com` | Email remetente |
| `EMAIL_DESTINO` | `ccjota51@gmail.com` | Email destinatário |

### **2️⃣ Gerar Senha de Aplicativo Gmail**

1. Acesse: [myaccount.google.com](https://myaccount.google.com)
2. Vá para: `Segurança` → `Verificação em duas etapas`
3. Clique em: `Senhas de app`
4. Selecione: `Email` + `Windows Computer`
5. Clique em: `Gerar`
6. **COPIE** a senha de 16 caracteres
7. Cole no secret `EMAIL_PASS`

## 🚀 **Como Funciona Agora**

### **Workflow Atualizado**
- ✅ Executa todos os scrapers
- ✅ Reorganiza dados com PDFs
- ✅ **ENVIA EMAIL AUTOMÁTICO** ← **NOVO!**
- ✅ Faz upload dos arquivos

### **Conteúdo do Email**
O email incluirá:
- 📊 Resumo da execução
- 🏫 UFMG: número de editais
- 🔬 FAPEMIG: número de oportunidades  
- 🎯 CNPq: número de chamadas
- 📄 Total de itens com PDFs
- ⏰ Data/hora da execução

## 🧪 **Teste Local**

Para testar antes de usar no GitHub Actions:

```bash
# 1. Instalar dependências
pip install -r requirements-scraper.txt

# 2. Configurar variáveis de ambiente
export EMAIL_USER="ccjota51@gmail.com"
export EMAIL_PASS="sua_senha_de_app"
export EMAIL_DESTINO="ccjota51@gmail.com"

# 3. Testar configuração
python teste_email_local.py

# 4. Testar envio real
python enviar_email_resultados.py
```

## 📅 **Agendamento**

O workflow roda automaticamente:
- 🕐 **08:00 UTC** (05:00 BRT) - Todos os dias
- 🚀 **Manual** - Via GitHub Actions
- 📝 **Push** - Quando há mudanças no código

## 🔍 **Verificar Status**

1. Vá para: `Actions` → `🚀 Scraper Completo`
2. Clique no workflow mais recente
3. Verifique se o passo `📧 Enviar email com resultados` foi executado
4. Se houver erro, verifique os logs

## ❌ **Problemas Comuns**

### **Email não enviado**
- ✅ Verificar se todos os secrets estão configurados
- ✅ Verificar se a senha de aplicativo está correta
- ✅ Verificar logs do workflow

### **Erro de autenticação**
- ✅ Verificar se a verificação em duas etapas está ativada
- ✅ Verificar se a senha de aplicativo foi gerada corretamente
- ✅ Verificar se o email está correto

### **Workflow falhou**
- ✅ Verificar se todas as dependências estão instaladas
- ✅ Verificar se os scripts Python estão funcionando
- ✅ Verificar logs detalhados

## 🎉 **Resultado Esperado**

Após a configuração correta, você receberá emails automáticos como este:

```
🚀 RESUMO DA EXECUÇÃO DOS SCRAPERS
==================================================
📅 Data/Hora: 18/08/2025 05:00:00

📋 SCRAPER RÁPIDO:
   🏫 UFMG: 4 editais encontrados
   🔬 FAPEMIG: 3 oportunidades encontradas
   🎯 CNPq: 1 chamadas encontradas

🔍 SCRAPER DETALHADO CNPq:
   📊 4 chamadas detalhadas processadas

🧠 SCRAPER INTELIGENTE CNPq:
   🎯 4 chamadas extraídas inteligentemente

🔧 DADOS REORGANIZADOS:
   📄 FAPEMIG: 3 itens com PDFs
   📄 UFMG: 4 itens com PDFs
   📄 CNPQ: 4 itens com PDFs
   📊 TOTAL: 11 oportunidades

🎉 Execução concluída com sucesso!
📧 Este email foi enviado automaticamente pelo sistema de scrapers.
```

## 🆘 **Precisa de Ajuda?**

Se ainda não estiver funcionando:
1. Verifique se todos os secrets estão configurados
2. Execute o teste local primeiro
3. Verifique os logs do GitHub Actions
4. Confirme se a senha de aplicativo foi gerada corretamente

---

**🎯 Meta: Receber emails automáticos diários com os resultados dos scrapers!**
