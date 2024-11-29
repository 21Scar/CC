import subprocess
import re

def get_latency(target_ip):
    """
    Mede a latência (RTT) para um destino usando o comando 'ping'.
    :param target_ip: Endereço IP do destino.
    :return: Latência média em ms.
    """
    try:
        result = subprocess.run(
            ["ping", "-c", "4", target_ip],  # Envia 4 pacotes
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        output = result.stdout
        # Extrai a latência média usando regex
        match = re.search(r"rtt min/avg/max/mdev = [^/]+/([^/]+)/", output)
        if match:
            latency = float(match.group(1))
            return latency
        else:
            return None
    except Exception as e:
        print(f"Erro ao medir latência: {e}")
        return None

def get_packet_loss(target_ip):
    """
    Mede a perda de pacotes para um destino usando 'ping'.
    :param target_ip: Endereço IP do destino.
    :return: Percentual de pacotes perdidos.
    """
    try:
        result = subprocess.run(
            ["ping", "-c", "4", target_ip],  # Envia 4 pacotes
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        output = result.stdout
        # Extrai a perda de pacotes usando regex
        match = re.search(r"(\d+)% packet loss", output)
        if match:
            packet_loss = int(match.group(1))
            return packet_loss
        else:
            return 0
    except Exception as e:
        print(f"Erro ao medir perda de pacotes: {e}")
        return 0

def get_bandwidth(target_ip):
    """
    Mede a largura de banda usando a ferramenta 'iperf'.
    Certifique-se de que o iperf3 esteja instalado no sistema.
    :param target_ip: Endereço IP do servidor iperf.
    :return: Largura de banda em Mbps.
    """
    try:
        result = subprocess.run(
            ["iperf3", "-c", target_ip, "-t", "5"],  # Testa por 5 segundos
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        output = result.stdout
        # Extrai a largura de banda usando regex
        match = re.search(r"(\d+\.\d+)\s*Mbits/sec", output)
        if match:
            bandwidth = float(match.group(1))
            return bandwidth
        else:
            return None
    except FileNotFoundError:
        print("Erro: 'iperf3' não encontrado. Certifique-se de que está instalado.")
        return None
    except Exception as e:
        print(f"Erro ao medir largura de banda: {e}")
        return None

def collect_metrics(target_ip):
    """
    Coleta métricas de latência, perda de pacotes e largura de banda.
    :param target_ip: Endereço IP do destino.
    :return: Dicionário com as métricas coletadas.
    """
    metrics = {
        "latency": get_latency(target_ip),
        "packet_loss": get_packet_loss(target_ip),
        "bandwidth": get_bandwidth(target_ip)
    }
    return metrics
