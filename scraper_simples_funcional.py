#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Scraper Simples e Funcional
Busca dados reais de CNPq, FAPEMIG e UFJF
"""

import json
import re
import time
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.parse import urljoin
from html.parser import HTMLParser

class SimpleHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.texts = []
        self.current_tag = None
        
    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        if tag == 'a':
            for attr in attrs:
                if attr[0] == 'href':
                    self.links.append(attr[1])
    
    def handle_data(self, data):
        if data.strip():
            self.texts.append(data.strip())

def extrair_data_do_texto(texto):
    """Extrai datas do texto usando regex"""
    if not texto:
        return None
        
    # Padrões de data
    padroes = [
        r'(\d{1,2}/\d{1,2}/\d{4})',  # DD/MM/AAAA
        r'(\d{1,2}/\d{1,2}/\d{2})',  # DD/MM/AA
        r'(\d{1,2}\.\d{1,2}\.\d{4})', # DD.MM.AAAA
        r'(\d{4}-\d{1,2}-\d{1,2})'   # AAAA-MM-DD
    ]
    
    for padrao in padroes:
        match = re.search(padrao, texto)
        if match:
            return match.group(1)
    return None

def extrair_numero_chamada(texto):
    """Extrai número da chamada do texto"""
    if not texto:
        return None
        
    # Padrões para números de chamada
    padroes = [
        r'(\d{3,4}/\d{4})',  # 011/2025
        r'(\d{1,2}/\d{4})',  # 12/2025
        r'(\d{4,5})',         # 1874
        r'(\d{1,2})'          # 08
    ]
    
    for padrao in padroes:
        match = re.search(padrao, texto)
        if match:
            return match.group(1)
    return None

def buscar_site(url, user_agent=None):
    """Busca conteúdo de um site"""
    try:
        if not user_agent:
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        
        req = Request(url, headers={'User-Agent': user_agent})
        with urlopen(req, timeout=10) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"❌ Erro ao acessar {url}: {e}")
        return None

def extrair_chamadas_cnpq():
    """Extrai chamadas do CNPq"""
    print("🔬 Buscando chamadas do CNPq...")
    
    try:
        url = "http://memoria2.cnpq.br/web/guest/chamadas-publicas"
        html = buscar_site(url)
        
        if not html:
            return []
        
        # Busca por padrões de chamadas
        chamadas = []
        
        # Padrões comuns em sites CNPq
        padroes_chamada = [
            r'CHAMADA[^<]*?(\d{1,2}/\d{4})[^<]*?',
            r'EDITAL[^<]*?(\d{1,2}/\d{4})[^<]*?',
            r'(\d{1,2}/\d{4})[^<]*?CHAMADA[^<]*?',
            r'(\d{1,2}/\d{4})[^<]*?EDITAL[^<]*?'
        ]
        
        for padrao in padroes_chamada:
            matches = re.finditer(padrao, html, re.IGNORECASE)
            for match in matches:
                numero = match.group(1)
                contexto = html[max(0, match.start()-100):match.end()+100]
                
                # Limpa o contexto
                contexto_limpo = re.sub(r'<[^>]+>', ' ', contexto)
                contexto_limpo = re.sub(r'\s+', ' ', contexto_limpo).strip()
                
                if len(contexto_limpo) > 50:
                    chamada = {
                        'titulo': contexto_limpo[:200] + "..." if len(contexto_limpo) > 200 else contexto_limpo,
                        'numero': numero,
                        'prazo_final': extrair_data_do_texto(contexto_limpo),
                        'link_pdf': url,
                        'fonte': 'CNPq',
                        'data_coleta': datetime.now().isoformat()
                    }
                    chamadas.append(chamada)
        
        # Remove duplicatas
        chamadas_unicas = []
        numeros_vistos = set()
        for chamada in chamadas:
            if chamada['numero'] not in numeros_vistos:
                chamadas_unicas.append(chamada)
                numeros_vistos.add(chamada['numero'])
        
        print(f"✅ CNPq: {len(chamadas_unicas)} chamadas encontradas")
        return chamadas_unicas[:10]  # Limita a 10 resultados
        
    except Exception as e:
        print(f"❌ Erro ao extrair CNPq: {e}")
        return []

def extrair_chamadas_fapemig():
    """Extrai chamadas da FAPEMIG"""
    print("🏛️ Buscando chamadas da FAPEMIG...")
    
    try:
        url = "http://www.fapemig.br/pt/chamadas_abertas_oportunidades_fapemig/"
        html = buscar_site(url)
        
        if not html:
            return []
        
        # Busca por padrões de chamadas FAPEMIG
        chamadas = []
        
        padroes_chamada = [
            r'CHAMADA[^<]*?(\d{3}/\d{4})[^<]*?',
            r'(\d{3}/\d{4})[^<]*?CHAMADA[^<]*?',
            r'EDITAL[^<]*?(\d{3}/\d{4})[^<]*?',
            r'(\d{3}/\d{4})[^<]*?EDITAL[^<]*?'
        ]
        
        for padrao in padroes_chamada:
            matches = re.finditer(padrao, html, re.IGNORECASE)
            for match in matches:
                numero = match.group(1)
                contexto = html[max(0, match.start()-100):match.end()+100]
                
                # Limpa o contexto
                contexto_limpo = re.sub(r'<[^>]+>', ' ', contexto)
                contexto_limpo = re.sub(r'\s+', ' ', contexto_limpo).strip()
                
                if len(contexto_limpo) > 50:
                    chamada = {
                        'titulo': contexto_limpo[:200] + "..." if len(contexto_limpo) > 200 else contexto_limpo,
                        'numero': numero,
                        'prazo_final': extrair_data_do_texto(contexto_limpo),
                        'link_pdf': url,
                        'fonte': 'FAPEMIG',
                        'data_coleta': datetime.now().isoformat()
                    }
                    chamadas.append(chamada)
        
        # Remove duplicatas
        chamadas_unicas = []
        numeros_vistos = set()
        for chamada in chamadas:
            if chamada['numero'] not in numeros_vistos:
                chamadas_unicas.append(chamada)
                numeros_vistos.add(chamada['numero'])
        
        print(f"✅ FAPEMIG: {len(chamadas_unicas)} chamadas encontradas")
        return chamadas_unicas[:10]  # Limita a 10 resultados
        
    except Exception as e:
        print(f"❌ Erro ao extrair FAPEMIG: {e}")
        return []

def extrair_chamadas_ufjf():
    """Extrai chamadas da UFJF"""
    print("🎓 Buscando chamadas da UFJF...")
    
    try:
        url = "https://www2.ufjf.br/propp/editais/"
        html = buscar_site(url)
        
        if not html:
            return []
        
        # Busca por padrões de editais UFJF
        chamadas = []
        
        padroes_edital = [
            r'EDITAL[^<]*?(\d{4})[^<]*?',
            r'(\d{4})[^<]*?EDITAL[^<]*?',
            r'EDITAL[^<]*?(\d{1,2}/\d{4})[^<]*?',
            r'(\d{1,2}/\d{4})[^<]*?EDITAL[^<]*?'
        ]
        
        for padrao in padroes_edital:
            matches = re.finditer(padrao, html, re.IGNORECASE)
            for match in matches:
                numero = match.group(1)
                contexto = html[max(0, match.start()-100):match.end()+100]
                
                # Limpa o contexto
                contexto_limpo = re.sub(r'<[^>]+>', ' ', contexto)
                contexto_limpo = re.sub(r'\s+', ' ', contexto_limpo).strip()
                
                if len(contexto_limpo) > 50:
                    chamada = {
                        'titulo': contexto_limpo[:200] + "..." if len(contexto_limpo) > 200 else contexto_limpo,
                        'numero': numero,
                        'prazo_final': extrair_data_do_texto(contexto_limpo),
                        'link_pdf': url,
                        'fonte': 'UFJF',
                        'data_coleta': datetime.now().isoformat()
                    }
                    chamadas.append(chamada)
        
        # Remove duplicatas
        chamadas_unicas = []
        numeros_vistos = set()
        for chamada in chamadas:
            if chamada['numero'] not in numeros_vistos:
                chamadas_unicas.append(chamada)
                numeros_vistos.add(chamada['numero'])
        
        print(f"✅ UFJF: {len(chamadas_unicas)} chamadas encontradas")
        return chamadas_unicas[:10]  # Limita a 10 resultados
        
    except Exception as e:
        print(f"❌ Erro ao extrair UFJF: {e}")
        return []

def executar_scraping_completo():
    """Executa o scraping de todas as fontes"""
    print("🚀 Iniciando scraping completo...")
    print("=" * 50)
    
    resultados = {
        'cnpq': [],
        'fapemig': [],
        'ufjf': []
    }
    
    try:
        # Extrai dados de todas as fontes
        resultados['cnpq'] = extrair_chamadas_cnpq()
        resultados['fapemig'] = extrair_chamadas_fapemig()
        resultados['ufjf'] = extrair_chamadas_ufjf()
        
        return resultados
        
    except Exception as e:
        print(f"❌ Erro durante scraping: {e}")
        return resultados

def salvar_resultados(resultados):
    """Salva os resultados em arquivo JSON"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"dados_reais_simples_{timestamp}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Resultados salvos em: {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ Erro ao salvar: {e}")
        return None

def mostrar_resumo(resultados):
    """Mostra resumo dos resultados"""
    print("\n📊 RESUMO DOS RESULTADOS:")
    print("=" * 50)
    
    total_geral = 0
    for fonte, chamadas in resultados.items():
        print(f"{fonte.upper()}: {len(chamadas)} chamadas")
        total_geral += len(chamadas)
    
    print(f"\n🎯 TOTAL GERAL: {total_geral} chamadas")
    
    if total_geral > 0:
        print("\n📋 Exemplos de chamadas encontradas:")
        for fonte, chamadas in resultados.items():
            if chamadas:
                print(f"\n{fonte.upper()}:")
                for i, chamada in enumerate(chamadas[:2], 1):
                    print(f"  {i}. {chamada['titulo'][:80]}...")

def main():
    """Função principal"""
    print("🚀 Scraper Simples e Funcional")
    print("=" * 50)
    
    # Executa o scraping
    resultados = executar_scraping_completo()
    
    # Salva os resultados
    arquivo = salvar_resultados(resultados)
    
    # Mostra resumo
    mostrar_resumo(resultados)
    
    if arquivo:
        print(f"\n🎉 Scraping concluído com sucesso!")
        print(f"📁 Arquivo salvo: {arquivo}")
        print("\n💡 Use este arquivo para gerar relatórios reais!")
    else:
        print("❌ Falha ao salvar resultados")

if __name__ == "__main__":
    main()
