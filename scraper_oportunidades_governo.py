#!/usr/bin/env python3
"""Coleta editais e chamadas públicas de CNPq, CAPES e MCTI."""

import json
import re
import argparse
import subprocess
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
    "ufjf": {
        "nome": "UFJF/CRITT - Bolsas",
        "url": "https://www2.ufjf.br/critt/vagas-e-bolsas-do-critt/controle-de-editais-2026/",
        "keywords": re.compile(r"\bbolsa(?:s)?\b", re.IGNORECASE),
        "section": "1. Vagas:",
    },
    "iel": {
        "nome": "IEL-MG/FIEMG",
        "url": "https://www.fiemg.com.br/iel/",
        "fallback": "https://ielmg.com.br/",
    },
    "cidades": {
        "nome": "Ministério das Cidades",
        "url": "https://www.gov.br/cidades/pt-br/assuntos",
        "projetos": True,
    },
}

KEYWORDS = re.compile(
    r"\b(edital|chamada(?:s)? pública(?:s)?|seleção pública|oportunidade|" \
    r"programa de bolsas|fomento)\b",
    re.IGNORECASE,
)
DATE_PATTERN = re.compile(r"\b\d{1,2}/\d{1,2}/\d{4}\b")
DATE_RANGE_PATTERN = re.compile(
    r"(?:inscri(?:ção|ções)|abertura|início|inicial).*?"
    r"(\d{1,2}/\d{1,2}/\d{4}).{0,80}?"
    r"(?:a|até|[-–]).{0,20}?(\d{1,2}/\d{1,2}/\d{4})",
    re.IGNORECASE,
)
PT_DATE_RANGE_PATTERN = re.compile(
    r"(?:inscri(?:ção|ções)|abertura|início|inicial).*?"
    r"(\d{1,2})\s+de\s+([a-zç]+)\s+a\s+(\d{1,2})\s+de\s+([a-zç]+)\s+de\s+(\d{4})",
    re.IGNORECASE,
)
MONTHS = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4,
    "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
    "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
}


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


def extract_period(text):
    """Extrai datas de abertura e conclusão do prazo de inscrição."""
    match = PT_DATE_RANGE_PATTERN.search(text)
    if match:
        start_month = MONTHS.get(match.group(2).lower())
        end_month = MONTHS.get(match.group(4).lower())
        if start_month and end_month:
            return (
                f"{int(match.group(1)):02d}/{start_month:02d}/{match.group(5)}",
                f"{int(match.group(3)):02d}/{end_month:02d}/{match.group(5)}",
            )
    match = DATE_RANGE_PATTERN.search(text)
    if match:
        return match.group(1), match.group(2)
    dates = DATE_PATTERN.findall(text)
    return (dates[0], dates[1] if len(dates) > 1 else "") if dates else ("", "")


def extract_detail_dates(url):
    """Busca datas na página individual quando a listagem não as exibe."""
    try:
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; OportunidadesBot/1.0)"},
            timeout=20,
        )
        if "text/html" not in response.headers.get("content-type", ""):
            return []
        text = clean_text(BeautifulSoup(response.text, "html.parser").get_text(" "))
        return DATE_PATTERN.findall(text)
    except requests.RequestException:
        return []


def extract_pdf_text(url):
    """Lê o texto de um edital PDF para confirmar que é de bolsa."""
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        result = subprocess.run(
            ["pdftotext", "-", "-"],
            input=response.content,
            capture_output=True,
            check=False,
            timeout=30,
        )
        return result.stdout.decode("utf-8", errors="ignore")
    except Exception:
        return ""


def extract_items(html, page_url, source_name):
    soup = BeautifulSoup(html, "html.parser")
    if isinstance(source_name, dict) and source_name.get("projetos"):
        return extract_city_projects(soup, page_url)
    items = []
    seen = set()
    anchors = [(anchor, "") for anchor in soup.select("a[href]")]
    if isinstance(source_name, dict) and source_name.get("section"):
        section = next(
            (heading for heading in soup.find_all(["h1", "h2", "h3"])
             if clean_text(heading.get_text(" ", strip=True)) == source_name["section"]),
            None,
        )
        if section:
            anchors = []
            section_status = ""
            for node in section.find_all_next():
                if node.name == "h1" and node is not section:
                    break
                if node.name == "h2":
                    heading = clean_text(node.get_text(" ", strip=True)).lower()
                    if heading in ("abertos", "fechados"):
                        section_status = "aberto" if heading == "abertos" else "antigo"
                if node.name == "a" and node.get("href"):
                    anchors.append((node, section_status))

    for anchor, section_status in anchors:
        title = clean_text(anchor.get_text(" ", strip=True))
        href = urljoin(page_url, anchor.get("href", ""))
        keyword_pattern = source_name.get("keywords", KEYWORDS) if isinstance(source_name, dict) else KEYWORDS
        pdf_text = extract_pdf_text(href) if isinstance(source_name, dict) and source_name.get("section") else ""
        if len(title) < 8 or href in seen or not keyword_pattern.search(title + " " + pdf_text):
            continue
        seen.add(href)
        context = clean_text(anchor.parent.get_text(" ", strip=True))
        for parent in anchor.parents:
            candidate = clean_text(parent.get_text(" ", strip=True))
            if DATE_PATTERN.search(candidate) and len(candidate) <= 1200:
                context = candidate
                break
        context = clean_text(f"{context} {pdf_text}")
        dates = DATE_PATTERN.findall(context)
        if not dates:
            dates = extract_detail_dates(href)
        data_abertura, data_conclusao = extract_period(context)
        if data_abertura and data_abertura not in dates:
            dates.extend([data_abertura, data_conclusao] if data_conclusao else [data_abertura])
        status, prazo_final = classify_status(dates)
        if section_status:
            status = section_status
        finalidade = clean_text(anchor.parent.get_text(" ", strip=True))
        items.append(
            {
                "titulo": title,
                "descricao": context[:500],
                "data_inscricao": " - ".join(dates[:2]),
                "data_abertura": data_abertura,
                "data_conclusao": data_conclusao,
                "finalidade": finalidade[:500],
                "prazo_final": prazo_final,
                "status": status,
                "link_permanente": href,
                "link_pdf": href if ".pdf" in href.lower() else "",
                "fonte": source_name,
                "data_coleta": datetime.now(timezone.utc).isoformat(),
            }
        )
    return items


def extract_city_projects(soup, page_url):
    """Lista projetos do Ministério agrupados pela área da URL."""
    items = []
    seen = set()
    excluded = {"assuntos", "acesso-a-informacao", "navegacao", "perguntas-frequentes"}
    for anchor in soup.select("a[href]"):
        title = clean_text(anchor.get_text(" ", strip=True))
        href = urljoin(page_url, anchor.get("href", ""))
        if not title or len(title) < 8 or href in seen:
            continue
        if not href.startswith("https://www.gov.br/cidades/pt-br/"):
            continue
        parts = [part for part in href.rstrip("/").split("/") if part]
        if len(parts) < 6 or parts[-1] in excluded:
            continue
        if any(term in title.lower() for term in ("navegação", "dúvidas", "acesso à informação")):
            continue
        seen.add(href)
        area_index = parts.index("pt-br") + 1
        area = parts[area_index].replace("-", " ").title()
        items.append(
            {
                "titulo": title,
                "descricao": title,
                "data_inscricao": "",
                "data_abertura": "",
                "data_conclusao": "",
                "finalidade": title,
                "prazo_final": "",
                "status": "catalogado",
                "link_permanente": href,
                "link_pdf": "",
                "fonte": "Ministério das Cidades",
                "data_coleta": datetime.now(timezone.utc).isoformat(),
                "subgrupo": area,
                "link_projeto": href,
            }
        )
    return items


def classify_status(date_values):
    """Classifica o edital pelo último prazo encontrado no texto."""
    parsed_dates = []
    for value in date_values:
        try:
            parsed_dates.append(datetime.strptime(value, "%d/%m/%Y").date())
        except ValueError:
            continue
    if not parsed_dates:
        return "sem_prazo", ""

    deadline = max(parsed_dates)
    today = datetime.now(timezone.utc).date()
    return ("aberto" if deadline >= today else "antigo"), deadline.strftime("%d/%m/%Y")


def collect_source(source):
    urls = [source["url"]]
    if source.get("fallback"):
        urls.append(source["fallback"])
    last_error = None
    for url in urls:
        try:
            html, final_url = fetch(url)
            items = extract_items(html, final_url, source)
            for item in items:
                item["fonte"] = source["nome"]
            return items, {"url": final_url, "status": "ok", "itens": len(items)}
        except requests.RequestException as error:
            last_error = str(error)
    return [], {"url": urls[0], "status": "erro", "erro": last_error}


def main():
    parser = argparse.ArgumentParser(description="Filtra oportunidades por situação")
    parser.add_argument(
        "--status",
        choices=("todos", "aberto", "antigo", "sem_prazo"),
        default="todos",
        help="Status a manter no resultado final",
    )
    args = parser.parse_args()
    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "fontes": {},
        "cnpq": [],
        "capes": [],
        "mcti": [],
        "iel": [],
        "cidades": [],
        "abertos": [],
        "antigos": [],
        "sem_prazo": [],
        "filtro_aplicado": args.status,
    }
    for key, source in SOURCES.items():
        items, status = collect_source(source)
        if args.status != "todos" and not source.get("projetos"):
            items = [item for item in items if item["status"] == args.status]
        result[key] = items
        result["fontes"][key] = status
        print(f"{source['nome']}: {len(items)} oportunidades ({status['status']})")

    for key in SOURCES:
        for item in result[key]:
            if item["status"] not in ("aberto", "antigo", "sem_prazo"):
                continue
            grouped_key = {
                "aberto": "abertos",
                "antigo": "antigos",
                "sem_prazo": "sem_prazo",
            }[item["status"]]
            result[grouped_key].append(item)

    result["resumo"] = {
        "abertos": len(result["abertos"]),
        "antigos": len(result["antigos"]),
        "sem_prazo": len(result["sem_prazo"]),
    }
    result["subgrupos_cidades"] = {}
    for item in result["cidades"]:
        result["subgrupos_cidades"].setdefault(item["subgrupo"], []).append(
            {"titulo": item["titulo"], "link_projeto": item["link_projeto"]}
        )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = Path(f"oportunidades_governo_{timestamp}.json")
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Resultado salvo em: {output}")
    print(f"Total: {sum(len(result[key]) for key in SOURCES)}")


if __name__ == "__main__":
    main()
