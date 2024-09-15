import json
import requests
from tqdm import tqdm
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import csv

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
    resultados_item.append((origem_analise, origem_geo, destino_analise, destino_geo, timestamp))

    # Iterar sobre os resultados para extrair a origem de cada "probe"
    for resultado in item.get('result', []):
        numero_hops = len(resultado.get('result', []))
        for probe in resultado.get('result', []):
            origem_probe = probe.get('from', 'Origem da probe não especificada')
            latencia = probe.get('rtt', 'Latência não especificada')
            origem_probe_geo = obter_informacoes_geograficas(origem_probe, cache_geo)
            resultados_item.append((origem_probe, origem_probe_geo, latencia, numero_hops))
            if isinstance(latencia, (int, float)):
                latencias_item.append((latencia, origem_probe_geo))

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
        melhor_latencia = min(latencias, key=lambda x: x[0])
        pior_latencia = max(latencias, key=lambda x: x[0])
        media_latencia = sum(x[0] for x in latencias) / len(latencias)
        
        # Distribuição das latências
        latencias_abaixo_100ms = len([x for x in latencias if x[0] < 100])
        latencias_100ms_500ms = len([x for x in latencias if 100 <= x[0] < 500])
        latencias_acima_500ms = len([x for x in latencias if x[0] >= 500])
        
        resumo = (
            f"\nResumo das Latências:\n"
            f"Melhor Latência: {melhor_latencia[0]} ({melhor_latencia[1]})\n"
            f"Pior Latência: {pior_latencia[0]} ({pior_latencia[1]})\n"
            f"Média das Latências: {media_latencia:.2f}\n"
            f"Latências abaixo de 100ms: {latencias_abaixo_100ms}\n"
            f"Latências entre 100ms e 500ms: {latencias_100ms_500ms}\n"
            f"Latências acima de 500ms: {latencias_acima_500ms}\n"
        )
        
        explicacao = (
            "\nExplicação dos Resultados:\n"
            "Melhor Latência: A menor latência registrada, indicando a menor demora na comunicação.\n"
            "Pior Latência: A maior latência registrada, indicando a maior demora na comunicação.\n"
            "Média das Latências: A média das latências registradas, fornecendo uma visão geral do desempenho.\n"
            "Latências abaixo de 100ms: Quantidade de latências consideradas muito boas.\n"
            "Latências entre 100ms e 500ms: Quantidade de latências consideradas aceitáveis.\n"
            "Latências acima de 500ms: Quantidade de latências consideradas ruins.\n"
        )
        
        print(resumo)
        print(explicacao)
        resultados.append(("Resumo das La