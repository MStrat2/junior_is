import sys
import socket
import threading

# Hexdump function
def hexdump(src, length=16):
    result = []
    for i in range(0, len(src), length):
        s = src[i:i+length]
        hexa = ' '.join([f'{b:02x}' for b in s])
        printable = ''.join([chr(b) if 32 <= b < 127 else '.' for b in s])
        result.append(f'{i:04x}  {hexa:<{length*3}}  {printable}')
    return '\n'.join(result)

#reads data from a socket connection
def receive_from(connection):
    buffer = b''
    connection.settimeout(2)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except:
        pass
    return buffer

# Handles the proxying of data between client and remote server
def proxy_handler(client_socket, remote_host, remote_port):
    # Connect to remote server
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))
    
    print(f"[*] Connected to {remote_host}:{remote_port}")
    
    while True:
        # Receive from client
        client_data = receive_from(client_socket)
        if client_data:
            print(f"\n[==>] Received {len(client_data)} bytes from client")
            print(hexdump(client_data))
            remote_socket.send(client_data)
        
        # Receive from remote
        remote_data = receive_from(remote_socket)
        if remote_data:
            print(f"\n[<==] Received {len(remote_data)} bytes from remote")
            print(hexdump(remote_data))
            client_socket.send(remote_data)
        
        if not client_data and not remote_data:
            break
    
    client_socket.close()
    remote_socket.close()

# Creates a listening socket
def server_loop(local_port, remote_host, remote_port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', local_port))
    server.listen(5)
    print(f"[*] Listening on 0.0.0.0:{local_port}")
    
    while True:
        client_socket, addr = server.accept()
        print(f"[*] Got connection from {addr[0]}:{addr[1]}")
        proxy_thread = threading.Thread(
            target=proxy_handler,
            args=(client_socket, remote_host, remote_port)
        )
        proxy_thread.start()

#Opens port 9000 and forwards to destination. 
if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python proxy.py [local_port] [remote_host] [remote_port]")
        print("Example: python proxy.py 9000 127.0.0.1 5555")
        sys.exit(1)
    
    local_port = int(sys.argv[1])
    remote_host = sys.argv[2]
    remote_port = int(sys.argv[3])
    
    server_loop(local_port, remote_host, remote_port)