import pandas as pd
import matplotlib.pyplot as plt
import json

# Função para carregar dados das medições de um arquivo JSON
def carregar_dados(arquivo_json):
    with open(arquivo_json, 'r') as file:
        data = json.load(file)
    
    registros = []
    for medicao in data:
        destino = medicao['dst_addr']
        probe = medicao['prb_id']
        for hop in medicao['result']:
            for resultado in hop['result']:
                if 'rtt' in resultado:
                    registros.append({
                        'destino': destino,
                        'probe': probe,
                        'latencia': resultado['rtt'],
                        'saltos': hop['hop'],
                        'timestamp': medicao['timestamp']
                    })
    
    return pd.DataFrame(registros)

# Função para gerar gráficos de latência
def gerar_graficos_latencia(dados):
    if 'destino' not in dados.columns or 'probe' not in dados.columns or 'latencia' not in dados.columns:
        print("Erro: O arquivo JSON não contém as colunas necessárias ('destino', 'probe', 'latencia').")
        return
    for destino in dados['destino'].unique():
        df_destino = dados[dados['destino'] == destino]
        plt.figure()
        for probe in df_destino['probe'].unique():
            df_probe = df_destino[df_destino['probe'] == probe]
            plt.plot(df_probe['timestamp'], df_probe['latencia'], label=f'Probe {probe}')
        plt.title(f'Latência para {destino}')
        plt.xlabel('Tempo')
        plt.ylabel('Latência (ms)')
        plt.legend()
        plt.show()

# Função para gerar gráficos de número de saltos
def gerar_graficos_saltos(dados):
    if 'destino' not in dados.columns or 'probe' not in dados.columns or 'saltos' not in dados.columns:
        print("Erro: O arquivo JSON não contém as colunas necessárias ('destino', 'probe', 'saltos').")
        return
    for destino in dados['destino'].unique():
        df_destino = dados[dados['destino'] == destino]
        plt.figure()
        for probe in df_destino['probe'].unique():
            df_probe = df_destino[df_destino['probe'] == probe]
            plt.plot(df_probe['timestamp'], df_probe['saltos'], label=f'Probe {probe}')
        plt.title(f'Número de Saltos para {destino}')
        plt.xlabel('Tempo')
        plt.ylabel('Número de Saltos')
        plt.legend()
        plt.show()

# Função para gerar gráficos de correlação
def gerar_graficos_correlacao(dados):
    if 'destino' not in dados.columns or 'latencia' not in dados.columns or 'saltos' not in dados.columns:
        print("Erro: O arquivo JSON não contém as colunas necessárias ('destino', 'latencia', 'saltos').")
        return
    for destino in dados['destino'].unique():
        df_destino = dados[dados['destino'] == destino]
        plt.figure()
        plt.scatter(df_destino['saltos'], df_destino['latencia'])
        plt.title(f'Correlação entre Latência e Número de Saltos para {destino}')
        plt.xlabel('Número de Saltos')
        plt.ylabel('Latência (ms)')
        plt.show()

# Perguntar ao usuário qual arquivo JSON ele deseja analisar
arquivo_json = input("Digite o caminho do arquivo JSON que você deseja analisar: ")

# Carregar dados e gerar gráficos
dados = carregar_dados(arquivo_json)
gerar_graficos_latencia(dados)
gerar_graficos_saltos(dados)
gerar_graficos_correlacao(dados)