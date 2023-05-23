import socket
import datetime
import http
from socket_hw import HOST, PORT


def http_response(status=200, body=""):
    try:
        http_status = http.HTTPStatus(status)
    except:
        http_status = http.HTTPStatus(200)
        print(f"Unknown Status {status}, Default Status Is Used {http_status}")
    return f"""HTTP/1.0 {http_status.value} {http_status.phrase}
Server: homework
Date: {datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}
Content-Type: text/html; charset=UTF-8

<html><body><pre>{body}</pre></body></html>

    """


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.bind((HOST, PORT))
    sock_ip, sock_port = sock.getsockname()
    print(f'Server Started At {sock_ip}:{sock_port}')
    sock.listen()

    while True:
        client, (client_ip, client_port) = sock.accept()
        with client:
            print(f'Connection From {client_ip}:{client_port}')
            data = ""

            while True:
                data_batch = client.recv(16)
                print(f'Getting Next Batch: {data_batch}')

                if not data_batch:
                    print('EMPTY BATCH')
                    break

                data += data_batch.decode()
                if "\r\n\r\n" in data:
                    print('Sequence Break Found')
                    break

            headers_list = data.splitlines()
            method, target, protocol = headers_list.pop(0).split()
            headers_dict = {}

            for header in headers_list:
                if header:
                    key, value = header.split(':', 1)
                    headers_dict[key.strip()] = value.strip()
            params_dict = {}
            params_url = target.split("?")

            if len(params_url) > 1:
                params_dict = dict(_.split('=') for _ in params_url[1].split('&'))
            headers_str = '\n'.join([f'{" " * 16}-{key:20}: {value}' for key, value in headers_dict.items()])
            params_str = '\n'.join([f'{" " * 16}-{key:20}: {value}' for key, value in params_dict.items()])
            report = f"""
    === Server Data Received ===:
    METHOD: {method}
    TARGET: {target}
    PROTOCOL: {protocol}
    HEADERS: \n{headers_str}
    PARAMETERS: \n{params_str}
    ============================
    """
            print(report)
            status_str = params_dict.get('status', '200')
            try:
                status = int(status_str)

            except:
                status = 200
                print(f'Default Status Is Used{status}. Wrong status {status_str}')

            response = http_response(status=status, body=report)
            client.sendall(response.encode())
