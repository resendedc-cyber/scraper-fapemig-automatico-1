# 🚀 Scraper de Editais e Chamadas - CNPq, FAPEMIG e UFJF

Sistema automatizado para captura de editais, chamadas públicas e oportunidades de fomento das principais agências brasileiras.

## 📋 Funcionalidades

### 🔍 Scraper Rápido (`scraper_rapido.py`)
- **Execução ultra-rápida** para coleta diária
- **Múltiplas fontes**: CNPq, FAPEMIG e UFJF
- **Timeouts otimizados** para ambiente CI/CD
- **Fallback automático** para URLs alternativas

### 🔍 Scraper Detalhado CNPq (`scraper_cnpq_detalhado.py`)
- **Extração especializada** para chamadas do CNPq
- **Informações detalhadas**: datas de inscrição, links permanentes, descrições completas
- **Padrões inteligentes** para extração de dados estruturados
- **Dados de exemplo** baseados em chamadas reais

### 🔎 Fontes monitoradas
- CNPq, CAPES, MCTI, FAPEMIG e UFJF/CRITT.
- IEL, usando o portal IEL acessível e fallback do portal nacional da indústria.
- Ministério das Cidades, usando o portal oficial de assuntos e programas.

### 🎓 Editais UFJF
- Coleta somente editais de bolsas publicados pelo CRITT/UFJF.
- Fonte oficial: `https://www2.ufjf.br/critt/vagas-e-bolsas-do-critt/controle-de-editais-2026/`

## 🏗️ Arquitetura

```
meu-scraper/
├── .github/workflows/
│   └── scraper.yml          # Workflow automatizado GitHub Actions
├── scraper_rapido.py        # Scraper principal (rápido)
├── scraper_cnpq_detalhado.py # Scraper especializado CNPq
├── scraper_simples.py       # Versão básica
├── requirements-scraper.txt  # Dependências Python
└── README.md                # Documentação
```

## 🚀 Execução Automatizada

### GitHub Actions
- **Agendamento**: Execução diária às 08:00 UTC (05:00 BRT)
- **Trigger manual**: Disponível via interface do GitHub
- **Push automático**: Executa em commits para main/master
- **Artefatos**: Upload automático dos resultados JSON

### Execução Local
```bash
# Scraper rápido
python scraper_rapido.py

# Scraper detalhado CNPq
python scraper_cnpq_detalhado.py
```

## 📊 Saídas

### Scraper Rápido
- `editais_rapidos_YYYYMMDD_HHMMSS.json`
- Estrutura: UFJF, FAPEMIG, CNPq

### Scraper Detalhado CNPq
- `chamadas_cnpq_detalhadas_YYYYMMDD_HHMMSS.json`
- Estrutura detalhada com:
  - Título da chamada
  - Descrição completa
  - Datas de inscrição
  - Links permanentes
  - Status e fonte

## 🔧 Configuração

### Dependências
```bash
pip install -r requirements-scraper.txt
```

### Requisitos do Sistema
- Python 3.10+
- Chrome/Chromium
- Selenium WebDriver

## 📈 Monitoramento

### Logs de Execução
- Timestamps detalhados
- Contadores de itens extraídos
- Tratamento de erros robusto
- Resumos de execução

### Métricas
- Duração total de execução
- Quantidade de itens por fonte
- Taxa de sucesso por URL
- Fallbacks utilizados

## 🎯 Casos de Uso

### Pesquisadores
- Acompanhamento de editais de fomento
- Identificação de oportunidades de bolsas
- Monitoramento de prazos de inscrição

### Instituições
- Mapeamento de oportunidades disponíveis
- Análise de tendências de fomento
- Planejamento estratégico de captação

### Desenvolvedores
- Base para sistemas de notificação
- Integração com CRMs acadêmicos
- Dashboards de oportunidades

## 🔄 Manutenção

### Atualizações
- URLs e seletores CSS atualizados automaticamente
- Fallbacks para mudanças de estrutura
- Logs detalhados para debugging

### Escalabilidade
- Limitação de resultados por execução
- Timeouts configuráveis
- Tratamento de erros não-bloqueante

## 📝 Licença

Projeto desenvolvido para fins educacionais e de pesquisa.

## 🤝 Contribuições

Contribuições são bem-vindas! Por favor, abra uma issue ou pull request.

---

**Última atualização**: Janeiro 2025
**Versão**: 2.0 - Com scraper detalhado CNPq
