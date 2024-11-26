import socket
import json

def send_metrics(server_ip):
    metrics = {
        "agent_id": "agent-001",
        "metrics": {
            "latency": 20,
            "packet_loss": 2
        }
    }
    message = json.dumps(metrics).encode('utf-8')
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message, (server_ip, 5000))

def receive_task():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', 5001))
    while True:
        data, address = sock.recvfrom(4096)
        task = json.loads(data.decode('utf-8'))
        print(f"Tarefa recebida: {task}")

        # Executa a tarefa recebida 


def send_alert(server_ip, alert_data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_ip, 6000))
    alert_message = json.dumps(alert_data).encode('utf-8')
    sock.sendall(alert_message)
    sock.close()

    #por causa das metrics.py
    from metrics import collect_metrics

def send_metrics(server_ip):
    metrics = collect_metrics("10.0.4.10")  # Substitui pelo IP do destino
    payload = {
        "agent_id": "agent-001",
        "metrics": metrics
    }
    message = json.dumps(payload).encode('utf-8')
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message, (server_ip, 5000))

