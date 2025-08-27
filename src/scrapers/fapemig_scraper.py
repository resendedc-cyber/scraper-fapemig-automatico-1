"""
Scraper Especializado para FAPEMIG
===================================

Implementação específica para extrair dados da Fundação de Amparo à Pesquisa
do Estado de Minas Gerais (FAPEMIG).
"""

import re
from typing import List
from selenium.webdriver.common.by import By

from ..core.base_scraper import BaseScraper, ScrapedItem
from ..config.settings import get_config


class FAPEMIGScraper(BaseScraper):
    """Scraper especializado para FAPEMIG"""

    def __init__(self):
        config = get_config('fapemig')
        super().__init__(config)

    def get_source_name(self) -> str:
        """Retorna o nome da fonte"""
        return "FAPEMIG"

    def extract_data(self) -> List[ScrapedItem]:
        """
        Extrai dados específicos da FAPEMIG

        Returns:
            Lista de itens extraídos
        """
        # Tentar acessar as URLs da FAPEMIG
        if not self.try_urls(self.config.urls):
            self.logger.warning("Não foi possível acessar nenhuma URL da FAPEMIG")
            return []

        # Extrair dados usando estratégia específica da FAPEMIG
        items = []

        # Estratégia 1: Buscar por elementos h5 (mais comum na FAPEMIG)
        items.extend(self._extract_h5_elements())

        # Estratégia 2: Buscar por outros seletores se necessário
        if len(items) < self.config.max_items:
            items.extend(self.extract_with_selectors(
                ['h4', 'h6', '.chamada', '.oportunidade'],
                self.config.keywords
            ))

        # Estratégia 3: Buscar por texto específico se ainda não encontrou muito
        if len(items) < 3:
            items.extend(self._extract_by_specific_text())

        # Remover duplicatas
        items = self._remove_duplicates(items)

        return items[:self.config.max_items]

    def _extract_h5_elements(self) -> List[ScrapedItem]:
        """Extrai dados específicos dos elementos h5 da FAPEMIG"""
        items = []

        try:
            h5_elements = self.browser.find_elements_safe(By.CSS_SELECTOR, 'h5')

            for element in h5_elements:
                try:
                    text = element.text.strip()

                    if text and self._contains_keywords(text.upper(), self.config.keywords):
                        item = self._create_fapemig_item(element, text)
                        if item:
                            items.append(item)

                except Exception as e:
                    continue

        except Exception as e:
            self.logger.warning(f"Erro ao extrair elementos h5: {e}")

        return items

    def _extract_by_specific_text(self) -> List[ScrapedItem]:
        """Busca por textos específicos conhecidos da FAPEMIG"""
        items = []

        # Textos específicos que sabemos que existem na FAPEMIG
        specific_texts = [
            "CHAMADA",
            "PORTARIA",
            "EDITAL",
            "FAPEMIG"
        ]

        for text in specific_texts:
            try:
                # Buscar por elementos que contenham estes textos
                xpath = f"//*[contains(translate(text(), 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), '{text}')]"
                elements = self.browser.find_elements_safe(By.XPATH, xpath)

                for element in elements[:5]:  # Limitar para não sobrecarregar
                    try:
                        element_text = element.text.strip()

                        if len(element_text) > 20:  # Texto significativo
                            item = self._create_item_from_element(element, element_text)
                            if item and item not in items:
                                items.append(item)

                    except Exception as e:
                        continue

            except Exception as e:
                continue

        return items

    def _create_fapemig_item(self, element, text: str) -> ScrapedItem:
        """
        Cria um item específico da FAPEMIG com informações detalhadas

        Args:
            element: Elemento HTML
            text: Texto do elemento

        Returns:
            Item criado
        """
        try:
            # Extrair número da chamada (padrão FAPEMIG: XXX/XXXX)
            numero_chamada = ""
            numero_match = re.search(r'(\d{3}/\d{4})', text)
            if numero_match:
                numero_chamada = numero_match.group(1)

            # Extrair datas
            datas = re.findall(r'\d{2}/\d{2}/\d{4}', text)
            data_inscricao = ""
            prazo_final = ""

            if len(datas) >= 2:
                data_inscricao = datas[0]
                prazo_final = datas[1]
            elif len(datas) == 1:
                prazo_final = datas[0]

            # Tentar pegar elemento pai para mais contexto
            try:
                parent_element = element.find_element(By.XPATH, "./..")
                full_text = parent_element.text.strip()
            except:
                full_text = text

            # Verificar se tem anexos/PDFs
            has_attachments = "DOWNLOAD" in full_text.upper() or "PDF" in full_text.upper()

            # Criar item
            item = ScrapedItem(
                titulo=text[:200] + '...' if len(text) > 200 else text,
                descricao=text,
                data_inscricao=data_inscricao,
                data_limite=prazo_final,
                numero_chamada=numero_chamada,
                fonte=self.get_source_name(),
                data_coleta=self._get_current_datetime(),
                status="Ativa",
                texto_completo=full_text
            )

            return item

        except Exception as e:
            self.logger.warning(f"Erro ao criar item FAPEMIG: {e}")
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

    def _get_current_datetime(self) -> str:
        """Retorna a data/hora atual em formato ISO"""
        from datetime import datetime
        return datetime.now().isoformat()
