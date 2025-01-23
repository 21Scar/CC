import subprocess
import re
import psutil

def get_latency(target_ip):
    """
    Mede a latência (RTT) para um destino usando o comando 'ping'.
    :param target_ip: Endereço IP do destino.
    :return: Latência média em milissegundos (ms) ou None se não for possível calcular.
    """
    try:
        result = subprocess.run(
            ["ping", "-c", "4", target_ip],  # Envia 4 pacotes ICMP
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        output = result.stdout
        # Extrai a latência média a partir do texto da saída do comando
        match = re.search(r"rtt min/avg/max/mdev = [^/]+/([^/]+)/", output)
        if match:
            latency = float(match.group(1))  # Converte o valor extraído para float
            return latency
        else:
            return None  # Retorna None caso a latência não seja encontrada
    except Exception as e:
        print(f"Erro ao medir latência: {e}")  # Imprime erro caso o comando falhe
        return None

def get_packet_loss(target_ip):
    """
    Mede a porcentagem de perda de pacotes para um destino usando 'ping'.
    :param target_ip: Endereço IP do destino.
    :return: Percentual de pacotes perdidos ou 0 se não for possível calcular.
    """
    try:
        result = subprocess.run(
            ["ping", "-c", "4", target_ip],  # Envia 4 pacotes ICMP
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        output = result.stdout
        # Extrai a porcentagem de perda de pacotes usando regex
        match = re.search(r"(\d+)% packet loss", output)
        if match:
            packet_loss = int(match.group(1))  # Converte o valor extraído para inteiro
            return packet_loss
        else:
            return 0  # Retorna 0 se não for possível determinar a perda de pacotes
    except Exception as e:
        print(f"Erro ao medir perda de pacotes: {e}")  # Imprime erro caso o comando falhe
        return 0

def get_bandwidth(target_ip):
    """
    Mede a largura de banda para um destino usando o 'iperf'.
    Certifique-se de que o iperf3 esteja instalado no sistema.
    :param target_ip: Endereço IP do servidor iperf.
    :return: Largura de banda em Mbps ou None se não for possível calcular.
    """
    try:
        result = subprocess.run(
            ["iperf3", "-c", target_ip, "-t", "5"],  # Executa o teste de 5 segundos
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        output = result.stdout
        # Extrai a largura de banda a partir do texto da saída do comando
        match = re.search(r"(\d+\.\d+)\s*Mbits/sec", output)
        if match:
            bandwidth = float(match.group(1))  # Converte o valor extraído para float
            return bandwidth
        else:
            return None  # Retorna None caso a largura de banda não seja encontrada
    except FileNotFoundError:
        print("Erro: 'iperf3' não encontrado. Certifique-se de que está instalado.")  # Mensagem caso o iperf3 não esteja disponível
        return None
    except Exception as e:
        print(f"Erro ao medir largura de banda: {e}")  # Imprime erro caso o comando falhe
        return None
        
def get_cpu_usage():
    """
    Retorna o uso de CPU em porcentagem
    """
    return psutil.cpu_percent(interval=1)
    
def get_ram_usage():
    """
    Retorna o uso de memória RAM em porcentagem
    """
    return psutil.virtual_memory().percent        

def collect_metrics(target_ip):
    """
    Coleta métricas de latência, perda de pacotes e largura de banda para um destino.
    :param target_ip: Endereço IP do destino.
    :return: Dicionário com as métricas coletadas (latência, perda de pacotes e largura de banda).
    """
    metrics = {
        "latency": get_latency(target_ip),         # Mede a latência
        "packet_loss": get_packet_loss(target_ip), # Mede a perda de pacotes
        "bandwidth": get_bandwidth(target_ip),     # Mede a largura de banda
        "cpu_usage": get_cpu_usage(),              # Mede o uso do cpu
        "ram_usage": get_ram_usage()               # Mede o uso de ram
    }
    return metrics  # Retorna as métricas em formato de dicionário
