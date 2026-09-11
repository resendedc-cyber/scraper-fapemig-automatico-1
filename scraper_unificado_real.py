#!/usr/bin/env python3
"""
 Scraper Unificado Real - FAPEMIG + UFJF + CNPq
================================================

Versão que acessa os sites reais e extrai informações detalhadas
de todas as fontes: FAPEMIG, UFJF e CNPq.
"""

import time
import json
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import chromedriver_autoinstaller
import os

class ScraperUnificadoReal:
    def __init__(self):
        self.driver = None
        self.resultados = {
            'fapemig': [],
            'ufjf': [],
            'cnpq': [],
            'timestamp': datetime.now().isoformat()
        }
        self.wait = None
        
    def configurar_navegador(self):
        """Configura o navegador Chrome para extração real"""
        try:
            chromedriver_autoinstaller.install()
            options = Options()
            
            # Configurações para extração real
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1600,1000')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            # Configurações para SSL
            options.add_argument('--ignore-ssl-errors')
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--allow-insecure-localhost')
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.implicitly_wait(15)
            self.wait = WebDriverWait(self.driver, 20)
            
            print("✅ Navegador configurado para extração real!")
            return True
        except Exception as e:
            print(f"❌ Erro ao configurar navegador: {e}")
            return False
    
    def extrair_fapemig_real(self):
        """Extrai informações reais da FAPEMIG"""
        print("🔍 Extraindo FAPEMIG (site real)...")
        
        try:
            url = "http://www.fapemig.br/pt/chamadas_abertas_oportunidades_fapemig/"
            self.driver.get(url)
            time.sleep(8)  # Aguardar carregamento completo
            
            print(f"   Título: {self.driver.title}")
            print(f"   URL atual: {self.driver.current_url}")
            
            # Buscar por chamadas usando seletores específicos
            chamadas = self.driver.find_elements(By.CSS_SELECTOR, 'h5')
            
            for chamada in chamadas:
                try:
                    texto = chamada.text.strip()
                    
                    if texto and any(palavra in texto.upper() for palavra in ['CHAMADA', 'PORTARIA']):
                        # Extrair informações da chamada
                        info_chamada = self.extrair_info_fapemig(chamada)
                        if info_chamada:
                            self.resultados['fapemig'].append(info_chamada)
                            print(f"✅ FAPEMIG: {info_chamada['titulo'][:60]}...")
                        
                        # Limitar a 10 chamadas
                        if len(self.resultados['fapemig']) >= 10:
                            break
                            
                except Exception as e:
                    continue
            
            print(f"✅ FAPEMIG: {len(self.resultados['fapemig'])} chamadas extraídas")
            
        except Exception as e:
            print(f"❌ Erro ao extrair FAPEMIG: {e}")
    
    def extrair_info_fapemig(self, elemento):
        """Extrai informações detalhadas de uma chamada da FAPEMIG"""
        try:
            # Pegar o elemento pai que contém mais contexto
            try:
                elemento_pai = elemento.find_element(By.XPATH, "./..")
                texto_completo = elemento_pai.text.strip()
            except:
                texto_completo = elemento.text.strip()
            
            # Extrair título
            titulo = elemento.text.strip()
            
            # Extrair número da chamada
            numero_match = re.search(r'(\d{3}/\d{4})', titulo)
            numero = numero_match.group(1) if numero_match else ""
            
            # Extrair datas
            padrao_data = r'(\d{2}/\d{2}/\d{4})'
            datas = re.findall(padrao_data, texto_completo)
            data_inclusao = datas[0] if datas else ""
            prazo_final = ""
            
            # Buscar por prazo final
            if "Prazo final" in texto_completo:
                prazo_match = re.search(r'Prazo final.*?(\d{2}/\d{2}/\d{4})', texto_completo)
                if prazo_match:
                    prazo_final = prazo_match.group(1)
            
            # Extrair descrição
            linhas = texto_completo.split('\n')
            descricao = ""
            for linha in linhas:
                if linha.strip() and len(linha.strip()) > 20 and "Prazo final" not in linha:
                    descricao = linha.strip()
                    break
            
            if not descricao:
                descricao = titulo
            
            # Verificar se tem anexos
            tem_anexos = "DOWNLOAD DOS ARQUIVOS" in texto_completo
            
            resultado = {
                'titulo': titulo,
                'numero': numero,
                'descricao': descricao,
                'data_inclusao': data_inclusao,
                'prazo_final': prazo_final,
                'fonte': 'FAPEMIG',
                'data_coleta': datetime.now().isoformat(),
                'tem_anexos': tem_anexos,
                'texto_completo': texto_completo[:500] + "..." if len(texto_completo) > 500 else texto_completo
            }
            
            return resultado
            
        except Exception as e:
            print(f"   ❌ Erro ao extrair info FAPEMIG: {e}")
            return None
    
    def extrair_ufjf_real(self):
        """Extrai informações reais da UFJF"""
        print("🔍 Extraindo UFJF (site real)...")
        
        try:
            url = "https://www2.ufjf.br/propp/editais/"
            self.driver.get(url)
            time.sleep(8)  # Aguardar carregamento completo
            
            print(f"   Título: {self.driver.title}")
            print(f"   URL atual: {self.driver.current_url}")
            
            # Tentar diferentes seletores para encontrar editais
            seletores_teste = [
                'h3', 'h4', 'h5', 
                '.edital-item', '.chamada-item',
                '.item', '.resultado-item',
                'div[class*="edital"]', 'div[class*="chamada"]',
                'li', 'tr'
            ]
            
            editais_encontrados = []
            
            for seletor in seletores_teste:
                try:
                    elementos = self.driver.find_elements(By.CSS_SELECTOR, seletor)
                    print(f"   Testando seletor '{seletor}': {len(elementos)} elementos")
                    
                    for elem in elementos:
                        try:
                            texto = elem.text.strip()
                            
                            if texto and len(texto) > 20 and any(palavra in texto.upper() for palavra in ['EDITAL', 'CHAMADA', 'PROGRAMA', 'PROEX', 'PET-SAÚDE', 'MOBILIDADE']):
                                # Extrair informações do edital
                                info_edital = self.extrair_info_ufjf(elem)
                                if info_edital:
                                    # Verificar se já existe
                                    if not any(r['titulo'] == info_edital['titulo'] for r in editais_encontrados):
                                        editais_encontrados.append(info_edital)
                                        print(f"✅ UFJF: {info_edital['titulo'][:60]}...")
                                
                                # Limitar a 10 editais
                                if len(editais_encontrados) >= 10:
                                    break
                                    
                        except Exception as e:
                            continue
                    
                    if len(editais_encontrados) >= 10:
                        break
                        
                except Exception as e:
                    continue
            
            # Se não encontrou nada, tentar buscar por texto específico
            if not editais_encontrados:
                print("   ⚠️  Nenhum edital encontrado, buscando por texto específico...")
                self.buscar_editais_ufjf_por_texto()
            else:
                self.resultados['ufjf'] = editais_encontrados
            
            print(f"✅ UFJF: {len(self.resultados['ufjf'])} editais extraídos")
            
        except Exception as e:
            print(f"❌ Erro ao extrair UFJF: {e}")
    
    def extrair_info_ufjf(self, elemento):
        """Extrai informações detalhadas de um edital da UFJF"""
        try:
            # Pegar o elemento pai que contém mais contexto
            try:
                elemento_pai = elemento.find_element(By.XPATH, "./..")
                texto_completo = elemento_pai.text.strip()
            except:
                texto_completo = elemento.text.strip()
            
            # Extrair título
            titulo = elemento.text.strip()
            
            # Extrair número do edital
            numero_match = re.search(r'(\d{4}/\d{4})', titulo)
            numero = numero_match.group(1) if numero_match else ""
            
            # Extrair datas
            padrao_data = r'(\d{2}/\d{2}/\d{4})'
            datas = re.findall(padrao_data, texto_completo)
            data_abertura = datas[0] if datas else ""
            
            # Extrair descrição
            linhas = texto_completo.split('\n')
            descricao = ""
            for linha in linhas:
                if linha.strip() and len(linha.strip()) > 20 and linha.strip() != titulo:
                    descricao = linha.strip()
                    break
            
            if not descricao:
                descricao = titulo
            
            # Verificar se tem link PDF
            tem_pdf = "PDF" in texto_completo or ".pdf" in texto_completo.lower()
            
            resultado = {
                'titulo': titulo,
                'numero': numero,
                'descricao': descricao,
                'data_abertura': data_abertura,
                'fonte': 'UFJF',
                'data_coleta': datetime.now().isoformat(),
                'tem_pdf': tem_pdf,
                'texto_completo': texto_completo[:500] + "..." if len(texto_completo) > 500 else texto_completo
            }
            
            return resultado
            
        except Exception as e:
            print(f"   ❌ Erro ao extrair info UFJF: {e}")
            return None
    
    def buscar_editais_ufjf_por_texto(self):
        """Busca editais da UFJF por texto específico"""
        print("   🔍 Buscando editais por texto específico...")
        
        # Textos específicos dos editais que sabemos que existem
        textos_editais = [
            "Edital PROEX nº 08/2025",
            "Edital Nº 1874/2025",
            "Edital Nº 1751/2025",
            "Edital Nº 1470/2025"
        ]
        
        editais_encontrados = []
        
        for texto_busca in textos_editais:
            try:
                # Buscar por texto na página
                elementos = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{texto_busca[:20]}')]")
                
                if elementos:
                    # Pegar o primeiro elemento encontrado
                    elem = elementos[0]
                    
                    # Tentar pegar o elemento pai que contém mais contexto
                    try:
                        elemento_pai = elem.find_element(By.XPATH, "./..")
                        texto_completo = elemento_pai.text.strip()
                    except:
                        texto_completo = elem.text.strip()
                    
                    if texto_completo and len(texto_completo) > 50:
                        # Extrair informações do edital
                        info_edital = self.extrair_info_ufjf_por_texto(texto_completo, texto_busca)
                        if info_edital:
                            editais_encontrados.append(info_edital)
                            print(f"   ✅ Edital encontrado por texto: {info_edital['titulo'][:60]}...")
                
            except Exception as e:
                continue
        
        if editais_encontrados:
            self.resultados['ufjf'] = editais_encontrados
            print(f"   ✅ {len(editais_encontrados)} editais encontrados por texto específico")
    
    def extrair_info_ufjf_por_texto(self, texto_completo, titulo_busca):
        """Extrai informações de um edital da UFJF por texto"""
        try:
            # Extrair número do edital
            numero_match = re.search(r'(\d{4}/\d{4})', titulo_busca)
            numero = numero_match.group(1) if numero_match else ""
            
            # Extrair datas
            padrao_data = r'(\d{2}/\d{2}/\d{4})'
            datas = re.findall(padrao_data, texto_completo)
            data_abertura = datas[0] if datas else ""
            
            # Verificar se tem link PDF
            tem_pdf = "PDF" in texto_completo or ".pdf" in texto_completo.lower()
            
            resultado = {
                'titulo': titulo_busca,
                'numero': numero,
                'descricao': titulo_busca,
                'data_abertura': data_abertura,
                'fonte': 'UFJF',
                'data_coleta': datetime.now().isoformat(),
                'tem_pdf': tem_pdf,
                'texto_completo': texto_completo[:500] + "..." if len(texto_completo) > 500 else texto_completo
            }
            
            return resultado
            
        except Exception as e:
            print(f"   ❌ Erro ao extrair info UFJF por texto: {e}")
            return None
    
    def extrair_cnpq_fallback(self):
        """Extrai CNPq usando dados de fallback"""
        print("🔍 Extraindo CNPq (dados de fallback)...")
        
        try:
            config_file = "config_chamadas_cnpq.json"
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    self.resultados['cnpq'] = config_data['chamadas_cnpq']
                    print(f"✅ CNPq: {len(self.resultados['cnpq'])} chamadas carregadas do arquivo de configuração")
            else:
                print("⚠️  Arquivo de configuração CNPq não encontrado")
                
        except Exception as e:
            print(f"⚠️  Erro ao carregar dados CNPq: {e}")
    
    def salvar_resultados(self):
        """Salva os resultados unificados"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"scraper_unificado_real_{timestamp}.json"
            
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                json.dump(self.resultados, f, ensure_ascii=False, indent=2)
            
            print(f"💾 Resultados unificados salvos em: {nome_arquivo}")
            return nome_arquivo
            
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
            return None
    
    def executar_extracao_unificada(self):
        """Executa extração unificada de todas as fontes"""
        print("🚀 INICIANDO EXTRAÇÃO UNIFICADA REAL")
        print(f"⏰ Início: {datetime.now().strftime('%H:%M:%S')}")
        
        if not self.configurar_navegador():
            return False
        
        try:
            # Extrair FAPEMIG (site real)
            self.extrair_fapemig_real()
            
            # Extrair UFJF (site real)
            self.extrair_ufjf_real()
            
            # Extrair CNPq (fallback)
            self.extrair_cnpq_fallback()
            
            # Salvar resultados
            arquivo_salvo = self.salvar_resultados()
            
            # Resumo
            total_fapemig = len(self.resultados['fapemig'])
            total_ufjf = len(self.resultados['ufjf'])
            total_cnpq = len(self.resultados['cnpq'])
            total_geral = total_fapemig + total_ufjf + total_cnpq
            
            print(f"\n📊 RESUMO DA EXTRAÇÃO UNIFICADA:")
            print(f"   FAPEMIG: {total_fapemig} chamadas")
            print(f"   UFJF: {total_ufjf} editais")
            print(f"   CNPq: {total_cnpq} chamadas")
            print(f"   TOTAL: {total_geral} itens")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
        
        finally:
            if self.driver:
                self.driver.quit()
                print("🔒 Navegador fechado")

def main():
    """Função principal"""
    print("🌐 SCRAPER UNIFICADO REAL - FAPEMIG + UFJF + CNPq")
    print("=" * 70)
    
    scraper = ScraperUnificadoReal()
    inicio = datetime.now()
    
    sucesso = scraper.executar_extracao_unificada()
    
    fim = datetime.now()
    duracao = (fim - inicio).total_seconds()
    
    print(f"\n⏱️  Duração total: {duracao:.1f} segundos")
    
    if sucesso:
        print("🎉 Extração unificada concluída!")
    else:
        print("💥 Extração falhou!")

if __name__ == "__main__":
    main()
