import socket
import json
import time
from metrics import collect_metrics  # Funções para coleta de métricas

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Registra o agente no servidor
register_message = {
    "type": "register",
    "agent_id": "agent-001",
    "ip": "192.168.1.20",
    "status": "active"
}
sock.sendto(json.dumps(register_message).encode(), (UDP_IP, UDP_PORT))
print(f"Mensagem de registo enviada para o servidor: {register_message}")

# Definir um timeout de 5 segundos para não ficar bloqueado
sock.settimeout(5)

try:
    # Receber a resposta de registo do servidor
    data, addr = sock.recvfrom(1024)
    response = json.loads(data.decode())
    print(f"Resposta recebida do servidor: {response}")

    if response.get("status") == "success":
        print("Agente registrado com sucesso!")

        # Solicitar tarefa ao servidor
        task_request = {"type": "task_request", "agent_id": "agent-001"}
        sock.sendto(json.dumps(task_request).encode(), (UDP_IP, UDP_PORT))
        print("Pedido de tarefa enviado ao servidor.")

        # Receber a tarefa do servidor
        data, addr = sock.recvfrom(1024)
        task_message = json.loads(data.decode())
        print(f"Tarefa recebida: {task_message}")

        # Executar as métricas especificadas na tarefa
        task = task_message["task"]
        for device in task["devices"]:
            if device["device_id"] == "agent-001":
                frequency = task["frequency"]
                while True:
                    metrics = collect_metrics(device["link_metrics"]["latency"]["destination"])
                    results_message = {
                        "type": "metrics",
                        "agent_id": "agent-001",
                        "metrics": metrics
                    }
                    sock.sendto(json.dumps(results_message).encode(), (UDP_IP, UDP_PORT))
                    print(f"Métricas enviadas para o servidor: {metrics}")
                    time.sleep(frequency)

except socket.timeout:
    print("Sem resposta do servidor após 5 segundos.")
