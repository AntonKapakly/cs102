import dataclasses
import io
import typing as tp
import urllib.parse

from httpserver import HTTPRequest, HTTPServer


@dataclasses.dataclass
class WSGIRequest(HTTPRequest):
    def to_environ(self, server: HTTPServer) -> tp.Dict[str, tp.Any]:

        if "?" in self.url:
            path, query = self.url.split("?", 1)
        else:
            path, query = self.url, ""

        environ = {
            "REQUEST_METHOD": self.method,
            "SCRIPT_NAME": "",
            "CONTENT_TYPE": self.headers.get("content-type", ""),
            "CONTENT_LENGTH": self.headers.get("content-length", len(self.body)),
            "SERVER_NAME": server.host,
            "SERVER_PORT": server.port,
            "PATH_INFO": urllib.parse.unquote(path, "iso-8859-1"),
            "QUERY_STRING": query,
            "SERVER_PROTOCOL": "HTTP/1.0",
            "HTTP_Variables": self.headers,
            "wsgi.version": (1, 0),
            "wsgi.url_scheme": self.url.split("://")[0],
            "wsgi.input": io.StringIO(self.body),
            "wsgi.errors": io.StringIO(),
            "wsgi.multithread": True,
            "wsgi.multiprocess": True,
            "wsgi.run_once": False,
        }
        return environ
