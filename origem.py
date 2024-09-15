import json
import requests

def obter_informacoes_geograficas(ip):
    try:
        resposta = requests.get(f'https://ipinfo.io/{ip}/json')
        if resposta.status_code == 200:
            dados = resposta.json()
            cidade = dados.get('city', 'Cidade não especificada')
            regiao = dados.get('region', 'Região não especificada')
            pais = dados.get('country', 'País não especificado')
            return f"{cidade}, {regiao}, {pais}"
        else:
            return 'Informações geográficas não encontradas'
    except requests.RequestException as e:
        return f"Erro ao obter informações geográficas: {e}"

try:
    # Carregar o arquivo JSON
    with open('download1.json', 'r') as arquivo:
        dados = json.load(arquivo)

    resultados = []
    latencias = []

    # Iterar sobre cada item na lista de dados
    for item in dados:
        origem_analise = item.get('src_addr', 'Origem da análise não especificada')
        destino_analise = item.get('dst_addr', 'Destino da análise não especificado')
        origem_geo = obter_informacoes_geograficas(origem_analise)
        destino_geo = obter_informacoes_geograficas(destino_analise)
        print(f"Origem da Análise: {origem_analise} ({origem_geo})")
        print(f"Destino da Análise: {destino_analise} ({destino_geo})")
        resultados.append(f"Origem da Análise: {origem_analise} ({origem_geo})")
        resultados.append(f"Destino da Análise: {destino_analise} ({destino_geo})")

        # Iterar sobre os resultados para extrair a origem de cada "probe"
        for resultado in item.get('result', []):
            for probe in resultado.get('result', []):
                origem_probe = probe.get('from', 'Origem da probe não especificada')
                latencia = probe.get('rtt', 'Latência não especificada')
                origem_probe_geo = obter_informacoes_geograficas(origem_probe)
                print(f"Origem da Probe: {origem_probe} ({origem_probe_geo}), Latência: {latencia}")
                resultados.append(f"Origem da Probe: {origem_probe} ({origem_probe_geo}), Latência: {latencia}")
                if isinstance(latencia, (int, float)):
                    latencias.append(latencia)

    # Calcular resumo das latências
    if latencias:
        melhor_latencia = min(latencias)
        pior_latencia = max(latencias)
        media_latencia = sum(latencias) / len(latencias)
        resumo = (
            f"\nResumo das Latências:\n"
            f"Melhor Latência: {melhor_latencia}\n"
            f"Pior Latência: {pior_latencia}\n"
            f"Média das Latências: {media_latencia:.2f}\n"
        )
        print(resumo)
        resultados.append(resumo)

    # Escrever resultados em um arquivo .txt
    with open('resultados.txt', 'w') as arquivo_resultados:
        for linha in resultados:
            arquivo_resultados.write(linha + '\n')

except json.JSONDecodeError as e:
    print(f"Erro ao decodificar o JSON: {e}")
except FileNotFoundError:
    print("Arquivo JSON não encontrado.")