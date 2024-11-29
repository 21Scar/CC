import socket
import json
import threading
import time

# Configuração inicial do servidor
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
TCP_PORT = 6000

# Inicializa o socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

# Inicializa o socket TCP
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.bind((UDP_IP, TCP_PORT))
tcp_sock.listen(5)

# Dicionário para armazenar métricas dos agentes
metrics_data = {}  # {agent_id: [metrics]}
agents = {}  # {agent_id: (IP, porta)}

# Função para carregar e interpretar tarefas
def parse_tasks(file_path):
    """
    Lê e interpreta o ficheiro JSON contendo as tarefas.
    :param file_path: Caminho do ficheiro JSON.
    :return: Lista de tarefas (ou levanta erro se inválido).
    """
    try:
        with open(file_path, 'r') as file:
            tasks = json.load(file)

        # Valida a estrutura das tarefas
        for task in tasks:
            if "task_id" not in task or "frequency" not in task or "devices" not in task:
                raise ValueError(f"Tarefa inválida: {task}")
            for device in task["devices"]:
                if "device_id" not in device or "device_metrics" not in device or "link_metrics" not in device:
                    raise ValueError(f"Dispositivo inválido na tarefa {task['task_id']}: {device}")

        return tasks
    except FileNotFoundError:
        print(f"Erro: Ficheiro {file_path} não encontrado.")
        return None
    except json.JSONDecodeError as e:
        print(f"Erro ao interpretar o JSON: {e}")
        return None
    except ValueError as e:
        print(f"Erro de validação: {e}")
        return None

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
                # Aqui você pode armazenar ou processar o alerta conforme necessário
            except json.JSONDecodeError:
                print("Mensagem TCP recebida não é um JSON válido.")
        conn.close()

# Caminho para o ficheiro JSON com tarefas
TASKS_FILE = "tasks.json"

# Carregar e interpretar as tarefas
tasks = parse_tasks(TASKS_FILE)
if tasks:
    print(f"Tarefas carregadas: {tasks}")
else:
    print("Erro ao carregar tarefas.")

# Função para mostrar as métricas armazenadas
def show_metrics():
    print("\n--- Métricas Armazenadas ---")
    for agent_id, metrics_list in metrics_data.items():
        print(f"Agente: {agent_id}")
        for metrics in metrics_list:
            print(f"  {metrics}")
    print("\n----------------------------")

# Inicia a thread para lidar com conexões TCP (alertas)
tcp_thread = threading.Thread(target=handle_alerts, daemon=True)
tcp_thread.start()

print("Servidor UDP iniciado, aguardando dados...")

# Loop principal do servidor
while True:
    data, addr = sock.recvfrom(1024)
    print(f"Recebido de {addr}: {data.decode()}")

    try:
        message = json.loads(data.decode())

        if message.get("type") == "register":
            # Regista o agente
            agent_id = message["agent_id"]
            agents[agent_id] = addr
            print(f"Agente registado: {agent_id} em {addr}")

            # Atribuir tarefas ao agente
            if tasks:
                agent_tasks = [task for task in tasks if any(d["device_id"] == agent_id for d in task["devices"])]
                print(f"Tarefas atribuídas ao agente {agent_id}: {agent_tasks}")
            else:
                print(f"Sem tarefas atribuídas para o agente {agent_id}.")

            # Envia confirmação de registo ao agente
            response = {"status": "success", "message": "Agent registered"}
            sock.sendto(json.dumps(response).encode(), addr)

        elif message.get("type") == "task_request":
            # Envia as tarefas pendentes ao agente
            agent_id = message["agent_id"]
            if agent_id in agents:
                # Enviar tarefa aqui...
                pass

        elif message.get("type") == "metrics":
            # Recebe os resultados das métricas
            agent_id = message["agent_id"]
            results = message["metrics"]
            if agent_id not in metrics_data:
                metrics_data[agent_id] = []
            metrics_data[agent_id].append(results)
            print(f"Métricas recebidas do agente {agent_id}: {results}")

            # Mostrar métricas armazenadas a cada novo conjunto de métricas recebidas
            show_metrics()

    except json.JSONDecodeError:
        print("Mensagem recebida não é um JSON válido.")
