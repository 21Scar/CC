import socket
import json

# Configuração inicial do servidor
UDP_IP = "127.0.0.1"
UDP_PORT = 5005

# Inicializa o socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

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


# Caminho para o ficheiro JSON com tarefas
TASKS_FILE = "tasks.json"

# Carregar e interpretar as tarefas
tasks = parse_tasks(TASKS_FILE)
if tasks:
    print(f"Tarefas carregadas: {tasks}")
else:
    print("Erro ao carregar tarefas.")

# Registro de agentes e tarefas pendentes
agents = {}  # {agent_id: (IP, porta)}
pending_tasks = {}  # {agent_id: [tarefas]}

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
            print(f"Agente registrado: {agent_id} em {addr}")

            # Atribuir tarefas ao agente
            if tasks:
                agent_tasks = [task for task in tasks if any(d["device_id"] == agent_id for d in task["devices"])]
                pending_tasks[agent_id] = agent_tasks
                print(f"Tarefas atribuídas ao agente {agent_id}: {agent_tasks}")
            else:
                pending_tasks[agent_id] = []

            # Envia confirmação de registo ao agente
            response = {"status": "success", "message": "Agent registered"}
            sock.sendto(json.dumps(response).encode(), addr)

        elif message.get("type") == "task_request":
            # Envia as tarefas pendentes ao agente
            agent_id = message["agent_id"]
            if agent_id in pending_tasks and pending_tasks[agent_id]:
                task = pending_tasks[agent_id].pop(0)  # Remove e envia a próxima tarefa
                task_message = {"type": "task", "task": task}
                sock.sendto(json.dumps(task_message).encode(), agents[agent_id])
                print(f"Tarefa enviada para o agente {agent_id}: {task}")
            else:
                print(f"Sem tarefas pendentes para o agente {agent_id}.")

    except json.JSONDecodeError:
        print("Mensagem recebida não é um JSON válido.")
