import socket
import json
import threading

# Configuração inicial do servidor
UDP_IP = "0.0.0.0"  # Escuta em todas as interfaces para permitir flexibilidade no teste
UDP_PORT = 5005      # Porta UDP para NetTask
TCP_PORT = 6000      # Porta TCP para AlertFlow

# Inicializa o socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

# Inicializa o socket TCP
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.bind((UDP_IP, TCP_PORT))
tcp_sock.listen(5)

# Registro de agentes e métricas
agents = {}  # {agent_id: (IP, porta)}
tasks = []   # Lista de tarefas carregadas do ficheiro
metrics_data = {}  # {agent_id: [resultados]}

# Função para lidar com conexões TCP para alertas
def handle_alerts():
    print("Servidor TCP para alertas iniciado, aguardando conexões...")
    while True:
        conn, addr = tcp_sock.accept()
        print(f"Conexão TCP recebida de {addr}")
        data = conn.recv(1024)
        if data:
            try:
                alert = json.loads(data.decode())
                print(f"Alerta recebido: {alert}")
            except json.JSONDecodeError:
                print("Mensagem TCP recebida não é um JSON válido.")
        conn.close()

# Carregar tarefas do ficheiro
def load_tasks(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Erro ao carregar tarefas: {e}")
        return []

# Thread para tratar alertas TCP
tcp_thread = threading.Thread(target=handle_alerts, daemon=True)
tcp_thread.start()

# Carregar tarefas
tasks = load_tasks("tasks.json")
print(f"Tarefas carregadas: {tasks}")

print("Servidor UDP iniciado, aguardando dados...")

# Loop principal do servidor
while True:
    try:
        data, addr = sock.recvfrom(1024)
        print(f"Recebido de {addr}: {data.decode()}")

        try:
            message = json.loads(data.decode())

            if message.get("type") == "register":
                # Registra o agente
                agent_id = message["agent_id"]
                agents[agent_id] = addr
                print(f"Agente registado: {agent_id} em {addr}")

                # Envia resposta de confirmação
                response = {"status": "success", "message": "Agent registered"}
                sock.sendto(json.dumps(response).encode(), addr)

            elif message.get("type") == "task_request":
                # Envia as tarefas atribuídas ao agente
                agent_id = message["agent_id"]
                if agent_id in agents:
                    agent_tasks = [
                        task for task in tasks if any(d["device_id"] == agent_id for d in task["devices"])
                    ]
                    response = {"type": "task", "tasks": agent_tasks}
                    sock.sendto(json.dumps(response).encode(), addr)
                    print(f"Tarefas enviadas ao agente {agent_id}: {agent_tasks}")
                else:
                    print(f"Agente {agent_id} não registado.")

        except json.JSONDecodeError:
            print("Mensagem recebida não é um JSON válido.")

    except KeyboardInterrupt:
        print("\nServidor interrompido pelo utilizador.")
        break
