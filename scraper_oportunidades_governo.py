#!/usr/bin/env python3
"""Coleta editais e chamadas públicas de CNPq, CAPES e MCTI."""

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

SOURCES = {
    "cnpq": {
        "nome": "CNPq",
        "url": "https://www.gov.br/cnpq/pt-br/assuntos/chamadas-publicas",
        "fallback": "https://www.cnpq.br/web/guest/chamadas-publicas",
    },
    "capes": {
        "nome": "CAPES",
        "url": "https://www.gov.br/capes/pt-br/assuntos/editais-e-resultados-capes",
    },
    "mcti": {
        "nome": "MCTI",
        "url": "https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/noticias",
    },
}

KEYWORDS = re.compile(
    r"\b(edital|chamada(?:s)? pública(?:s)?|seleção pública|oportunidade|" \
    r"programa de bolsas|fomento)\b",
    re.IGNORECASE,
)
DATE_PATTERN = re.compile(r"\b\d{1,2}/\d{1,2}/\d{4}\b")


def fetch(url):
    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; OportunidadesBot/1.0)"},
        timeout=30,
    )
    response.raise_for_status()
    return response.text, response.url


def clean_text(value):
    return re.sub(r"\s+", " ", value or "").strip()


def extract_items(html, page_url, source_name):
    soup = BeautifulSoup(html, "html.parser")
    items = []
    seen = set()

    for anchor in soup.select("a[href]"):
        title = clean_text(anchor.get_text(" ", strip=True))
        href = urljoin(page_url, anchor.get("href", ""))
        if len(title) < 12 or href in seen or not KEYWORDS.search(title):
            continue
        seen.add(href)
        context = clean_text(anchor.parent.get_text(" ", strip=True))
        dates = DATE_PATTERN.findall(context)
        items.append(
            {
                "titulo": title,
                "descricao": context[:500],
                "data_inscricao": " - ".join(dates[:2]),
                "link_permanente": href,
                "link_pdf": href if ".pdf" in href.lower() else "",
                "fonte": source_name,
                "data_coleta": datetime.now(timezone.utc).isoformat(),
            }
        )
    return items


def collect_source(source):
    urls = [source["url"]]
    if source.get("fallback"):
        urls.append(source["fallback"])
    last_error = None
    for url in urls:
        try:
            html, final_url = fetch(url)
            items = extract_items(html, final_url, source["nome"])
            return items, {"url": final_url, "status": "ok", "itens": len(items)}
        except requests.RequestException as error:
            last_error = str(error)
    return [], {"url": urls[0], "status": "erro", "erro": last_error}


def main():
    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "fontes": {},
        "cnpq": [],
        "capes": [],
        "mcti": [],
    }
    for key, source in SOURCES.items():
        items, status = collect_source(source)
        result[key] = items
        result["fontes"][key] = status
        print(f"{source['nome']}: {len(items)} oportunidades ({status['status']})")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = Path(f"oportunidades_governo_{timestamp}.json")
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Resultado salvo em: {output}")
    print(f"Total: {sum(len(result[key]) for key in SOURCES)}")


if __name__ == "__main__":
    main()
