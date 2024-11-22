import socket
import json

# Configuração inicial do servidor
UDP_IP = "127.0.0.1"  # Localhost
UDP_PORT = 5005       # Porta de comunicação

# Inicializa o socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print("Servidor UDP iniciado, aguardando dados...")

while True:
    # Recebe mensagem dos agentes
    data, addr = sock.recvfrom(1024)
    print(f"Recebido de {addr}: {data.decode()}")
    
    # Exemplo: Parse de uma mensagem JSON
    try:
        message = json.loads(data.decode())
        print("Mensagem interpretada:", message)
    except json.JSONDecodeError:
        print("Mensagem recebida não é um JSON válido.")


# Para testar o servidor, execute o script e envie uma mensagem de alerta de um agente:
# $ python3 nms_server.py
# Servidor UDP iniciado, aguardando dados...
# Recebido de ('
#
#
#
#
#
#
#

# ', 5005): b'{\n  "type": "alert",\n  "agent_id": "agent-001",\n  "metric": "cpu_usage",\n  "value": 85,\n  "threshold": 80,\n  "timestamp": "2024-11-16T12:00:00Z"\n}\n'
# Mensagem interpretada: {'type': 'alert', 'agent_id': 'agent-001', 'metric': 'cpu_usage', 'value': 85, 'threshold': 80, 'timestamp': '2024-11-16T12:00:00Z'}
# Recebido de ('
#   
#
#
#
#

# ', 5005): b'{\n  "type": "alert",\n  "agent_id": "agent-002",\n  "metric": "memory_usage",\n  "value": 95,\n  "threshold": 90,\n  "timestamp": "2024-11-16T12:00:00Z"\n}\n'
# Mensagem interpretada: {'type': 'alert', 'agent_id': 'agent-002', 'metric': 'memory_usage', 'value': 95, 'threshold': 90, 'timestamp': '2024-11-16T12:00:00Z'}
# Recebido de ('
#
#
#
#
#
#
#   
#

# ', 5005): b'{\n  "type": "alert",\n  "agent_id": "agent-003",\n  "metric": "disk_usage",\n  "value": 75,\n  "threshold": 70,\n  "timestamp": "2024-11-16T12:00:00Z"\n}\n'
# Mensagem interpretada: {'type': 'alert', 'agent_id': 'agent-003', 'metric': 'disk_usage', 'value': 75, 'threshold': 70, 'timestamp': '2024-11-16T12:00:00Z'}
# Recebido de ('
