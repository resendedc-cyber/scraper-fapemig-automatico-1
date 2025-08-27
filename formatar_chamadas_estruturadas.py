import json
import re
from datetime import datetime
from pathlib import Path

def extrair_periodo_do_texto(texto):
    """
    Tenta extrair período de inscrição/prazo do texto usando regex
    """
    if not texto:
        return ""
    
    # Padrões para datas brasileiras
    padroes = [
        r'(\d{1,2}/\d{1,2}/\d{2,4})\s*(?:a|até|-)\s*(\d{1,2}/\d{1,2}/\d{2,4})',  # 01/08/2025 a 30/09/2025
        r'(\d{1,2}/\d{1,2}/\d{2,4})',  # Data única
        r'prazo.*?(\d{1,2}/\d{1,2}/\d{2,4})',  # "prazo até 30/09/2025"
        r'inscrições.*?(\d{1,2}/\d{1,2}/\d{2,4})',  # "inscrições até 30/09/2025"
    ]
    
    for padrao in padroes:
        match = re.search(padrao, texto, re.I)
        if match:
            if len(match.groups()) == 2:
                return f"{match.group(1)} a {match.group(2)}"
            else:
                return match.group(1)
    
    return ""

def formatar_chamada_cnpq(chamada):
    """Formata uma chamada do CNPq"""
    nome = chamada.get('titulo', 'Sem título')
    periodo = chamada.get('data_inscricao', '')
    link = chamada.get('link_permanente', '')
    
    # Se não tem período, tenta extrair da descrição
    if not periodo:
        periodo = extrair_periodo_do_texto(chamada.get('descricao', ''))
    
    return {
        'nome': nome,
        'periodo': periodo,
        'link': link,
        'fonte': 'CNPq'
    }

def formatar_chamada_fapemig(chamada):
    """Formata uma chamada do FAPEMIG"""
    nome = chamada.get('titulo', 'Sem título')
    periodo = chamada.get('data_limite', '')
    link = chamada.get('link_pdf', '')
    
    # Se não tem período, tenta extrair do título
    if not periodo:
        periodo = extrair_periodo_do_texto(nome)
    
    return {
        'nome': nome,
        'periodo': periodo,
        'link': link,
        'fonte': 'FAPEMIG'
    }

def formatar_chamada_ufmg(chamada):
    """Formata uma chamada da UFMG"""
    nome = chamada.get('titulo', 'Sem título')
    periodo = chamada.get('data_limite', '')
    link = chamada.get('link_pdf', '')
    
    # Se não tem período, tenta extrair do título
    if not periodo:
        periodo = extrair_periodo_do_texto(nome)
    
    return {
        'nome': nome,
        'periodo': periodo,
        'link': link,
        'fonte': 'UFMG'
    }

def formatar_todas_chamadas(arquivo_json):
    """Formata todas as chamadas de um arquivo JSON"""
    try:
        with open(arquivo_json, 'r', encoding='utf-8') as f:
            dados = json.load(f)
    except Exception as e:
        print(f"Erro ao ler {arquivo_json}: {e}")
        return []
    
    chamadas_formatadas = []
    
    # Processa CNPq
    if 'cnpq' in dados and dados['cnpq']:
        for chamada in dados['cnpq']:
            chamadas_formatadas.append(formatar_chamada_cnpq(chamada))
    
    # Processa FAPEMIG
    if 'fapemig' in dados and dados['fapemig']:
        for chamada in dados['fapemig']:
            chamadas_formatadas.append(formatar_chamada_fapemig(chamada))
    
    # Processa UFMG
    if 'ufmg' in dados and dados['ufmg']:
        for chamada in dados['ufmg']:
            chamadas_formatadas.append(formatar_chamada_ufmg(chamada))
    
    # Processa chamadas_cnpq (formato alternativo)
    if 'chamadas_cnpq' in dados and dados['chamadas_cnpq']:
        for chamada in dados['chamadas_cnpq']:
            chamadas_formatadas.append(formatar_chamada_cnpq(chamada))
    
    return chamadas_formatadas

def exibir_chamadas_formatadas(chamadas):
    """Exibe as chamadas em formato legível"""
    if not chamadas:
        print("❌ Nenhuma chamada encontrada!")
        return
    
    print(f"🎯 Total de {len(chamadas)} chamadas encontradas:\n")
    
    for i, chamada in enumerate(chamadas, 1):
        print(f"{i}. {chamada['nome']}")
        if chamada['periodo']:
            print(f"   📅 {chamada['periodo']}")
        else:
            print(f"   📅 Período não especificado")
        
        if chamada['link']:
            print(f"   🔗 {chamada['link']}")
        else:
            print(f"   🔗 Link não disponível")
        
        print(f"   📋 Fonte: {chamada['fonte']}")
        print()

def main():
    """Função principal"""
    print("🔍 Formatador de Chamadas Estruturadas")
    print("=" * 50)
    
    # Lista arquivos JSON disponíveis
    arquivos_json = list(Path('.').glob('*.json'))
    
    if not arquivos_json:
        print("❌ Nenhum arquivo JSON encontrado no diretório atual!")
        return
    
    print("📁 Arquivos JSON disponíveis:")
    for i, arquivo in enumerate(arquivos_json, 1):
        print(f"   {i}. {arquivo.name}")
    
    print("\n" + "=" * 50)
    
    # Processa cada arquivo
    todas_chamadas = []
    
    for arquivo in arquivos_json:
        print(f"\n📖 Processando: {arquivo.name}")
        chamadas = formatar_todas_chamadas(arquivo)
        todas_chamadas.extend(chamadas)
        print(f"   ✅ {len(chamadas)} chamadas extraídas")
    
    print("\n" + "=" * 50)
    print("🎯 RESULTADO FINAL:")
    print("=" * 50)
    
    # Remove duplicatas baseado no nome
    chamadas_unicas = []
    nomes_vistos = set()
    
    for chamada in todas_chamadas:
        nome_limpo = re.sub(r'\s+', ' ', chamada['nome'].strip())
        if nome_limpo not in nomes_vistos:
            nomes_vistos.add(nome_limpo)
            chamadas_unicas.append(chamada)
    
    exibir_chamadas_formatadas(chamadas_unicas)
    
    # Salva resultado em arquivo
    resultado = {
        'chamadas_formatadas': chamadas_unicas,
        'total_chamadas': len(chamadas_unicas),
        'timestamp': datetime.now().isoformat(),
        'fontes': list(set(ch['fonte'] for ch in chamadas_unicas))
    }
    
    nome_arquivo = f"chamadas_formatadas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Resultado salvo em: {nome_arquivo}")

if __name__ == "__main__":
    main()


