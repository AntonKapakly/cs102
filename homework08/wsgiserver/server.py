import typing as tp

from httpserver import BaseHTTPRequestHandler, HTTPServer, HTTPResponse, HTTPRequest

from .request import WSGIRequest
from .response import WSGIResponse


class WSGIServer(HTTPServer):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.base_environ: tp.Dict[str, str] = {}
        self.application: tp.Callable = object

    def setup_environ(self):
        self.base_environ["SERVER_NAME"] = "Anton`s server"
        self.base_environ["GATEWAY_INTERFACE"] = "CGI/1.1"
        self.base_environ["SERVER_PORT"] = str(self.port)

    def set_app(self, application: tp.Callable) -> None:
        self.application = application

    def get_app(self) -> tp.Callable:
        return self.application


class WSGIRequestHandler(BaseHTTPRequestHandler):
    request_klass = WSGIRequest
    response_klass = WSGIResponse

    def handle_request(self, request: HTTPRequest) -> HTTPResponse:
        if not isinstance(request, WSGIRequest):
            raise TypeError("You're should give WSGI request for WSGI handler")
        self.server: WSGIServer
        app = self.server.get_app()

        env = self.server.base_environ.copy()
        env.update(request.to_environ(self.server))
        resp = self.response_klass()
        body = app(env, resp.start_response)
        resp.body = "".join(body)
        return resp
