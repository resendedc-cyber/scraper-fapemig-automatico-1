"""
Classe Base para Scrapers
=========================

Classe abstrata que define a interface e funcionalidades comuns
para todos os scrapers do sistema.
"""

import time
import re
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from ..utils.browser import BrowserManager
from ..utils.data_handler import DataHandler
from ..utils.logger import get_logger, log_scraper_start, log_scraper_end, log_error, log_scraper_info
from ..config.settings import ScraperConfig


@dataclass
class ScrapedItem:
    """Representa um item extraído (edital, chamada, etc.)"""
    titulo: str
    descricao: str = ""
    data_inscricao: str = ""
    data_limite: str = ""
    link_pdf: str = ""
    link_detalhes: str = ""
    fonte: str = ""
    data_coleta: str = ""
    numero_chamada: str = ""
    status: str = "Ativa"
    texto_completo: str = ""


class BaseScraper(ABC):
    """Classe base abstrata para todos os scrapers"""

    def __init__(self, config: ScraperConfig):
        self.config = config
        self.browser = BrowserManager()
        self.data_handler = DataHandler()
        self.logger = get_logger(config.name)
        self.resultados: List[ScrapedItem] = []
        self._start_time: Optional[float] = None

    @abstractmethod
    def extract_data(self) -> List[ScrapedItem]:
        """
        Método abstrato que deve ser implementado por cada scraper específico.
        Responsável por extrair os dados do site.

        Returns:
            Lista de itens extraídos
        """
        pass

    @abstractmethod
    def get_source_name(self) -> str:
        """Retorna o nome da fonte de dados"""
        pass

    def scrape(self) -> Dict[str, Any]:
        """
        Método principal que executa o processo de scraping completo

        Returns:
            Dicionário com resultados e metadados
        """
        self._start_time = time.time()

        try:
            log_scraper_start(self.config.name, self.config.urls)

            # Inicializar navegador
            if not self.browser.setup_driver():
                raise Exception("Falha ao configurar navegador")

            # Extrair dados
            self.resultados = self.extract_data()

            # Calcular duração
            duration = time.time() - self._start_time

            log_scraper_end(self.config.name, len(self.resultados), duration)

            # Preparar resultado final
            return self._prepare_final_result(duration)

        except Exception as e:
            duration = time.time() - self._start_time if self._start_time else 0
            log_error(self.config.name, e, "scrape()")
            return self._prepare_error_result(e, duration)

        finally:
            self.browser.close()

    def _prepare_final_result(self, duration: float) -> Dict[str, Any]:
        """Prepara o resultado final do scraping"""
        return {
            self.get_source_name().lower(): [item.__dict__ for item in self.resultados],
            'timestamp': datetime.now().isoformat(),
            'total_itens': len(self.resultados),
            'duracao_segundos': round(duration, 2),
            'fonte': self.get_source_name(),
            'status': 'sucesso'
        }

    def _prepare_error_result(self, error: Exception, duration: float) -> Dict[str, Any]:
        """Prepara resultado em caso de erro"""
        return {
            self.get_source_name().lower(): [],
            'timestamp': datetime.now().isoformat(),
            'total_itens': 0,
            'duracao_segundos': round(duration, 2),
            'fonte': self.get_source_name(),
            'status': 'erro',
            'erro': str(error)
        }

    def try_urls(self, urls: List[str]) -> bool:
        """
        Tenta acessar múltiplas URLs até conseguir

        Args:
            urls: Lista de URLs para tentar

        Returns:
            True se conseguiu acessar alguma URL
        """
        for url in urls:
            log_scraper_info(self.config.name, f"Tentando URL: {url}")

            if self.browser.navigate_to_url(url, wait_time=3):
                log_scraper_info(self.config.name, f"✅ URL acessada com sucesso: {url}")
                return True
            else:
                log_scraper_info(self.config.name, f"❌ Falha ao acessar: {url}")

        log_error(self.config.name, Exception("Todas as URLs falharam"), "try_urls()")
        return False

    def extract_with_selectors(self, selectors: List[str], keywords: List[str]) -> List[ScrapedItem]:
        """
        Método genérico para extrair dados usando seletores CSS

        Args:
            selectors: Lista de seletores CSS para tentar
            keywords: Palavras-chave que os títulos devem conter

        Returns:
            Lista de itens extraídos
        """
        from selenium.webdriver.common.by import By

        items = []

        for selector in selectors:
            try:
                elements = self.browser.find_elements_safe(By.CSS_SELECTOR, selector)
                log_scraper_info(self.config.name, f"Seletor '{selector}': {len(elements)} elementos")

                for element in elements[:self.config.max_items]:
                    try:
                        text = element.text.strip()

                        if text and self._contains_keywords(text.upper(), keywords):
                            item = self._create_item_from_element(element, text)
                            if item:
                                items.append(item)

                                if len(items) >= self.config.max_items:
                                    break

                    except Exception as e:
                        continue

                if len(items) >= self.config.max_items:
                    break

            except Exception as e:
                log_error(self.config.name, e, f"extract_with_selectors({selector})")
                continue

        return items

    def _contains_keywords(self, text: str, keywords: List[str]) -> bool:
        """Verifica se o texto contém alguma das palavras-chave"""
        return any(keyword in text for keyword in keywords)

    def _create_item_from_element(self, element, text: str) -> Optional[ScrapedItem]:
        """
        Cria um item a partir de um elemento HTML.
        Pode ser sobrescrito pelas subclasses para lógica específica.
        """
        try:
            # Extrair informações básicas
            titulo = text[:200] + '...' if len(text) > 200 else text

            # Extrair datas (padrão brasileiro)
            datas = re.findall(r'\d{2}/\d{2}/\d{4}', text)
            data_inscricao = ' - '.join(datas) if datas else ''

            # Extrair links
            links = element.find_elements_by_css_selector('a')
            link_pdf = ''
            link_detalhes = ''

            for link in links:
                href = link.get_attribute('href')
                if href:
                    if href.endswith('.pdf') or 'pdf' in href.lower():
                        link_pdf = href
                    else:
                        link_detalhes = href

            return ScrapedItem(
                titulo=titulo,
                descricao=text,
                data_inscricao=data_inscricao,
                link_pdf=link_pdf,
                link_detalhes=link_detalhes,
                fonte=self.get_source_name(),
                data_coleta=datetime.now().isoformat(),
                texto_completo=text
            )

        except Exception as e:
            log_error(self.config.name, e, "_create_item_from_element")
            return None

    def save_results(self, results: Dict[str, Any]) -> Optional[str]:
        """
        Salva os resultados em arquivo JSON

        Args:
            results: Resultados a serem salvos

        Returns:
            Caminho do arquivo salvo ou None se erro
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.get_source_name().lower()}_{timestamp}.json"

            return self.data_handler.save_json(results, filename)

        except Exception as e:
            log_error(self.config.name, e, "save_results")
            return None

    def save_report(self, results: Dict[str, Any], format_type: str = 'txt') -> Optional[str]:
        """
        Salva relatório formatado

        Args:
            results: Dados do relatório
            format_type: Tipo do relatório ('txt' ou 'html')

        Returns:
            Caminho do arquivo salvo
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"relatorio_{self.get_source_name().lower()}_{timestamp}.{format_type}"

            if format_type == 'html':
                return self.data_handler.save_html_report(results, filename)
            else:
                return self.data_handler.save_text_report(results, filename)

        except Exception as e:
            log_error(self.config.name, e, f"save_report({format_type})")
            return None
