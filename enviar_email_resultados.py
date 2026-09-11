#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📧 Script para enviar emails com resultados dos scrapers
Autor: Sistema Automatizado
Data: 2025
"""

import os
import json
import glob
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import pytz

def validar_configuracao_email():
    """Valida se todas as variáveis de email estão configuradas"""
    variaveis_obrigatorias = {
        'SMTP_SERVER': os.getenv('SMTP_SERVER'),
        'SMTP_PORT': os.getenv('SMTP_PORT'),
        'EMAIL_USER': os.getenv('EMAIL_USER'),
        'EMAIL_PASS': os.getenv('EMAIL_PASS'),
        'EMAIL_FROM': os.getenv('EMAIL_FROM'),
        'EMAIL_DESTINO': os.getenv('EMAIL_DESTINO')
    }
    
    print("🔍 VALIDANDO CONFIGURAÇÃO DE EMAIL:")
    print("=" * 40)
    
    configurado = True
    for var, valor in variaveis_obrigatorias.items():
        if valor and valor.strip():
            # Mascarar senha
            if 'PASS' in var:
                valor_exibicao = '*' * len(valor)
            else:
                valor_exibicao = valor
            print(f"✅ {var}: {valor_exibicao}")
        else:
            print(f"❌ {var}: NÃO CONFIGURADO")
            configurado = False
    
    if not configurado:
        print("\n⚠️  PROBLEMAS ENCONTRADOS:")
        print("   - Algumas variáveis de ambiente não estão configuradas")
        print("   - Verifique se os GitHub Secrets estão configurados corretamente")
        print("   - Execute o teste local primeiro: python teste_email_local.py")
        return False
    
    # Validações específicas
    try:
        porta = int(variaveis_obrigatorias['SMTP_PORT'])
        if porta <= 0 or porta > 65535:
            print(f"❌ SMTP_PORT inválido: {porta}")
            return False
    except (ValueError, TypeError):
        print(f"❌ SMTP_PORT deve ser um número válido: {variaveis_obrigatorias['SMTP_PORT']}")
        return False
    
    print("✅ Todas as variáveis estão configuradas corretamente!")
    return True

def carregar_dados_recentes():
    """Carrega os dados mais recentes dos scrapers"""
    dados = {
        'editais_rapidos': None,
        'chamadas_cnpq_detalhadas': None,
        'chamadas_cnpq_inteligentes': None,
        'dados_reorganizados': None
    }
    
    # Buscar arquivos mais recentes
    for tipo in dados.keys():
        arquivos = glob.glob(f'{tipo}_*.json')
        if arquivos:
            # Pegar o arquivo mais recente baseado no timestamp no nome
            arquivo_mais_recente = max(arquivos, key=lambda x: os.path.getctime(x))
            try:
                with open(arquivo_mais_recente, 'r', encoding='utf-8') as f:
                    dados[tipo] = json.load(f)
                print(f"✅ {tipo}: {arquivo_mais_recente}")
            except Exception as e:
                print(f"❌ Erro ao carregar {tipo}: {e}")
    
    return dados

def criar_resumo_email(dados):
    """Cria o resumo para o email"""
    resumo = []
    resumo.append("🚀 RESUMO DA EXECUÇÃO DOS SCRAPERS")
    resumo.append("=" * 50)
    resumo.append(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    resumo.append("")
    
    # Resumo dos editais rápidos
    if dados['editais_rapidos']:
        editais = dados['editais_rapidos']
        resumo.append("📋 SCRAPER RÁPIDO:")
        if 'ufjf' in editais:
            resumo.append(f"   🏫 UFJF: {len(editais['ufjf'])} editais encontrados")
        if 'fapemig' in editais:
            resumo.append(f"   🔬 FAPEMIG: {len(editais['fapemig'])} oportunidades encontradas")
        if 'cnpq' in editais:
            resumo.append(f"   🎯 CNPq: {len(editais['cnpq'])} chamadas encontradas")
        resumo.append("")
    
    # Resumo das chamadas detalhadas CNPq
    if dados['chamadas_cnpq_detalhadas']:
        chamadas = dados['chamadas_cnpq_detalhadas']
        if 'chamadas_cnpq' in chamadas:
            resumo.append("🔍 SCRAPER DETALHADO CNPq:")
            resumo.append(f"   📊 {len(chamadas['chamadas_cnpq'])} chamadas detalhadas processadas")
            resumo.append("")
    
    # Resumo das chamadas inteligentes CNPq
    if dados['chamadas_cnpq_inteligentes']:
        chamadas = dados['chamadas_cnpq_inteligentes']
        if 'chamadas_cnpq' in chamadas:
            resumo.append("🧠 SCRAPER INTELIGENTE CNPq:")
            resumo.append(f"   🎯 {len(chamadas['chamadas_cnpq'])} chamadas extraídas inteligentemente")
            resumo.append("")
    
    # Resumo dos dados reorganizados
    if dados['dados_reorganizados']:
        dados_reorg = dados['dados_reorganizados']
        resumo.append("🔧 DADOS REORGANIZADOS:")
        total = 0
        for fonte, itens in dados_reorg.items():
            if isinstance(itens, list) and fonte != 'timestamp' and fonte != 'status':
                resumo.append(f"   📄 {fonte.upper()}: {len(itens)} itens com PDFs")
                total += len(itens)
        resumo.append(f"   📊 TOTAL: {total} oportunidades")
        resumo.append("")
    
    resumo.append("🎉 Execução concluída com sucesso!")
    resumo.append("📧 Este email foi enviado automaticamente pelo sistema de scrapers.")
    
    return "\n".join(resumo)

def enviar_email(destinatario, assunto, corpo):
    """Envia o email usando as credenciais configuradas"""
    try:
        # Configurações do servidor SMTP
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        email_user = os.getenv('EMAIL_USER')
        email_pass = os.getenv('EMAIL_PASS')
        email_from = os.getenv('EMAIL_FROM', email_user)
        
        # Validações finais
        if not email_user or not email_pass:
            print("❌ Credenciais de email não configuradas!")
            return False
        
        if not destinatario or not destinatario.strip():
            print("❌ Destinatário não configurado!")
            return False
        
        # Criar mensagem
        msg = MIMEMultipart()
        msg['From'] = email_from
        msg['To'] = destinatario
        msg['Subject'] = assunto
        
        # Adicionar corpo do email
        msg.attach(MIMEText(corpo, 'plain', 'utf-8'))
        
        # Conectar e enviar
        print(f"🔗 Conectando ao servidor SMTP: {smtp_server}:{smtp_port}")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        
        print(f"🔐 Fazendo login com: {email_user}")
        server.login(email_user, email_pass)
        
        print(f"📤 Enviando email para: {destinatario}")
        server.send_message(msg)
        server.quit()
        
        print("✅ Email enviado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao enviar email: {e}")
        return False

def main():
    """Função principal"""
    print("📧 INICIANDO ENVIO DE EMAIL COM RESULTADOS")
    print("=" * 50)
    
    # Validar configuração de email primeiro
    if not validar_configuracao_email():
        print("\n❌ CONFIGURAÇÃO DE EMAIL INVÁLIDA!")
        print("🔧 Para resolver:")
        print("   1. Configure os GitHub Secrets no repositório")
        print("   2. Execute o teste local: python teste_email_local.py")
        print("   3. Verifique se todos os secrets estão preenchidos")
        return 1
    
    # Carregar dados dos scrapers
    print("\n📂 Carregando dados dos scrapers...")
    dados = carregar_dados_recentes()
    
    # Criar resumo para o email
    print("📝 Criando resumo do email...")
    resumo = criar_resumo_email(dados)
    
    # Configurar email
    destinatario = os.getenv('EMAIL_DESTINO', 'ccjota51@gmail.com')
    assunto = f"🚀 Resultados dos Scrapers - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    
    print(f"📧 Configurando email para: {destinatario}")
    print(f"📋 Assunto: {assunto}")
    
    # Enviar email
    print("🚀 Enviando email...")
    sucesso = enviar_email(destinatario, assunto, resumo)
    
    if sucesso:
        print("🎉 Processo concluído com sucesso!")
        print("📧 Email enviado para:", destinatario)
    else:
        print("❌ Falha no envio do email!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
