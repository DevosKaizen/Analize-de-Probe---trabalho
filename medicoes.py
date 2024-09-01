import ripe.atlas.cousteau as atlas
import time

# Configurações das medições
destinos = ["8.8.8.8", "1.1.1.1", "208.67.222.222"]  # Exemplo de destinos
intervalo = 120 * 60  # 120 minutos em segundos
duracao = 2 * 24 * 60 * 60  # 2 dias em segundos

# Seleção das probes
probes = [
    # Adicione aqui os IDs das probes selecionadas
]

# Função para criar medições de traceroute
def criar_medicao(destino, probes):
    traceroute = atlas.Traceroute(
        af=4,
        target=destino,
        description="Traceroute para análise de desempenho",
        interval=intervalo,
        is_oneoff=False,
        packets=3,
        protocol="ICMP"
    )
    atlas_request = atlas.AtlasCreateRequest(
        start=int(time.time()),
        key="YOUR_API_KEY",
        measurements=[traceroute],
        sources=[atlas.Source(type="probes", value=",".join(map(str, probes)))],
        is_oneoff=False
    )
    return atlas_request.create()

# Criar medições para cada destino
for destino in destinos:
    criar_medicao(destino, probes)