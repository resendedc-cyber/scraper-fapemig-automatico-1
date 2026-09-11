"""
Sistema de Configuração Centralizada
====================================

Centraliza todas as configurações do sistema de scraping,
incluindo URLs, timeouts, seletores CSS, etc.
"""

import os
from typing import Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class ScraperConfig:
    """Configuração para um scraper específico"""
    name: str
    urls: List[str]
    selectors: List[str]
    keywords: List[str]
    timeout: int = 30
    max_items: int = 10
    headless: bool = True
    window_size: str = "1920,1080"


@dataclass
class GlobalConfig:
    """Configuração global do sistema"""
    # Configurações do navegador
    browser: Dict[str, Any] = field(default_factory=lambda: {
        'headless': True,
        'window_size': '1920,1080',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'implicit_wait': 10,
        'page_load_timeout': 30,
        'script_timeout': 30
    })

    # Configurações de output
    output: Dict[str, Any] = field(default_factory=lambda: {
        'base_dir': 'data',
        'timestamp_format': '%Y%m%d_%H%M%S',
        'json_indent': 2,
        'encoding': 'utf-8'
    })

    # Configurações de logging
    logging: Dict[str, Any] = field(default_factory=lambda: {
        'level': 'INFO',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'file': 'logs/scraper.log'
    })


class ConfigManager:
    """Gerenciador de configurações centralizadas"""

    def __init__(self):
        self.global_config = GlobalConfig()
        self.scrapers_config = self._load_scrapers_config()

    def _load_scrapers_config(self) -> Dict[str, ScraperConfig]:
        """Carrega configurações específicas para cada scraper"""
        return {
            'fapemig': ScraperConfig(
                name='FAPEMIG',
                urls=[
                    'http://www.fapemig.br/pt/chamadas_abertas_oportunidades_fapemig/',
                    'https://fapemig.br/pt/chamadas_abertas_oportunidades_fapemig/',
                    'https://fapemig.br/pt/',
                    'http://www.fapemig.br/pt/'
                ],
                selectors=['h5', 'h4', 'h3', '.chamada', '.oportunidade', 'a'],
                keywords=['CHAMADA', 'PORTARIA', 'EDITAL', 'FAPEMIG'],
                timeout=30,
                max_items=15
            ),

            'cnpq': ScraperConfig(
                name='CNPq',
                urls=[
                    'https://www.cnpq.br/web/guest/chamadas-publicas',
                    'https://cnpq.br/web/guest/chamadas-publicas',
                    'https://www.cnpq.br/',
                    'http://memoria2.cnpq.br/web/guest/chamadas-publicas'
                ],
                selectors=['h4', 'h3', 'h5', '.chamada', '.oportunidade', '.edital'],
                keywords=['CHAMADA', 'EDITAL', 'PROGRAMA', 'OPORTUNIDADE'],
                timeout=25,
                max_items=10
            ),

            'ufjf': ScraperConfig(
                name='UFJF',
                urls=[
                    'https://www2.ufjf.br/propp/editais/',
                    'https://www2.ufjf.br/ufjf/editais/'
                ],
                selectors=['h3', 'h4', 'h5', '.edital-item', '.chamada-item', 'a'],
                keywords=['EDITAL', 'CHAMADA', 'PROGRAMA', 'PROEX', 'PET-SAÚDE'],
                timeout=35,
                max_items=12
            )
        }

    def get_scraper_config(self, scraper_name: str) -> ScraperConfig:
        """Retorna configuração específica de um scraper"""
        return self.scrapers_config.get(scraper_name.lower())

    def get_global_config(self) -> GlobalConfig:
        """Retorna configuração global"""
        return self.global_config

    def update_browser_config(self, **kwargs):
        """Atualiza configurações do navegador"""
        self.global_config.browser.update(kwargs)

    def update_output_config(self, **kwargs):
        """Atualiza configurações de output"""
        self.global_config.output.update(kwargs)


# Instância global do gerenciador de configuração
config_manager = ConfigManager()


def get_config(scraper_name: str = None) -> ScraperConfig | GlobalConfig:
    """Função helper para obter configurações"""
    if scraper_name:
        return config_manager.get_scraper_config(scraper_name)
    return config_manager.get_global_config()
