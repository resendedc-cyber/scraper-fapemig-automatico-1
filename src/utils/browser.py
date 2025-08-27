"""
Utilitários para configuração e gerenciamento do navegador
==========================================================
"""

import time
import logging
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
import chromedriver_autoinstaller

from ..config.settings import get_config


logger = logging.getLogger(__name__)


class BrowserManager:
    """Gerenciador unificado do navegador Chrome"""

    def __init__(self):
        self.driver = None
        self.wait = None
        self.config = get_config().browser

    def setup_driver(self) -> bool:
        """
        Configura o driver do Chrome com as configurações otimizadas

        Returns:
            bool: True se configurado com sucesso, False caso contrário
        """
        try:
            logger.info("Configurando navegador Chrome...")

            # Instalar chromedriver automaticamente
            chromedriver_autoinstaller.install()

            # Configurar opções do Chrome
            options = Options()

            # Configurações básicas
            if self.config['headless']:
                options.add_argument('--headless')
                logger.info("Executando em modo headless")

            options.add_argument(f'--window-size={self.config["window_size"]}')
            options.add_argument(f'--user-agent={self.config["user_agent"]}')

            # Configurações de performance
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-images')  # Carregar mais rápido
            options.add_argument('--disable-javascript')  # Para alguns sites, opcional

            # Configurações de segurança
            options.add_argument('--ignore-ssl-errors')
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--allow-insecure-localhost')
            options.add_argument('--disable-web-security')

            # Inicializar driver
            self.driver = webdriver.Chrome(options=options)

            # Configurar timeouts
            self.driver.implicitly_wait(self.config['implicit_wait'])
            self.driver.set_page_load_timeout(self.config['page_load_timeout'])
            self.driver.set_script_timeout(self.config['script_timeout'])

            # Configurar WebDriverWait
            self.wait = WebDriverWait(self.driver, self.config['implicit_wait'])

            logger.info("✅ Navegador configurado com sucesso!")
            return True

        except Exception as e:
            logger.error(f"❌ Erro ao configurar navegador: {e}")
            return False

    def navigate_to_url(self, url: str, wait_time: int = 3) -> bool:
        """
        Navega para uma URL específica

        Args:
            url: URL para navegar
            wait_time: Tempo de espera após carregamento

        Returns:
            bool: True se navegou com sucesso
        """
        if not self.driver:
            logger.error("Driver não inicializado")
            return False

        try:
            logger.info(f"Navegando para: {url}")
            self.driver.get(url)

            if wait_time > 0:
                time.sleep(wait_time)

            # Verificar se carregou corretamente
            if self._check_page_loaded():
                logger.info(f"✅ Página carregada: {self.driver.title}")
                return True
            else:
                logger.warning(f"⚠️  Problema ao carregar página: {url}")
                return False

        except Exception as e:
            logger.error(f"❌ Erro ao navegar para {url}: {e}")
            return False

    def _check_page_loaded(self) -> bool:
        """Verifica se a página carregou corretamente"""
        try:
            # Verificar se há problemas de SSL/conexão
            current_url = self.driver.current_url
            title = self.driver.title

            if "chrome-error" in current_url or "O site não é seguro" in title:
                return False

            return True
        except:
            return False

    def find_elements_safe(self, by: By, selector: str, multiple: bool = True):
        """
        Busca elementos de forma segura com tratamento de erros

        Args:
            by: Estratégia de localização (By.ID, By.CSS_SELECTOR, etc.)
            selector: Seletor a ser usado
            multiple: Se deve buscar múltiplos elementos

        Returns:
            Lista de elementos ou elemento único
        """
        if not self.driver:
            return [] if multiple else None

        try:
            if multiple:
                return self.driver.find_elements(by, selector)
            else:
                return self.driver.find_element(by, selector)
        except Exception as e:
            logger.warning(f"Elemento não encontrado - {by}: {selector} - {e}")
            return [] if multiple else None

    def wait_for_element(self, by: By, selector: str, timeout: int = 10):
        """Espera por um elemento específico"""
        if not self.wait:
            return None

        try:
            return self.wait.until(
                EC.presence_of_element_located((by, selector))
            )
        except TimeoutException:
            logger.warning(f"Timeout aguardando elemento: {selector}")
            return None

    def scroll_page(self, direction: str = "down", pixels: int = 500):
        """Faz scroll na página"""
        if not self.driver:
            return

        try:
            if direction == "down":
                self.driver.execute_script(f"window.scrollBy(0, {pixels});")
            elif direction == "up":
                self.driver.execute_script(f"window.scrollBy(0, -{pixels});")
            elif direction == "top":
                self.driver.execute_script("window.scrollTo(0, 0);")
            elif direction == "bottom":
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            time.sleep(0.5)  # Pequena pausa após scroll

        except Exception as e:
            logger.warning(f"Erro ao fazer scroll: {e}")

    def close(self):
        """Fecha o navegador"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("🔒 Navegador fechado")
            except Exception as e:
                logger.warning(f"Erro ao fechar navegador: {e}")
            finally:
                self.driver = None
                self.wait = None

    def __enter__(self):
        """Context manager entry"""
        self.setup_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


def create_browser_manager() -> BrowserManager:
    """Factory function para criar gerenciador de navegador"""
    return BrowserManager()
