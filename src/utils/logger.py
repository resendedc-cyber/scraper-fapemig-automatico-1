"""
Sistema de Logging Centralizado
===============================
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional

from ..config.settings import get_config


def setup_logging(log_level: str = None, log_file: str = None) -> logging.Logger:
    """
    Configura o sistema de logging

    Args:
        log_level: Nível de logging (DEBUG, INFO, WARNING, ERROR)
        log_file: Caminho do arquivo de log

    Returns:
        Logger configurado
    """
    config = get_config().logging

    # Usar configurações padrão se não especificadas
    if not log_level:
        log_level = config['level']
    if not log_file:
        log_file = config['file']

    # Criar diretório do log se não existir
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Configurar formatação
    formatter = logging.Formatter(config['format'])

    # Configurar logger raiz
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remover handlers existentes
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Handler para arquivo
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Retorna um logger com nome específico"""
    return logging.getLogger(name)


def log_scraper_start(scraper_name: str, urls: list):
    """Log padronizado para início de scraping"""
    logger = get_logger(scraper_name)
    logger.info(f"🚀 Iniciando {scraper_name}")
    logger.info(f"📋 URLs: {', '.join(urls)}")


def log_scraper_end(scraper_name: str, items_found: int, duration: float):
    """Log padronizado para fim de scraping"""
    logger = get_logger(scraper_name)
    logger.info(f"✅ {scraper_name} concluído")
    logger.info(f"📊 Itens encontrados: {items_found}")
    logger.info(".1f"def log_error(scraper_name: str, error: Exception, context: str = ""):
    """Log padronizado para erros"""
    logger = get_logger(scraper_name)
    logger.error(f"❌ Erro em {scraper_name}: {error}")
    if context:
        logger.error(f"📝 Contexto: {context}")


def log_scraper_info(scraper_name: str, message: str):
    """Log informativo padronizado"""
    logger = get_logger(scraper_name)
    logger.info(f"🔍 {scraper_name}: {message}")
