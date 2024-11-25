import socket
import json

def start_server():
    server_address = ('0.0.0.0', 5000)  # Endereço e porta para UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(server_address)
    print("Servidor UDP à escuta em:", server_address)

    while True:
        data, address = sock.recvfrom(4096)
        message = json.loads(data.decode('utf-8'))
        print(f"Recebido de {address}: {message}")
        # Processa a mensagem recebida (métricas ou confirmação de tarefas)

if __name__ == "__main__":
    start_server()

def start_alert_listener():
    server_address = ('0.0.0.0', 6000)  # Porta para TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(server_address)
    sock.listen(5)
    print("Servidor TCP à escuta para alertas em:", server_address)

    while True:
        connection, client_address = sock.accept()
        try:
            data = connection.recv(1024)
            if data:
                alert = json.loads(data.decode('utf-8'))
                print(f"Alerta recebido: {alert}")
        finally:
            connection.close()

