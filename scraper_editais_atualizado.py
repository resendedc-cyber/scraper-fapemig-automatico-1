#!/usr/bin/env python3
"""
Scraper Atualizado para Editais e Chamadas
==========================================

Sistema robusto que coleta informações completas de editais dos sites:
- UFJF (Universidade Federal de Juiz de Fora)
- FAPEMIG (Fundação de Amparo à Pesquisa de Minas Gerais)
- CNPq (Conselho Nacional de Desenvolvimento Científico e Tecnológico)

Extrai:
- Título da chamada/edital
- Breve descrição
- Link para o PDF (quando existir)
- Data limite de submissão
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
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import chromedriver_autoinstaller

class ScraperEditaisAtualizado:
    def __init__(self):
        self.driver = None
        self.resultados = {
            'ufjf': [],
            'fapemig': [],
            'cnpq': [],
            'timestamp': datetime.now().isoformat()
        }
        self.wait = None
        
    def configurar_navegador(self):
        """Configura o navegador Chrome com opções otimizadas"""
        try:
            chromedriver_autoinstaller.install()
            options = Options()
            # options.add_argument('--headless')  # Descomente para modo headless
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.implicitly_wait(10)
            self.wait = WebDriverWait(self.driver, 15)
            
            print("✅ Navegador configurado com sucesso!")
            return True
        except Exception as e:
            print(f"❌ Erro ao configurar navegador: {e}")
            return False
    
    def extrair_ufjf(self):
        """Extrai editais da UFJF"""
        print("\n🔍 Extraindo editais da UFJF...")
        
        try:
            self.driver.get('https://www2.ufjf.br/propp/editais/')
            time.sleep(3)
            
            # Aguardar carregamento da página
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Buscar por links que contenham editais
            editais = self.driver.find_elements(By.CSS_SELECTOR, 'a')
            
            for edital in editais:
                try:
                    texto = edital.text.strip()
                    href = edital.get_attribute('href')
                    
                    # Verificar se é um edital válido
                    if (texto and href and 
                        any(palavra in texto.lower() for palavra in ['edital', 'chamada', 'seleção', 'concurso']) and
                        (href.startswith('http') and ('pdf' in href.lower() or 'edital' in href.lower() or 'chamada' in href.lower()))):
                        
                        # Extrair descrição (geralmente já está no texto)
                        desc = texto
                        
                        # Buscar por datas no texto
                        data_match = re.search(r'\d{2}/\d{2}/\d{4}', texto)
                        data_limite = data_match.group(0) if data_match else ""
                        
                        # Buscar por outras datas relacionadas
                        if not data_limite:
                            # Buscar por padrões de data comuns
                            padroes_data = [
                                r'até \d{2}/\d{2}/\d{4}',
                                r'até dia \d{2}/\d{2}/\d{4}',
                                r'prazo: \d{2}/\d{2}/\d{4}',
                                r'encerra em \d{2}/\d{2}/\d{4}'
                            ]
                            
                            for padrao in padroes_data:
                                match = re.search(padrao, texto, re.IGNORECASE)
                                if match:
                                    data_limite = re.search(r'\d{2}/\d{2}/\d{4}', match.group(0)).group(0)
                                    break
                        
                        resultado = {
                            'titulo': texto,
                            'descricao': desc,
                            'link_pdf': href,
                            'data_limite': data_limite,
                            'fonte': 'UFJF',
                            'data_coleta': datetime.now().isoformat()
                        }
                        
                        self.resultados['ufjf'].append(resultado)
                        
                        print(f"[UFJF] ✅ Encontrado:")
                        print(f"   Título: {texto}")
                        print(f"   PDF: {href}")
                        print(f"   Data limite: {data_limite}")
                        print("   ---")
                        
                except Exception as e:
                    print(f"   ⚠️ Erro ao processar edital UFJF: {e}")
                    continue
            
            print(f"✅ UFJF: {len(self.resultados['ufjf'])} editais encontrados")
            
        except Exception as e:
            print(f"❌ Erro ao extrair UFJF: {e}")
    
    def extrair_fapemig(self):
        """Extrai oportunidades da FAPEMIG"""
        print("\n🔍 Extraindo oportunidades da FAPEMIG...")
        
        try:
            self.driver.get('http://www.fapemig.br/pt/chamadas_abertas_oportunidades_fapemig/?hl=pt-BR')
            time.sleep(4)
            
            # Aguardar carregamento da página
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Estratégia 1: Buscar por títulos de chamadas
            chamadas = self.driver.find_elements(By.TAG_NAME, "h5")
            
            for chamada in chamadas:
                try:
                    texto = chamada.text.strip()
                    
                    if (texto and 
                        any(palavra in texto.upper() for palavra in ['CHAMADA', 'PORTARIA', 'CREDENCIAMENTO', 'EDITAL', 'OPORTUNIDADE'])):
                        
                        # Buscar descrição próxima ao título
                        desc = ""
                        try:
                            # Tentar encontrar descrição em elementos próximos
                            parent = chamada.find_element(By.XPATH, "..")
                            elementos_proximos = parent.find_elements(By.XPATH, ".//*[position()<=3]")
                            
                            for elem in elementos_proximos:
                                if elem != chamada and elem.text.strip() and len(elem.text.strip()) > 20:
                                    desc = elem.text.strip()
                                    break
                        except:
                            pass
                        
                        # Buscar link para PDF ou detalhes
                        link_pdf = ""
                        link_detalhes = ""
                        
                        try:
                            # Buscar por links próximos
                            links_proximos = chamada.find_elements(By.XPATH, "following-sibling::a")
                            for link in links_proximos:
                                href = link.get_attribute('href')
                                if href:
                                    if href.endswith('.pdf') or 'pdf' in href.lower():
                                        link_pdf = href
                                    elif any(palavra in href.lower() for palavra in ['detalhes', 'ver', 'abrir', 'chamada']):
                                        link_detalhes = href
                        except:
                            pass
                        
                        # Se não encontrou PDF, tentar buscar no texto da chamada
                        if not link_pdf:
                            try:
                                link_elem = chamada.find_element(By.XPATH, ".//a")
                                href = link_elem.get_attribute('href')
                                if href and (href.endswith('.pdf') or 'pdf' in href.lower()):
                                    link_pdf = href
                            except:
                                pass
                        
                        # Extrair datas do texto
                        data_limite = ""
                        if texto or desc:
                            padroes_data = [
                                r'\d{2}/\d{2}/\d{4}',
                                r'\d{2} de \w+ de \d{4}',
                                r'até \d{2}/\d{2}/\d{4}',
                                r'prazo: \d{2}/\d{2}/\d{4}'
                            ]
                            
                            for padrao in padroes_data:
                                match = re.search(padrao, texto + " " + desc, re.IGNORECASE)
                                if match:
                                    data_limite = match.group(0)
                                    break
                        
                        resultado = {
                            'titulo': texto,
                            'descricao': desc,
                            'link_pdf': link_pdf,
                            'link_detalhes': link_detalhes,
                            'data_limite': data_limite,
                            'fonte': 'FAPEMIG',
                            'data_coleta': datetime.now().isoformat()
                        }
                        
                        self.resultados['fapemig'].append(resultado)
                        
                        print(f"[FAPEMIG] ✅ Encontrado:")
                        print(f"   Título: {texto}")
                        print(f"   Descrição: {desc[:100]}..." if len(desc) > 100 else f"   Descrição: {desc}")
                        print(f"   PDF: {link_pdf}" if link_pdf else "   PDF: Não encontrado")
                        print(f"   Detalhes: {link_detalhes}" if link_detalhes else "   Detalhes: Não encontrado")
                        print(f"   Data limite: {data_limite}")
                        print("   ---")
                        
                except Exception as e:
                    print(f"   ⚠️ Erro ao processar chamada FAPEMIG: {e}")
                    continue
            
            # Estratégia 2: Buscar por outros elementos que possam conter chamadas
            try:
                outros_elementos = self.driver.find_elements(By.CSS_SELECTOR, "h3, h4, .chamada, .oportunidade")
                
                for elem in outros_elementos:
                    try:
                        texto = elem.text.strip()
                        
                        if (texto and len(texto) > 10 and 
                            any(palavra in texto.lower() for palavra in ['chamada', 'edital', 'oportunidade', 'programa'])):
                            
                            # Verificar se já foi processado
                            if not any(r['titulo'] == texto for r in self.resultados['fapemig']):
                                
                                # Buscar links próximos
                                link_pdf = ""
                                try:
                                    link_elem = elem.find_element(By.XPATH, ".//a")
                                    href = link_elem.get_attribute('href')
                                    if href and (href.endswith('.pdf') or 'pdf' in href.lower()):
                                        link_pdf = href
                                except:
                                    pass
                                
                                resultado = {
                                    'titulo': texto,
                                    'descricao': "",
                                    'link_pdf': link_pdf,
                                    'link_detalhes': "",
                                    'data_limite': "",
                                    'fonte': 'FAPEMIG',
                                    'data_coleta': datetime.now().isoformat()
                                }
                                
                                self.resultados['fapemig'].append(resultado)
                                
                    except Exception as e:
                        continue
                        
            except Exception as e:
                print(f"   ⚠️ Erro na estratégia alternativa FAPEMIG: {e}")
            
            print(f"✅ FAPEMIG: {len(self.resultados['fapemig'])} oportunidades encontradas")
            
        except Exception as e:
            print(f"❌ Erro ao extrair FAPEMIG: {e}")
    
    def extrair_cnpq(self):
        """Extrai chamadas do CNPq"""
        print("\n🔍 Extraindo chamadas do CNPq...")
        
        try:
            self.driver.get('http://memoria2.cnpq.br/web/guest/chamadas-publicas')
            time.sleep(4)
            
            # Aguardar carregamento da página
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Estratégia 1: Buscar por títulos h4
            h4s = self.driver.find_elements(By.TAG_NAME, "h4")
            
            for h4 in h4s:
                try:
                    texto = h4.text.strip()
                    
                    if (texto and 
                        any(palavra in texto.upper() for palavra in ['CHAMADA', 'EDITAL', 'OPORTUNIDADE', 'PROGRAMA', 'BOLSA'])):
                        
                        # Buscar descrição e links próximos
                        desc = ""
                        link_pdf = ""
                        
                        try:
                            parent = h4.find_element(By.XPATH, "..")
                            
                            # Buscar por descrição em elementos próximos
                            elementos_proximos = parent.find_elements(By.XPATH, ".//*")
                            
                            for elem in elementos_proximos:
                                try:
                                    # Buscar por PDFs
                                    if elem.tag_name == 'a':
                                        href = elem.get_attribute('href')
                                        if href and (href.endswith('.pdf') or 'pdf' in href.lower()):
                                            link_pdf = href
                                    
                                    # Buscar por descrição
                                    if elem.text and len(elem.text.strip()) > 20 and elem != h4:
                                        if not desc or len(elem.text.strip()) > len(desc):
                                            desc = elem.text.strip()
                                            
                                except:
                                    continue
                            
                        except Exception as e:
                            print(f"     ⚠️ Erro ao buscar detalhes: {e}")
                        
                        # Extrair datas do texto
                        data_limite = ""
                        if texto or desc:
                            padroes_data = [
                                r'\d{2}/\d{2}/\d{4}',
                                r'\d{2} de \w+ de \d{4}',
                                r'até \d{2}/\d{2}/\d{4}',
                                r'prazo: \d{2}/\d{2}/\d{4}',
                                r'inscrição: \d{2}/\d{2}/\d{4}'
                            ]
                            
                            for padrao in padroes_data:
                                match = re.search(padrao, texto + " " + desc, re.IGNORECASE)
                                if match:
                                    data_limite = match.group(0)
                                    break
                        
                        resultado = {
                            'titulo': texto,
                            'descricao': desc,
                            'link_pdf': link_pdf,
                            'data_limite': data_limite,
                            'fonte': 'CNPq',
                            'data_coleta': datetime.now().isoformat()
                        }
                        
                        self.resultados['cnpq'].append(resultado)
                        
                        print(f"[CNPq] ✅ Encontrado:")
                        print(f"   Título: {texto}")
                        print(f"   Descrição: {desc[:100]}..." if len(desc) > 100 else f"   Descrição: {desc}")
                        print(f"   PDF: {link_pdf}" if link_pdf else "   PDF: Não encontrado")
                        print(f"   Data limite: {data_limite}")
                        print("   ---")
                        
                except Exception as e:
                    print(f"   ⚠️ Erro ao processar chamada CNPq: {e}")
                    continue
            
            # Estratégia 2: Buscar por outros elementos
            try:
                outros_elementos = self.driver.find_elements(By.CSS_SELECTOR, "h3, h5, .chamada, .oportunidade, .edital")
                
                for elem in outros_elementos:
                    try:
                        texto = elem.text.strip()
                        
                        if (texto and len(texto) > 10 and 
                            any(palavra in texto.lower() for palavra in ['chamada', 'edital', 'oportunidade', 'programa', 'bolsa']) and
                            not any(r['titulo'] == texto for r in self.resultados['cnpq'])):
                            
                            # Buscar links próximos
                            link_pdf = ""
                            try:
                                link_elem = elem.find_element(By.XPATH, ".//a")
                                href = link_elem.get_attribute('href')
                                if href and (href.endswith('.pdf') or 'pdf' in href.lower()):
                                    link_pdf = href
                            except:
                                pass
                            
                            resultado = {
                                'titulo': texto,
                                'descricao': "",
                                'link_pdf': link_pdf,
                                'data_limite': "",
                                'fonte': 'CNPq',
                                'data_coleta': datetime.now().isoformat()
                            }
                            
                            self.resultados['cnpq'].append(resultado)
                            
                    except Exception as e:
                        continue
                        
            except Exception as e:
                print(f"   ⚠️ Erro na estratégia alternativa CNPq: {e}")
            
            print(f"✅ CNPq: {len(self.resultados['cnpq'])} chamadas encontradas")
            
        except Exception as e:
            print(f"❌ Erro ao extrair CNPq: {e}")
    
    def salvar_resultados(self):
        """Salva os resultados em arquivo JSON"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"editais_extraidos_{timestamp}.json"
            
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                json.dump(self.resultados, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 Resultados salvos em: {nome_arquivo}")
            return nome_arquivo
            
        except Exception as e:
            print(f"❌ Erro ao salvar resultados: {e}")
            return None
    
    def imprimir_resumo(self):
        """Imprime um resumo dos resultados"""
        print("\n" + "="*60)
        print("📊 RESUMO DA EXTRAÇÃO")
        print("="*60)
        
        total_ufjf = len(self.resultados['ufjf'])
        total_fapemig = len(self.resultados['fapemig'])
        total_cnpq = len(self.resultados['cnpq'])
        total_geral = total_ufjf + total_fapemig + total_cnpq
        
        print(f"🏛️  UFJF: {total_ufjf} editais")
        print(f"🔬 FAPEMIG: {total_fapemig} oportunidades")
        print(f"📚 CNPq: {total_cnpq} chamadas")
        print(f"📈 TOTAL: {total_geral} itens encontrados")
        print("="*60)
        
        # Mostrar alguns exemplos
        if total_geral > 0:
            print("\n📋 EXEMPLOS ENCONTRADOS:")
            print("-" * 40)
            
            for fonte, resultados in self.resultados.items():
                if resultados:
                    print(f"\n{fonte.upper()}:")
                    for i, resultado in enumerate(resultados[:2]):  # Mostrar apenas os 2 primeiros
                        print(f"  {i+1}. {resultado['titulo'][:60]}...")
                        if resultado.get('link_pdf'):
                            print(f"     PDF: {resultado['link_pdf']}")
                        if resultado.get('data_limite'):
                            print(f"     Data: {resultado['data_limite']}")
    
    def executar_extracao(self):
        """Executa a extração completa"""
        print("🚀 Iniciando extração de editais...")
        print(f"⏰ Início: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        if not self.configurar_navegador():
            return False
        
        try:
            # Executar extrações
            self.extrair_ufjf()
            self.extrair_fapemig()
            self.extrair_cnpq()
            
            # Salvar e mostrar resultados
            arquivo_salvo = self.salvar_resultados()
            self.imprimir_resumo()
            
            if arquivo_salvo:
                print(f"\n✅ Extração concluída com sucesso!")
                print(f"📁 Arquivo salvo: {arquivo_salvo}")
            else:
                print("\n⚠️ Extração concluída, mas houve erro ao salvar arquivo")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro durante a extração: {e}")
            return False
        
        finally:
            if self.driver:
                self.driver.quit()
                print("🔒 Navegador fechado")

def main():
    """Função principal"""
    scraper = ScraperEditaisAtualizado()
    sucesso = scraper.executar_extracao()
    
    if sucesso:
        print("\n🎉 Processo finalizado com sucesso!")
    else:
        print("\n💥 Processo finalizado com erros!")

if __name__ == "__main__":
    main()
