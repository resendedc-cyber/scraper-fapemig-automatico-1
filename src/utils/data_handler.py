"""
Utilitários para manipulação e salvamento de dados
==================================================
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from ..config.settings import get_config


logger = logging.getLogger(__name__)


class DataHandler:
    """Gerenciador de dados para salvar e carregar informações"""

    def __init__(self):
        self.config = get_config().output
        self._ensure_data_directory()

    def _ensure_data_directory(self):
        """Garante que o diretório de dados existe"""
        data_dir = Path(self.config['base_dir'])
        data_dir.mkdir(parents=True, exist_ok=True)

        # Criar subdiretórios
        (data_dir / 'json').mkdir(exist_ok=True)
        (data_dir / 'html').mkdir(exist_ok=True)
        (data_dir / 'txt').mkdir(exist_ok=True)
        (data_dir / 'logs').mkdir(exist_ok=True)

    def save_json(self, data: Dict[str, Any], filename: Optional[str] = None,
                  subdirectory: str = 'json') -> Optional[str]:
        """
        Salva dados em formato JSON

        Args:
            data: Dados a serem salvos
            filename: Nome do arquivo (opcional)
            subdirectory: Subdiretório onde salvar

        Returns:
            str: Caminho do arquivo salvo ou None se erro
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime(self.config['timestamp_format'])
                filename = f"scraper_{timestamp}.json"

            # Garantir extensão .json
            if not filename.endswith('.json'):
                filename += '.json'

            # Caminho completo
            file_path = Path(self.config['base_dir']) / subdirectory / filename

            # Salvar dados
            with open(file_path, 'w', encoding=self.config['encoding']) as f:
                json.dump(data, f, ensure_ascii=False, indent=self.config['json_indent'])

            logger.info(f"💾 Dados salvos em: {file_path}")
            return str(file_path)

        except Exception as e:
            logger.error(f"❌ Erro ao salvar JSON: {e}")
            return None

    def save_text_report(self, data: Dict[str, Any], filename: Optional[str] = None) -> Optional[str]:
        """
        Salva relatório em formato texto

        Args:
            data: Dados do relatório
            filename: Nome do arquivo (opcional)

        Returns:
            str: Caminho do arquivo salvo
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime(self.config['timestamp_format'])
                filename = f"relatorio_{timestamp}.txt"

            if not filename.endswith('.txt'):
                filename += '.txt'

            file_path = Path(self.config['base_dir']) / 'txt' / filename

            with open(file_path, 'w', encoding=self.config['encoding']) as f:
                f.write(self._generate_text_report(data))

            logger.info(f"💾 Relatório texto salvo em: {file_path}")
            return str(file_path)

        except Exception as e:
            logger.error(f"❌ Erro ao salvar relatório texto: {e}")
            return None

    def save_html_report(self, data: Dict[str, Any], filename: Optional[str] = None) -> Optional[str]:
        """
        Salva relatório em formato HTML

        Args:
            data: Dados do relatório
            filename: Nome do arquivo (opcional)

        Returns:
            str: Caminho do arquivo salvo
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime(self.config['timestamp_format'])
                filename = f"relatorio_{timestamp}.html"

            if not filename.endswith('.html'):
                filename += '.html'

            file_path = Path(self.config['base_dir']) / 'html' / filename

            with open(file_path, 'w', encoding=self.config['encoding']) as f:
                f.write(self._generate_html_report(data))

            logger.info(f"💾 Relatório HTML salvo em: {file_path}")
            return str(file_path)

        except Exception as e:
            logger.error(f"❌ Erro ao salvar relatório HTML: {e}")
            return None

    def _generate_text_report(self, data: Dict[str, Any]) -> str:
        """Gera relatório em formato texto"""
        lines = []
        lines.append("=" * 80)
        lines.append("RELATÓRIO DE SCRAPING - EDITAIS E CHAMADAS")
        lines.append("=" * 80)
        lines.append("")

        # Timestamp
        if 'timestamp' in data:
            lines.append(f"Data/Hora: {data['timestamp']}")
        lines.append("")

        # Totais por fonte
        total_geral = 0
        for fonte, itens in data.items():
            if fonte == 'timestamp':
                continue
            if isinstance(itens, list):
                total_fonte = len(itens)
                total_geral += total_fonte
                lines.append(f"{fonte.upper()}: {total_fonte} itens")
                lines.append("-" * 40)

                for i, item in enumerate(itens[:5], 1):  # Mostra apenas os primeiros 5
                    lines.append(f"{i}. {item.get('titulo', 'N/A')}")
                    if 'data_inscricao' in item and item['data_inscricao']:
                        lines.append(f"   📅 Data: {item['data_inscricao']}")
                    if 'link_permanente' in item and item['link_permanente']:
                        lines.append(f"   🔗 Link: {item['link_permanente']}")
                    lines.append("")

                if len(itens) > 5:
                    lines.append(f"... e mais {len(itens) - 5} itens")
                lines.append("")

        lines.append("=" * 80)
        lines.append(f"TOTAL GERAL: {total_geral} itens encontrados")
        lines.append("=" * 80)

        return "\n".join(lines)

    def _generate_html_report(self, data: Dict[str, Any]) -> str:
        """Gera relatório em formato HTML"""
        html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Scraping</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ text-align: center; border-bottom: 2px solid #333; padding-bottom: 10px; }}
        .fonte {{ margin: 20px 0; }}
        .item {{ margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 5px; }}
        .stats {{ background: #e8f4f8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .titulo {{ font-weight: bold; color: #2c3e50; }}
        .data {{ color: #27ae60; font-size: 0.9em; }}
        .link {{ color: #3498db; text-decoration: none; }}
        .link:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Relatório de Scraping</h1>
        <h2>Editais e Chamadas Públicas</h2>
        <p><strong>Data/Hora:</strong> {data.get('timestamp', 'N/A')}</p>
    </div>
"""

        total_geral = 0

        for fonte, itens in data.items():
            if fonte == 'timestamp':
                continue
            if isinstance(itens, list):
                total_fonte = len(itens)
                total_geral += total_fonte

                html += f"""
    <div class="fonte">
        <h3>🏛️ {fonte.upper()}</h3>
        <div class="stats">Encontrados: {total_fonte} itens</div>
"""

                for item in itens[:10]:  # Mostra apenas os primeiros 10
                    titulo = item.get('titulo', 'N/A')
                    data_inscricao = item.get('data_inscricao', '')
                    link = item.get('link_permanente', '') or item.get('link_pdf', '')

                    html += f"""
        <div class="item">
            <div class="titulo">{titulo}</div>
            {"<div class='data'>📅 " + data_inscricao + "</div>" if data_inscricao else ""}
            {"<div><a class='link' href='" + link + "' target='_blank'>🔗 Link</a></div>" if link else ""}
        </div>
"""

                if len(itens) > 10:
                    html += f"<p>... e mais {len(itens) - 10} itens</p>"

                html += "    </div>"

        html += f"""
    <div class="stats" style="background: #d5f4e6;">
        <h3>📈 TOTAL GERAL: {total_geral} itens encontrados</h3>
    </div>
</body>
</html>
"""

        return html

    def load_json(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Carrega dados de um arquivo JSON"""
        try:
            with open(filepath, 'r', encoding=self.config['encoding']) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"❌ Erro ao carregar JSON {filepath}: {e}")
            return None

    def create_backup(self, filepath: str) -> Optional[str]:
        """Cria backup de um arquivo"""
        try:
            path = Path(filepath)
            if path.exists():
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = path.parent / f"{path.stem}_backup_{timestamp}{path.suffix}"
                backup_path.write_text(path.read_text(encoding=self.config['encoding']))
                logger.info(f"📁 Backup criado: {backup_path}")
                return str(backup_path)
        except Exception as e:
            logger.error(f"❌ Erro ao criar backup: {e}")
        return None


def create_data_handler() -> DataHandler:
    """Factory function para criar gerenciador de dados"""
    return DataHandler()
