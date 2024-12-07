import socket
import json
import time
from metrics import collect_metrics  # Funções para coleta de métricas

# Configurações do servidor (IP e portas para UDP e TCP)
UDP_IP = "127.0.0.1"  # Endereço IP do servidor
UDP_PORT = 5005       # Porta UDP para comunicação
TCP_PORT = 6000       # Porta TCP para envio de alertas

# Inicializa o socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Mensagem para registrar o agente no servidor
register_message = {
    "type": "register",          # Tipo da mensagem
    "agent_id": "agent-001",     # ID único do agente
    "ip": "192.168.1.20",        # Endereço IP do agente
    "status": "active"           # Status inicial do agente
}

# Envia a mensagem de registro para o servidor
sock.sendto(json.dumps(register_message).encode(), (UDP_IP, UDP_PORT))
print(f"Mensagem de registo enviada para o servidor: {register_message}")

# Função para enviar alertas ao servidor via TCP
def send_alert(alert_data):
    """
    Envia alertas para o servidor utilizando conexão TCP.
    :param alert_data: Dicionário contendo os dados do alerta.
    """
    try:
        with socket.create_connection((UDP_IP, TCP_PORT)) as tcp_sock:
            tcp_sock.sendall(json.dumps(alert_data).encode())
            print(f"Alerta enviado: {alert_data}")
    except Exception as e:
        print(f"Erro ao enviar alerta: {e}")

# Define um timeout para evitar bloqueio em caso de falha de resposta
sock.settimeout(5)

try:
    # Aguarda a resposta de registro do servidor
    data, addr = sock.recvfrom(1024)
    response = json.loads(data.decode())
    print(f"Resposta recebida do servidor: {response}")

    if response.get("status") == "success":
        print("Agente registado com sucesso!")

        # Solicita a tarefa ao servidor
        task_request = {"type": "task_request", "agent_id": "agent-001"}
        sock.sendto(json.dumps(task_request).encode(), (UDP_IP, UDP_PORT))
        print("Pedido de tarefa enviado ao servidor.")

        # Recebe a tarefa enviada pelo servidor
        data, addr = sock.recvfrom(1024)
        task_message = json.loads(data.decode())
        print(f"Tarefa recebida: {task_message}")

        # Executa as tarefas recebidas
        if isinstance(task_message, list):
            for task in task_message:
                task_id = task["task_id"]        # Identificador da tarefa
                frequency = task["frequency"]   # Frequência de execução

                # Itera sobre os dispositivos definidos na tarefa
                for device in task["devices"]:
                    if device["device_id"] == "agent-001":  # Verifica se o dispositivo é este agente
                        while True:
                            # Coleta métricas do dispositivo
                            destination = device["link_metrics"]["latency"]["destination"]
                            metrics = collect_metrics(destination)

                            # Verifica a disponibilidade das métricas coletadas
                            if metrics["latency"] is None:
                                print("Aviso: Métrica de latência não disponível.")
                            if metrics["bandwidth"] is None:
                                print("Aviso: Métrica de largura de banda não disponível.")

                            # Envia as métricas coletadas para o servidor
                            results_message = {
                                "type": "metrics",
                                "agent_id": "agent-001",
                                "task_id": task_id,
                                "metrics": metrics
                            }
                            sock.sendto(json.dumps(results_message).encode(), (UDP_IP, UDP_PORT))
                            print(f"Métricas enviadas para o servidor: {metrics}")

                            # Verifica se alguma métrica excede os limites definidos para alertas
                            conditions = device["alertflow_conditions"]

                            if metrics["latency"] is not None and metrics["latency"] > conditions["cpu_usage"]:
                                alert = {
                                    "type": "alert",
                                    "agent_id": "agent-001",
                                    "metric": "latency",
                                    "value": metrics["latency"],
                                    "threshold": conditions["cpu_usage"]
                                }
                                send_alert(alert)

                            # Aguarda o intervalo definido antes de repetir a coleta
                            time.sleep(frequency)
        else:
            print("Erro: A tarefa recebida não está no formato esperado.")

except socket.timeout:
    print("Sem resposta do servidor após 5 segundos.")
