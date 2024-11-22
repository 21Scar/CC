import socket
import json

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

message = {
    "type": "register",
    "agent_id": "agent-001",
    "ip": "192.168.1.20",
    "status": "active"
}

sock.sendto(json.dumps(message).encode(), (UDP_IP, UDP_PORT))

# Aguarda resposta
data, addr = sock.recvfrom(1024)
response = json.loads(data.decode())
print(f"Resposta do servidor: {response}")
