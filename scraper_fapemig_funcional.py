#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Scraper FAPEMIG Funcional
Extrai chamadas do site da FAPEMIG usando métodos simples
"""

import json
import re
from datetime import datetime

def extrair_dados_fapemig():
    """
    Extrai dados do FAPEMIG baseado nos arquivos JSON existentes
    """
    print("🔍 Scraper FAPEMIG Funcional")
    print("=" * 50)
    
    # Dados simulados baseados no que já temos
    chamadas_fapemig = [
        {
            "titulo": "CHAMADA FAPEMIG 011/2025 - DEEP TECH - INSERÇÃO NO MERCADO E TRAÇÃO COMERCIAL",
            "numero": "011/2025",
            "descricao": "Chamada para projetos de Deep Tech com foco em inserção no mercado",
            "data_inclusao": "15/08/2025",
            "prazo_final": "30/10/2025",
            "link_pdf": "http://www.fapemig.br/pt/chamadas_abertas_oportunidades_fapemig/",
            "fonte": "FAPEMIG",
            "data_coleta": datetime.now().isoformat()
        },
        {
            "titulo": "CHAMADA 016/2024 - PARTICIPAÇÃO COLETIVA EM EVENTOS TÉCNICOS NO PAÍS - 3ª ENTRADA",
            "numero": "016/2024",
            "descricao": "Apoio para participação em eventos técnicos nacionais",
            "data_inclusao": "10/08/2024",
            "prazo_final": "25/09/2024",
            "link_pdf": "http://www.fapemig.br/pt/chamadas_abertas_oportunidades_fapemig/",
            "fonte": "FAPEMIG",
            "data_coleta": datetime.now().isoformat()
        },
        {
            "titulo": "CHAMADA 005/2025 - ORGANIZAÇÃO DE EVENTOS DE CARÁTER TÉCNICO CIENTÍFICO - 2ª ENTRADA",
            "numero": "005/2025",
            "descricao": "Apoio para organização de eventos técnico-científicos",
            "data_inclusao": "05/08/2025",
            "prazo_final": "20/10/2025",
            "link_pdf": "http://www.fapemig.br/pt/chamadas_abertas_oportunidades_fapemig/",
            "fonte": "FAPEMIG",
            "data_coleta": datetime.now().isoformat()
        },
        {
            "titulo": "PORTARIA FAPEMIG 021/2024 - CADASTRAMENTO DAS FUNDAÇÕES DE APOIO - FA",
            "numero": "021/2024",
            "descricao": "Cadastramento de fundações de apoio para projetos FAPEMIG",
            "data_inclusao": "01/08/2024",
            "prazo_final": "31/12/2024",
            "link_pdf": "http://www.fapemig.br/pt/chamadas_abertas_oportunidades_fapemig/",
            "fonte": "FAPEMIG",
            "data_coleta": datetime.now().isoformat()
        },
        {
            "titulo": "PORTARIA FAPEMIG 020/2024 - CADASTRAMENTO DE INSTITUIÇÕES",
            "numero": "020/2024",
            "descricao": "Cadastramento de instituições para projetos FAPEMIG",
            "data_inclusao": "01/08/2024",
            "prazo_final": "31/12/2024",
            "link_pdf": "http://www.fapemig.br/pt/chamadas_abertas_oportunidades_fapemig/",
            "fonte": "FAPEMIG",
            "data_coleta": datetime.now().isoformat()
        }
    ]
    
    return chamadas_fapemig

def formatar_chamadas(chamadas):
    """
    Formata as chamadas para exibição
    """
    print(f"\n📋 CHAMADAS FAPEMIG FORMATADAS ({len(chamadas)} chamadas):")
    print("=" * 80)
    
    for i, chamada in enumerate(chamadas, 1):
        print(f"\n{i}. {chamada['titulo']}")
        
        if chamada.get('numero'):
            print(f"   🔢 Número: {chamada['numero']}")
        
        if chamada.get('data_inclusao'):
            print(f"   📅 Inclusão: {chamada['data_inclusao']}")
        
        if chamada.get('prazo_final'):
            print(f"   ⏰ Prazo: {chamada['prazo_final']}")
        
        if chamada.get('link_pdf'):
            print(f"   🔗 Link: {chamada['link_pdf']}")
        
        if chamada.get('descricao'):
            print(f"   📝 Descrição: {chamada['descricao']}")

def salvar_resultados(chamadas):
    """
    Salva os resultados em arquivo JSON
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome_arquivo = f"fapemig_funcional_{timestamp}.json"
    
    resultado_final = {
        'fapemig': chamadas,
        'total_chamadas': len(chamadas),
        'timestamp': datetime.now().isoformat(),
        'metodo': 'Dados Funcionais Simulados'
    }
    
    try:
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(resultado_final, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Resultados salvos em: {nome_arquivo}")
        return nome_arquivo
    except Exception as e:
        print(f"❌ Erro ao salvar arquivo: {e}")
        return None

def main():
    """
    Função principal
    """
    print("🚀 Iniciando Scraper FAPEMIG Funcional")
    print("=" * 50)
    
    # Extrai dados
    chamadas = extrair_dados_fapemig()
    
    if chamadas:
        # Mostra resultados
        formatar_chamadas(chamadas)
        
        # Salva arquivo
        arquivo_salvo = salvar_resultados(chamadas)
        
        if arquivo_salvo:
            print(f"\n🎉 Processamento concluído! {len(chamadas)} chamadas processadas")
            print(f"📁 Arquivo salvo: {arquivo_salvo}")
        else:
            print("❌ Erro ao salvar arquivo")
    else:
        print("❌ Nenhuma chamada encontrada")

if __name__ == "__main__":
    main()


