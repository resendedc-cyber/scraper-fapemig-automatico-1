#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gerador de Relatórios com Dados Reais
Cria relatórios para CNPq, FAPEMIG e UFJF usando dados extraídos
"""

import json
import re
from datetime import datetime

def limpar_texto(texto):
    """Limpa o texto removendo caracteres HTML e formatação"""
    if not texto:
        return ""
    
    # Remove caracteres HTML
    texto = re.sub(r'&#\d+;', '', texto)
    texto = re.sub(r'<[^>]+>', '', texto)
    texto = re.sub(r'le-\d+">', '', texto)
    texto = re.sub(r'="collapse">', '', texto)
    texto = re.sub(r'<s', '', texto)
    texto = re.sub(r'<i>', '', texto)
    
    # Remove espaços extras
    texto = re.sub(r'\s+', ' ', texto).strip()
    
    return texto

def gerar_relatorio_texto_unificado(chamadas_cnpq, chamadas_fapemig, chamadas_ufjf):
    """
    Gera relatório unificado em formato de texto
    """
    relatorio = []
    relatorio.append("🎯 RELATÓRIO COMPLETO DE CHAMADAS E OPORTUNIDADES")
    relatorio.append("=" * 70)
    relatorio.append(f"📅 Data do relatório: {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
    relatorio.append(f"📊 Total geral: {len(chamadas_cnpq) + len(chamadas_fapemig) + len(chamadas_ufjf)} chamadas")
    relatorio.append("")
    
    # CNPq
    if chamadas_cnpq:
        relatorio.append("🔬 CNPq - CONSELHO NACIONAL DE DESENVOLVIMENTO CIENTÍFICO E TECNOLÓGICO")
        relatorio.append("-" * 60)
        relatorio.append(f"📊 Total: {len(chamadas_cnpq)} chamadas")
        relatorio.append("")
        
        for i, chamada in enumerate(chamadas_cnpq, 1):
            titulo_limpo = limpar_texto(chamada['titulo'])
            relatorio.append(f"{i}. {titulo_limpo}")
            
            if chamada.get('numero'):
                relatorio.append(f"   🔢 Número: {chamada['numero']}")
            
            if chamada.get('prazo_final'):
                relatorio.append(f"   ⏰ Prazo: {chamada['prazo_final']}")
            
            if chamada.get('link_pdf'):
                relatorio.append(f"   🔗 Link: {chamada['link_pdf']}")
            
            relatorio.append("")
    
    # FAPEMIG
    if chamadas_fapemig:
        relatorio.append("🏛️ FAPEMIG - FUNDAÇÃO DE AMPARO À PESQUISA DO ESTADO DE MINAS GERAIS")
        relatorio.append("-" * 60)
        relatorio.append(f"📊 Total: {len(chamadas_fapemig)} chamadas")
        relatorio.append("")
        
        for i, chamada in enumerate(chamadas_fapemig, 1):
            titulo_limpo = limpar_texto(chamada['titulo'])
            relatorio.append(f"{i}. {titulo_limpo}")
            
            if chamada.get('numero'):
                relatorio.append(f"   🔢 Número: {chamada['numero']}")
            
            if chamada.get('prazo_final'):
                relatorio.append(f"   ⏰ Prazo: {chamada['prazo_final']}")
            
            if chamada.get('link_pdf'):
                relatorio.append(f"   🔗 Link: {chamada['link_pdf']}")
            
            relatorio.append("")
    
    # UFJF
    if chamadas_ufjf:
        relatorio.append("🎓 UFJF - UNIVERSIDADE FEDERAL DE JUIZ DE FORA")
        relatorio.append("-" * 60)
        relatorio.append(f"📊 Total: {len(chamadas_ufjf)} chamadas")
        relatorio.append("")
        
        for i, chamada in enumerate(chamadas_ufjf, 1):
            titulo_limpo = limpar_texto(chamada['titulo'])
            relatorio.append(f"{i}. {titulo_limpo}")
            
            if chamada.get('numero'):
                relatorio.append(f"   🔢 Número: {chamada['numero']}")
            
            if chamada.get('prazo_final'):
                relatorio.append(f"   ⏰ Prazo: {chamada['prazo_final']}")
            
            if chamada.get('link_pdf'):
                relatorio.append(f"   🔗 Link: {chamada['link_pdf']}")
            
            relatorio.append("")
    
    relatorio.append("📋 Fontes:")
    relatorio.append("   • CNPq: http://www.cnpq.br/")
    relatorio.append("   • FAPEMIG: http://www.fapemig.br/")
    relatorio.append("   • UFJF: https://www2.ufjf.br/ufjf/editais/")
    
    return "\n".join(relatorio)

def gerar_relatorio_html_unificado(chamadas_cnpq, chamadas_fapemig, chamadas_ufjf):
    """
    Gera relatório unificado em formato HTML
    """
    total_geral = len(chamadas_cnpq) + len(chamadas_fapemig) + len(chamadas_ufjf)
    
    html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório Completo - {datetime.now().strftime('%d/%m/%Y')}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
            margin-top: 10px;
        }}
        .stats {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            border-bottom: 1px solid #e9ecef;
        }}
        .stats .stat-item {{
            display: inline-block;
            margin: 0 15px;
            padding: 15px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .stats .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #3498db;
        }}
        .stats .stat-label {{
            color: #666;
            font-size: 0.9em;
        }}
        .content {{
            padding: 30px;
        }}
        .fonte-section {{
            margin: 40px 0;
        }}
        .fonte-header {{
            background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .fonte-header h2 {{
            margin: 0;
            font-size: 1.8em;
        }}
        .fonte-header .total {{
            font-size: 1.1em;
            opacity: 0.9;
            margin-top: 5px;
        }}
        .chamada {{
            background: #f8f9fa;
            margin: 20px 0;
            padding: 25px;
            border-radius: 10px;
            border-left: 5px solid #3498db;
            transition: transform 0.2s;
        }}
        .chamada:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }}
        .chamada h3 {{
            margin: 0 0 15px 0;
            color: #2c3e50;
            font-size: 1.3em;
        }}
        .chamada .meta {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }}
        .meta-item {{
            background: white;
            padding: 10px 15px;
            border-radius: 8px;
            border: 1px solid #e9ecef;
        }}
        .meta-item .label {{
            font-weight: bold;
            color: #666;
            font-size: 0.8em;
            text-transform: uppercase;
        }}
        .meta-item .value {{
            color: #2c3e50;
            margin-top: 5px;
        }}
        .footer {{
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }}
        .cnpq {{
            border-left-color: #e67e22 !important;
        }}
        .fapemig {{
            border-left-color: #9b59b6 !important;
        }}
        .ufjf {{
            border-left-color: #27ae60 !important;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Relatório Completo</h1>
            <div class="subtitle">Chamadas e Oportunidades de Pesquisa - DADOS REAIS</div>
        </div>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">{total_geral}</div>
                <div class="stat-label">Total de Chamadas</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{len(chamadas_cnpq)}</div>
                <div class="stat-label">CNPq</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{len(chamadas_fapemig)}</div>
                <div class="stat-label">FAPEMIG</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{len(chamadas_ufjf)}</div>
                <div class="stat-label">UFJF</div>
            </div>
        </div>
        
        <div class="content">
"""
    
    # CNPq
    if chamadas_cnpq:
        html += f"""
            <div class="fonte-section">
                <div class="fonte-header">
                    <h2>🔬 CNPq - Conselho Nacional de Desenvolvimento Científico e Tecnológico</h2>
                    <div class="total">📊 {len(chamadas_cnpq)} chamadas encontradas</div>
                </div>
"""
        
        for i, chamada in enumerate(chamadas_cnpq, 1):
            titulo_limpo = limpar_texto(chamada['titulo'])
            html += f"""
                <div class="chamada cnpq">
                    <h3>{i}. {titulo_limpo}</h3>
                    <div class="meta">
"""
            
            if chamada.get('numero'):
                html += f"""
                        <div class="meta-item">
                            <div class="label">Número</div>
                            <div class="value">🔢 {chamada['numero']}</div>
                        </div>
"""
            
            if chamada.get('prazo_final'):
                html += f"""
                        <div class="meta-item">
                            <div class="label">Prazo Final</div>
                            <div class="value">⏰ {chamada['prazo_final']}</div>
                        </div>
"""
            
            if chamada.get('link_pdf'):
                html += f"""
                        <div class="meta-item">
                            <div class="label">Link</div>
                            <div class="value">🔗 <a href="{chamada['link_pdf']}" target="_blank">Acessar</a></div>
                        </div>
"""
            
            html += """
                    </div>
                </div>
"""
        
        html += """
                </div>
"""
    
    # FAPEMIG
    if chamadas_fapemig:
        html += f"""
            <div class="fonte-section">
                <div class="fonte-header">
                    <h2>🏛️ FAPEMIG - Fundação de Amparo à Pesquisa do Estado de Minas Gerais</h2>
                    <div class="total">📊 {len(chamadas_fapemig)} chamadas encontradas</div>
                </div>
"""
        
        for i, chamada in enumerate(chamadas_fapemig, 1):
            titulo_limpo = limpar_texto(chamada['titulo'])
            html += f"""
                <div class="chamada fapemig">
                    <h3>{i}. {titulo_limpo}</h3>
                    <div class="meta">
"""
            
            if chamada.get('numero'):
                html += f"""
                        <div class="meta-item">
                            <div class="label">Número</div>
                            <div class="value">🔢 {chamada['numero']}</div>
                        </div>
"""
            
            if chamada.get('prazo_final'):
                html += f"""
                        <div class="meta-item">
                            <div class="label">Prazo Final</div>
                            <div class="value">⏰ {chamada['prazo_final']}</div>
                        </div>
"""
            
            if chamada.get('link_pdf'):
                html += f"""
                        <div class="meta-item">
                            <div class="label">Link</div>
                            <div class="value">🔗 <a href="{chamada['link_pdf']}" target="_blank">Acessar</a></div>
                        </div>
"""
            
            html += """
                    </div>
                </div>
"""
        
        html += """
                </div>
"""
    
    # UFJF
    if chamadas_ufjf:
        html += f"""
            <div class="fonte-section">
                <div class="fonte-header">
                    <h2>🎓 UFJF - Universidade Federal de Juiz de Fora</h2>
                    <div class="total">📊 {len(chamadas_ufjf)} chamadas encontradas</div>
                </div>
"""
        
        for i, chamada in enumerate(chamadas_ufjf, 1):
            titulo_limpo = limpar_texto(chamada['titulo'])
            html += f"""
                <div class="chamada ufjf">
                    <h3>{i}. {titulo_limpo}</h3>
                    <div class="meta">
"""
            
            if chamada.get('numero'):
                html += f"""
                        <div class="meta-item">
                            <div class="label">Número</div>
                            <div class="value">🔢 {chamada['numero']}</div>
                        </div>
"""
            
            if chamada.get('prazo_final'):
                html += f"""
                        <div class="meta-item">
                            <div class="label">Prazo Final</div>
                            <div class="value">⏰ {chamada['prazo_final']}</div>
                        </div>
"""
            
            if chamada.get('link_pdf'):
                html += f"""
                        <div class="meta-item">
                            <div class="label">Link</div>
                            <div class="value">🔗 <a href="{chamada['link_pdf']}" target="_blank">Acessar</a></div>
                        </div>
"""
            
            html += """
                    </div>
                </div>
"""
        
        html += """
                </div>
"""
    
    html += """
        </div>
        
        <div class="footer">
            📋 Fontes:<br>
            🔬 CNPq: <a href="http://www.cnpq.br/" target="_blank" style="color: #3498db;">http://www.cnpq.br/</a><br>
            🏛️ FAPEMIG: <a href="http://www.fapemig.br/" target="_blank" style="color: #3498db;">http://www.fapemig.br/</a><br>
            🎓 UFJF: <a href="https://www2.ufjf.br/ufjf/editais/" target="_blank" style="color: #3498db;">https://www2.ufjf.br/ufjf/editais/</a><br>
            📅 Relatório gerado em: """ + datetime.now().strftime('%d/%m/%Y às %H:%M') + """<br>
            🎯 DADOS REAIS EXTRAÍDOS DOS SITES OFICIAIS
        </div>
    </div>
</body>
</html>
"""
    
    return html

def gerar_relatorio_markdown_unificado(chamadas_cnpq, chamadas_fapemig, chamadas_ufjf):
    """
    Gera relatório unificado em formato Markdown
    """
    total_geral = len(chamadas_cnpq) + len(chamadas_fapemig) + len(chamadas_ufjf)
    
    relatorio = []
    relatorio.append("# 🎯 Relatório Completo de Chamadas e Oportunidades")
    relatorio.append("")
    relatorio.append(f"**Data do relatório:** {datetime.now().strftime('%d/%m/%Y às %H:%M')}  ")
    relatorio.append(f"**Total geral:** {total_geral} chamadas  ")
    relatorio.append("**🎯 DADOS REAIS EXTRAÍDOS DOS SITES OFICIAIS**  ")
    relatorio.append("")
    
    # CNPq
    if chamadas_cnpq:
        relatorio.append("## 🔬 CNPq - Conselho Nacional de Desenvolvimento Científico e Tecnológico")
        relatorio.append(f"**Total:** {len(chamadas_cnpq)} chamadas  ")
        relatorio.append("")
        
        for i, chamada in enumerate(chamadas_cnpq, 1):
            titulo_limpo = limpar_texto(chamada['titulo'])
            relatorio.append(f"### {i}. {titulo_limpo}")
            relatorio.append("")
            
            if chamada.get('numero'):
                relatorio.append(f"**Número:** {chamada['numero']}  ")
            
            if chamada.get('prazo_final'):
                relatorio.append(f"**Prazo Final:** {chamada['prazo_final']}  ")
            
            if chamada.get('link_pdf'):
                relatorio.append(f"**Link:** [{chamada['link_pdf']}]({chamada['link_pdf']})  ")
            
            relatorio.append("")
            relatorio.append("---")
            relatorio.append("")
    
    # FAPEMIG
    if chamadas_fapemig:
        relatorio.append("## 🏛️ FAPEMIG - Fundação de Amparo à Pesquisa do Estado de Minas Gerais")
        relatorio.append(f"**Total:** {len(chamadas_fapemig)} chamadas  ")
        relatorio.append("")
        
        for i, chamada in enumerate(chamadas_fapemig, 1):
            titulo_limpo = limpar_texto(chamada['titulo'])
            relatorio.append(f"### {i}. {titulo_limpo}")
            relatorio.append("")
            
            if chamada.get('numero'):
                relatorio.append(f"**Número:** {chamada['numero']}  ")
            
            if chamada.get('prazo_final'):
                relatorio.append(f"**Prazo Final:** {chamada['prazo_final']}  ")
            
            if chamada.get('link_pdf'):
                relatorio.append(f"**Link:** [{chamada['link_pdf']}]({chamada['link_pdf']})  ")
            
            relatorio.append("")
            relatorio.append("---")
            relatorio.append("")
    
    # UFJF
    if chamadas_ufjf:
        relatorio.append("## 🎓 UFJF - Universidade Federal de Juiz de Fora")
        relatorio.append(f"**Total:** {len(chamadas_ufjf)} chamadas  ")
        relatorio.append("")
        
        for i, chamada in enumerate(chamadas_ufjf, 1):
            titulo_limpo = limpar_texto(chamada['titulo'])
            relatorio.append(f"### {i}. {titulo_limpo}")
            relatorio.append("")
            
            if chamada.get('numero'):
                relatorio.append(f"**Número:** {chamada['numero']}  ")
            
            if chamada.get('prazo_final'):
                relatorio.append(f"**Prazo Final:** {chamada['prazo_final']}  ")
            
            if chamada.get('link_pdf'):
                relatorio.append(f"**Link:** [{chamada['link_pdf']}]({chamada['link_pdf']})  ")
            
            relatorio.append("")
            relatorio.append("---")
            relatorio.append("")
    
    relatorio.append("---")
    relatorio.append("**Fontes:**  ")
    relatorio.append("- 🔬 CNPq: http://www.cnpq.br/  ")
    relatorio.append("- 🏛️ FAPEMIG: http://www.fapemig.br/  ")
    relatorio.append("- 🎓 UFJF: https://www2.ufjf.br/ufjf/editais/  ")
    relatorio.append("")
    relatorio.append("**🎯 IMPORTANTE:** Este relatório contém dados reais extraídos diretamente dos sites oficiais das instituições.")
    
    return "\n".join(relatorio)

def main():
    """
    Função principal
    """
    print("🚀 Gerador de Relatórios com Dados Reais")
    print("=" * 50)
    
    # Carrega os dados reais extraídos
    try:
        with open('dados_reais_simples_20250817_230420.json', 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        chamadas_cnpq = dados.get('cnpq', [])
        chamadas_fapemig = dados.get('fapemig', [])
        chamadas_ufjf = dados.get('ufjf', [])
        
        print(f"✅ Dados carregados:")
        print(f"   • CNPq: {len(chamadas_cnpq)} chamadas")
        print(f"   • FAPEMIG: {len(chamadas_fapemig)} chamadas")
        print(f"   • UFJF: {len(chamadas_ufjf)} chamadas")
        
    except FileNotFoundError:
        print("❌ Arquivo de dados não encontrado!")
        print("💡 Execute primeiro o scraper para obter dados reais")
        return
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        return
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Gera relatório unificado em texto
    relatorio_texto = gerar_relatorio_texto_unificado(chamadas_cnpq, chamadas_fapemig, chamadas_ufjf)
    with open(f"relatorio_completo_dados_reais_texto_{timestamp}.txt", 'w', encoding='utf-8') as f:
        f.write(relatorio_texto)
    print(f"✅ Relatório completo em texto salvo: relatorio_completo_dados_reais_texto_{timestamp}.txt")
    
    # Gera relatório unificado em HTML
    relatorio_html = gerar_relatorio_html_unificado(chamadas_cnpq, chamadas_fapemig, chamadas_ufjf)
    with open(f"relatorio_completo_dados_reais_html_{timestamp}.html", 'w', encoding='utf-8') as f:
        f.write(relatorio_html)
    print(f"✅ Relatório completo em HTML salvo: relatorio_completo_dados_reais_html_{timestamp}.html")
    
    # Gera relatório unificado em Markdown
    relatorio_md = gerar_relatorio_markdown_unificado(chamadas_cnpq, chamadas_fapemig, chamadas_ufjf)
    with open(f"relatorio_completo_dados_reais_md_{timestamp}.md", 'w', encoding='utf-8') as f:
        f.write(relatorio_md)
    print(f"✅ Relatório completo em Markdown salvo: relatorio_completo_dados_reais_md_{timestamp}.md")
    
    print(f"\n🎉 Relatórios completos com dados reais gerados com sucesso!")
    print("📁 Arquivos criados:")
    print("   • .txt - Para emails e cópia/cola")
    print("   • .html - Para apresentações e web")
    print("   • .md - Para documentação e GitHub")
    print(f"\n📊 Resumo:")
    print(f"   • CNPq: {len(chamadas_cnpq)} chamadas")
    print(f"   • FAPEMIG: {len(chamadas_fapemig)} chamadas")
    print(f"   • UFJF: {len(chamadas_ufjf)} chamadas")
    print(f"   • Total: {len(chamadas_cnpq) + len(chamadas_fapemig) + len(chamadas_ufjf)} chamadas")
    print("\n🎯 Todos os dados são REAIS e foram extraídos diretamente dos sites oficiais!")

if __name__ == "__main__":
    main()
