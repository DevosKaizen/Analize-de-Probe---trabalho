import json
import requests
from tqdm import tqdm
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def obter_informacoes_geograficas(ip, cache):
    if ip in cache:
        return cache[ip]
    
    try:
        resposta = requests.get(f'https://ipinfo.io/{ip}/json')
        if resposta.status_code == 200:
            dados = resposta.json()
            cidade = dados.get('city', 'Cidade não especificada')
            regiao = dados.get('region', 'Região não especificada')
            pais = dados.get('country', 'País não especificado')
            info_geo = f"{cidade}, {regiao}, {pais}"
            cache[ip] = info_geo
            return info_geo
        else:
            return 'Informações geográficas não encontradas'
    except requests.RequestException as e:
        return f"Erro ao obter informações geográficas: {e}"

def processar_item(item, cache_geo):
    resultados_item = []
    latencias_item = []

    origem_analise = item.get('src_addr', 'Origem da análise não especificada')
    destino_analise = item.get('dst_addr', 'Destino da análise não especificado')
    timestamp = item.get('timestamp', 'Timestamp não especificado')
    origem_geo = obter_informacoes_geograficas(origem_analise, cache_geo)
    destino_geo = obter_informacoes_geograficas(destino_analise, cache_geo)
    resultados_item.append(f"Origem da Análise: {origem_analise} ({origem_geo})")
    resultados_item.append(f"Destino da Análise: {destino_analise} ({destino_geo})")
    resultados_item.append(f"Timestamp: {timestamp}")

    # Iterar sobre os resultados para extrair a origem de cada "probe"
    for resultado in item.get('result', []):
        numero_hops = len(resultado.get('result', []))
        for probe in resultado.get('result', []):
            origem_probe = probe.get('from', 'Origem da probe não especificada')
            latencia = probe.get('rtt', 'Latência não especificada')
            origem_probe_geo = obter_informacoes_geograficas(origem_probe, cache_geo)
            resultados_item.append(f"Origem da Probe: {origem_probe} ({origem_probe_geo}), Latência: {latencia}, Número de Hops: {numero_hops}")
            if isinstance(latencia, (int, float)):
                latencias_item.append(latencia)

    return resultados_item, latencias_item

try:
    # Carregar o arquivo JSON
    with open('download1.json', 'r') as arquivo:
        dados = json.load(arquivo)

    resultados = []
    latencias = []
    cache_geo = {}

    total_items = sum(len(item.get('result', [])) for item in dados)
    progress_bar = tqdm(total=total_items, desc="Processando", unit="item")

    # Usar ThreadPoolExecutor para paralelizar o processamento
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(processar_item, item, cache_geo) for item in dados]
        for future in as_completed(futures):
            resultados_item, latencias_item = future.result()
            resultados.extend(resultados_item)
            latencias.extend(latencias_item)
            progress_bar.update(len(resultados_item))

    progress_bar.close()

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