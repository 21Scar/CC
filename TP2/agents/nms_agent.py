import socket
import json

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

register_message = {
    "type": "register",
    "agent_id": "agent-001",
    "ip": "192.168.1.20",
    "status": "active"
}

sock.sendto(json.dumps(register_message).encode(), (UDP_IP, UDP_PORT))


while True:
    # Recebe mensagens do servidor
    data, addr = sock.recvfrom(1024)
    message = json.loads(data.decode())
    print(f"Tarefa recebida de {addr}: {message}")

    if "sequence" in message:
        # Confirma recebimento com ACK
        ack_message = {
            "type": "ack",
            "ack": message["sequence"],
            "agent_id": "agent-001"
        }
        sock.sendto(json.dumps(ack_message).encode(), addr)
        print(f"ACK enviado para {addr}")


#
# # Aguarda resposta
# data, addr = sock.recvfrom(1024)
# response = json.loads(data.decode())
# print(f"Resposta do servidor: {response}")
