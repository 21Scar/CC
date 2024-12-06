import socket
import json
import time

# Configuração do agente
SERVER_IP = "10.0.0.1"  # Substitua pelo IP do servidor no teste
SERVER_UDP_PORT = 5005
AGENT_ID = "agent-001"
AGENT_IP = "10.0.0.2"  # Substitua pelo IP do agente

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Mensagem de registro
register_message = {
    "type": "register",
    "agent_id": AGENT_ID,
    "ip": AGENT_IP,
    "status": "active"
}

# Enviar mensagem de registro
sock.sendto(json.dumps(register_message).encode(), (SERVER_IP, SERVER_UDP_PORT))
print(f"Mensagem de registo enviada para o servidor: {register_message}")

# Aguardar resposta do servidor
sock.settimeout(5)
try:
    data, addr = sock.recvfrom(1024)
    response = json.loads(data.decode())
    print(f"Resposta recebida do servidor: {response}")

    if response.get("status") == "success":
        print("Agente registado com sucesso!")

        # Solicitar tarefa ao servidor
        task_request = {"type": "task_request", "agent_id": AGENT_ID}
        sock.sendto(json.dumps(task_request).encode(), (SERVER_IP, SERVER_UDP_PORT))
        print("Pedido de tarefa enviado ao servidor.")

        # Aguardar resposta com tarefas
        data, addr = sock.recvfrom(1024)
        tasks = json.loads(data.decode())
        print(f"Tarefas recebidas do servidor: {tasks}")

except socket.timeout:
    print("Sem resposta do servidor após 5 segundos.")
