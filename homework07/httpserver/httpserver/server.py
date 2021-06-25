import socket
import logging
import typing as tp
from concurrent.futures import ThreadPoolExecutor, Future

from .handlers import BaseRequestHandler


class TCPServer:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5000,
        backlog_size: int = 1,
        max_workers: int = 1,
        timeout: tp.Optional[float] = None,
        request_handler_cls: tp.Type[BaseRequestHandler] = BaseRequestHandler,
    ) -> None:
        self.host = host
        self.port = port
        self.server_address = (host, port)
        self.backlog_size = backlog_size
        self.request_handler_cls = request_handler_cls
        self.max_workers = max_workers
        self.timeout = timeout
        self._threads: tp.List[Future[None]] = []

    def serve_forever(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            try:
                sock.bind(self.server_address)
                sock.listen(self.backlog_size)
                while True:
                    client_sock, _ = sock.accept()
                    client_sock.settimeout(self.timeout)
                    self._threads.append(executor.submit(self.handle_accept, client_sock))
            except KeyboardInterrupt:
                pass
            except OSError as e:
                logging.error(e)
            finally:
                sock.close()

    def handle_accept(self, server_socket: socket.socket) -> None:
        handler = self.request_handler_cls(server_socket, self.server_address, self)
        handler.handle()


class HTTPServer(TCPServer):
    pass
