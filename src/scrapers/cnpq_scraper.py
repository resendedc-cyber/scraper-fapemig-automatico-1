"""
Scraper Especializado para CNPq
===============================

Implementação específica para extrair dados do Conselho Nacional de
Desenvolvimento Científico e Tecnológico (CNPq).
"""

import os
import json
import re
from typing import List, Optional
from pathlib import Path

from ..core.base_scraper import BaseScraper, ScrapedItem
from ..config.settings import get_config


class CNPQScraper(BaseScraper):
    """Scraper especializado para CNPq"""

    def __init__(self):
        config = get_config('cnpq')
        super().__init__(config)

    def get_source_name(self) -> str:
        """Retorna o nome da fonte"""
        return "CNPq"

    def extract_data(self) -> List[ScrapedItem]:
        """
        Extrai dados específicos do CNPq

        O CNPq tem algumas particularidades:
        1. URLs podem mudar frequentemente
        2. Estrutura de dados pode ser complexa
        3. Às vezes usamos dados de fallback de arquivos de configuração

        Returns:
            Lista de itens extraídos
        """
        items = []

        # Estratégia 1: Tentar scraping direto das URLs
        if self.try_urls(self.config.urls):
            items.extend(self._extract_cnpq_live_data())

        # Estratégia 2: Se não encontrou dados suficientes, usar fallback
        if len(items) < 3:
            fallback_items = self._load_fallback_data()
            if fallback_items:
                items.extend(fallback_items)
                self.logger.info(f"Usando {len(fallback_items)} itens de dados de fallback")

        # Estratégia 3: Buscar por padrões específicos do CNPq
        if len(items) < self.config.max_items:
            items.extend(self._extract_cnpq_patterns())

        # Remover duplicatas e ordenar
        items = self._remove_duplicates(items)
        items = self._sort_by_date(items)

        return items[:self.config.max_items]

    def _extract_cnpq_live_data(self) -> List[ScrapedItem]:
        """Extrai dados diretamente do site do CNPq"""
        items = []

        try:
            # O CNPq tem uma estrutura específica, vamos tentar diferentes abordagens
            items.extend(self._extract_cnpq_tables())
            items.extend(self._extract_cnpq_links())
            items.extend(self.extract_with_selectors(
                ['h4', 'h3', '.chamada', '.oportunidade', '.edital'],
                self.config.keywords
            ))

        except Exception as e:
            self.logger.warning(f"Erro ao extrair dados live do CNPq: {e}")

        return items

    def _extract_cnpq_tables(self) -> List[ScrapedItem]:
        """Extrai dados de tabelas do CNPq"""
        items = []

        try:
            from selenium.webdriver.common.by import By

            # Procurar por tabelas
            tables = self.browser.find_elements_safe(By.CSS_SELECTOR, 'table')

            for table in tables:
                try:
                    rows = table.find_elements(By.CSS_SELECTOR, 'tr')

                    for row in rows[1:]:  # Pular cabeçalho
                        try:
                            cols = row.find_elements(By.CSS_SELECTOR, 'td')
                            if len(cols) >= 2:
                                titulo = cols[0].text.strip()
                                data = cols[1].text.strip() if len(cols) > 1 else ""

                                if titulo and self._contains_keywords(titulo.upper(), self.config.keywords):
                                    item = ScrapedItem(
                                        titulo=titulo,
                                        descricao=titulo,
                                        data_inscricao=data,
                                        fonte=self.get_source_name(),
                                        data_coleta=self._get_current_datetime()
                                    )
                                    items.append(item)

                        except Exception as e:
                            continue

                except Exception as e:
                    continue

        except Exception as e:
            self.logger.warning(f"Erro ao extrair tabelas CNPq: {e}")

        return items

    def _extract_cnpq_links(self) -> List[ScrapedItem]:
        """Extrai dados de links do CNPq"""
        items = []

        try:
            from selenium.webdriver.common.by import By

            # Procurar por links específicos
            link_selectors = [
                'a[href*="chamada"]',
                'a[href*="edital"]',
                'a[href*="oportunidade"]',
                'a[href*="programa"]'
            ]

            for selector in link_selectors:
                try:
                    links = self.browser.find_elements_safe(By.CSS_SELECTOR, selector)

                    for link in links:
                        try:
                            href = link.get_attribute('href')
                            text = link.text.strip()

                            if href and text and len(text) > 10:
                                item = ScrapedItem(
                                    titulo=text,
                                    link_detalhes=href,
                                    fonte=self.get_source_name(),
                                    data_coleta=self._get_current_datetime(),
                                    descricao=text
                                )
                                items.append(item)

                        except Exception as e:
                            continue

                except Exception as e:
                    continue

        except Exception as e:
            self.logger.warning(f"Erro ao extrair links CNPq: {e}")

        return items

    def _extract_cnpq_patterns(self) -> List[ScrapedItem]:
        """Busca por padrões específicos do CNPq"""
        items = []

        # Padrões específicos do CNPq
        patterns = [
            r'CHAMADA\s+(?:PÚBLICA\s+)?(?:CNPq\s+)?Nº\s*\d+/\d+',
            r'PROGRAMA\s+[\w\s]+',
            r'EDITAL\s+[\w\s]+',
            r'APOIO\s+[\w\s]+'
        ]

        try:
            from selenium.webdriver.common.by import By

            # Buscar em todo o texto da página
            page_text = self.browser.driver.find_element(By.TAG_NAME, 'body').text

            for pattern in patterns:
                matches = re.finditer(pattern, page_text, re.IGNORECASE)

                for match in matches:
                    text = match.group(0).strip()

                    # Extrair contexto ao redor
                    start = max(0, match.start() - 100)
                    end = min(len(page_text), match.end() + 200)
                    context = page_text[start:end]

                    item = ScrapedItem(
                        titulo=text,
                        descricao=context,
                        fonte=self.get_source_name(),
                        data_coleta=self._get_current_datetime(),
                        texto_completo=context
                    )
                    items.append(item)

        except Exception as e:
            self.logger.warning(f"Erro ao extrair padrões CNPq: {e}")

        return items

    def _load_fallback_data(self) -> Optional[List[ScrapedItem]]:
        """Carrega dados de fallback de arquivo de configuração"""
        try:
            # Procurar por arquivo de configuração de chamadas CNPq
            config_files = [
                'config_chamadas_cnpq.json',
                'src/config/chamadas_cnpq.json',
                'chamadas_cnpq_detalhadas_*.json'
            ]

            for config_file in config_files:
                try:
                    if '*' in config_file:
                        # Procurar por arquivos com padrão
                        import glob
                        files = glob.glob(config_file)
                        if files:
                            config_file = files[0]  # Usar o mais recente

                    if os.path.exists(config_file):
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config_data = json.load(f)

                        items = []
                        chamadas = config_data.get('chamadas_cnpq', [])

                        for chamada in chamadas:
                            item = ScrapedItem(
                                titulo=chamada.get('titulo', ''),
                                descricao=chamada.get('descricao', ''),
                                data_inscricao=chamada.get('data_inscricao', ''),
                                link_permanente=chamada.get('link_permanente', ''),
                                numero_chamada=chamada.get('numero_chamada', ''),
                                fonte=self.get_source_name(),
                                data_coleta=self._get_current_datetime(),
                                status=chamada.get('status', 'Ativa'),
                                texto_completo=chamada.get('texto_completo', '')
                            )
                            items.append(item)

                        self.logger.info(f"Dados de fallback carregados de: {config_file}")
                        return items

                except Exception as e:
                    continue

        except Exception as e:
            self.logger.warning(f"Erro ao carregar dados de fallback: {e}")

        return None

    def _remove_duplicates(self, items: List[ScrapedItem]) -> List[ScrapedItem]:
        """Remove itens duplicados baseado no título"""
        seen_titles = set()
        unique_items = []

        for item in items:
            # Normalizar título para comparação
            normalized_title = re.sub(r'\s+', ' ', item.titulo.strip().upper())

            if normalized_title not in seen_titles:
                seen_titles.add(normalized_title)
                unique_items.append(item)

        return unique_items

    def _sort_by_date(self, items: List[ScrapedItem]) -> List[ScrapedItem]:
        """Ordena itens por data (mais recentes primeiro)"""
        def extract_date(item):
            # Tentar extrair data do título ou descrição
            text = item.titulo + ' ' + item.descricao
            dates = re.findall(r'\d{2}/\d{2}/\d{4}', text)

            if dates:
                # Converter para formato comparável
                try:
                    from datetime import datetime
                    date_str = dates[0]
                    return datetime.strptime(date_str, '%d/%m/%Y')
                except:
                    pass

            # Se não conseguir extrair data, colocar no final
            return datetime.max

        return sorted(items, key=extract_date)

    def _get_current_datetime(self) -> str:
        """Retorna a data/hora atual em formato ISO"""
        from datetime import datetime
        return datetime.now().isoformat()
