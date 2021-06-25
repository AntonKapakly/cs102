from __future__ import annotations

import logging
import select
import socket
import typing as tp

import requests
from httptools import HttpRequestParser

from .request import HTTPRequest
from .response import HTTPResponse

if tp.TYPE_CHECKING:
    from .server import TCPServer

Address = tp.Tuple[str, int]


class BaseRequestHandler:
    def __init__(self, socket: socket.socket, address: Address, server: TCPServer) -> None:
        self.socket = socket
        self.address = address
        self.server = server

    def handle(self) -> None:
        self.close()

    def close(self) -> None:
        self.socket.close()


class EchoRequestHandler(BaseRequestHandler):
    def handle(self) -> None:
        try:
            data = self.socket.recv(1024)
        except (socket.timeout, BlockingIOError):
            pass
        else:
            self.socket.sendall(data)
        finally:
            self.close()


class BaseHTTPRequestHandler(BaseRequestHandler):
    request_klass = HTTPRequest
    response_klass = HTTPResponse

    def __init__(self, *args: tp.Any, **kwargs: tp.Any) -> None:
        super().__init__(*args, **kwargs)
        self.parser = HttpRequestParser(self)

        self._url: bytes = b""
        self._headers: tp.Dict[bytes, bytes] = {}
        self._body: bytes = b""
        self._parsed = False

    def handle(self) -> None:
        request = self.parse_request()
        if request:
            try:
                response = self.handle_request(request)
            except requests.exceptions.ConnectionError:
                logging.error("Something went wrong with connection")
                response = self.response_klass(status=500, headers={}, body=b"")
            except Exception as e:
                logging.exception("Invalid request", e)
                response = self.response_klass(status=500, headers={}, body=b"")
        else:
            response = self.response_klass(status=400, headers={}, body=b"")
        self.handle_response(response)
        self.close()

    def parse_request(self) -> tp.Optional[HTTPRequest]:
        while True:
            data = self.socket.recv(1024)
            if not data or data == b"":
                break
            self.parser.feed_data(data)
        if self._parsed:
            return self.request_klass(
                self.parser.get_method(), self._url, self._headers, self._body
            )
        return None

    def handle_request(self, request: HTTPRequest) -> tp.Union[tp.Any, HTTPResponse]:
        method = f"do_{request.method.decode()}"
        if hasattr(self, method):
            return getattr(self, method)()
        else:
            return self.response_klass(
                status=405,
                headers={"Allow": ", ".join([s[3:] for s in dir(self) if s.startswith("do_")])},
            )

    def handle_response(self, response: HTTPResponse) -> None:
        self.socket.sendall(response.to_http1())

    def on_url(self, url: bytes) -> None:
        self._url = url

    def on_header(self, name: bytes, value: bytes) -> None:
        self._headers[name] = value

    def on_body(self, body: bytes) -> None:
        self._body = body

    def on_message_complete(self) -> None:
        self._parsed = True
