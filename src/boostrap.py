from network.peer_discovery import BootstrapNode
from network.node import Node

bootstrap_node = BootstrapNode()

def start_bootstrap_server(host, port):
  import socket
  server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server.bind((host, port))
  server.listen(5)
  print(f"Bootstrap node running on {host}:{port} ...")

  while True:
    conn, addr = server.accept()
    data = conn.recv(1024).decode()
    if data.startswith("REGISTER"):
      _, address = data.split()
      peers = bootstrap_node.register_peer(address)
      conn.send(",".join(peers).encode())
    conn.close()


if __name__ == "__main__":
  start_bootstrap_server("127.0.0.1", 8000)
  node = Node("127.0.0.1", 5000)
  node.connect_to_bootstrap("127.0.0.1", 8000)
  node.start()