import socket
import json
import time
from metrics import collect_metrics  # Funções para coleta de métricas

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
TCP_PORT = 6000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Regista o agente no servidor
register_message = {
    "type": "register",
    "agent_id": "agent-001",
    "ip": "192.168.1.20",
    "status": "active"
}
sock.sendto(json.dumps(register_message).encode(), (UDP_IP, UDP_PORT))
print(f"Mensagem de registo enviada para o servidor: {register_message}")

# Função para enviar alertas via TCP
def send_alert(alert_data):
    try:
        with socket.create_connection((UDP_IP, TCP_PORT)) as tcp_sock:
            tcp_sock.sendall(json.dumps(alert_data).encode())
            print(f"Alerta enviado: {alert_data}")
    except Exception as e:
        print(f"Erro ao enviar alerta: {e}")

# Definir um timeout de 5 segundos para não ficar bloqueado
sock.settimeout(5)

try:
    # Receber a resposta de registo do servidor
    data, addr = sock.recvfrom(1024)
    response = json.loads(data.decode())
    print(f"Resposta recebida do servidor: {response}")

    if response.get("status") == "success":
        print("Agente registado com sucesso!")

        # Solicitar tarefa ao servidor
        task_request = {"type": "task_request", "agent_id": "agent-001"}
        sock.sendto(json.dumps(task_request).encode(), (UDP_IP, UDP_PORT))
        print("Pedido de tarefa enviado ao servidor.")

        # Receber a tarefa do servidor
        data, addr = sock.recvfrom(1024)
        task_message = json.loads(data.decode())
        print(f"Tarefa recebida: {task_message}")

        # Executar as métricas especificadas na tarefa

        if isinstance(task_message, list):
            for task in task_message:
                task_id = task["task_id"]
                frequency = task["frequency"]

                # Iterar sobre os dispositivos da tarefa
                for device in task["devices"]:
                    if device["device_id"] == "agent-001":
                        while True:
                            # Coletar métricas para o dispositivo especificado
                            destination = device["link_metrics"]["latency"]["destination"]
                            metrics = collect_metrics(destination)

                            # Validar resultados das métricas
                            if metrics["latency"] is None:
                                print("Aviso: Métrica de latência não disponível.")
                            if metrics["bandwidth"] is None:
                                print("Aviso: Métrica de largura de banda não disponível.")

                            # Enviar resultados das métricas via UDP
                            results_message = {
                                "type": "metrics",
                                "agent_id": "agent-001",
                                "task_id": task_id,
                                "metrics": metrics
                            }
                            sock.sendto(json.dumps(results_message).encode(), (UDP_IP, UDP_PORT))
                            print(f"Métricas enviadas para o servidor: {metrics}")

                            # Verificar condições de alerta
                            conditions = device["alertflow_conditions"]

                            # Processar alertas apenas para métricas válidas
                            if metrics["latency"] is not None and metrics["latency"] > conditions["cpu_usage"]:
                                alert = {
                                    "type": "alert",
                                    "agent_id": "agent-001",
                                    "metric": "latency",
                                    "value": metrics["latency"],
                                    "threshold": conditions["cpu_usage"]
                                }
                                send_alert(alert)

                            time.sleep(frequency)
        else:
            print("Erro: A tarefa recebida não está no formato esperado.")

except socket.timeout:
    print("Sem resposta do servidor após 5 segundos.")
