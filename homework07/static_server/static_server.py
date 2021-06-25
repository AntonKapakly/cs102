import logging
import mimetypes
import os
import pathlib
from email.utils import formatdate
from urllib.parse import urlparse, unquote

from httpserver import BaseHTTPRequestHandler, HTTPResponse, HTTPServer


def url_normalize(path: str) -> str:
    if path.startswith("."):
        path = "/" + path
    while "../" in path:
        p1 = path.find("/..")
        p2 = path.rfind("/", 0, p1)
        if p2 != -1:
            path = path[:p2] + path[p1 + 3 :]
        else:
            path = path.replace("/..", "", 1)
            path = path.replace("/./", "/")
            path = path.replace("/.", "")
    return path


class StaticHTTPRequestHandler(BaseHTTPRequestHandler):
    def _head(self) -> HTTPResponse:

        _url = urlparse(self._url.decode())
        self.path, qs = _url.path, _url.query
        self.path = url_normalize(unquote(self.path))
        self.path = self.path.strip("/")

        self.path = os.path.join(self.server.document_root, *os.path.split(self.path))

        if os.path.isdir(self.path):
            self.path += "index.html"

        if not os.path.exists(self.path):
            raise FileNotFoundError(self.path)

        content_type, _ = mimetypes.guess_type(self.path)
        content_size = os.path.getsize(self.path)

        return self.response_klass(
            status=200,
            headers={
                "Server": "server",
                "Date": formatdate(timeval=None, localtime=False, usegmt=True),
                "Content-Type": str(content_type),
                "Content-Length": str(content_size),
                "Connection": "Closed",
            },
        )

    def do_GET(self):
        try:
            response = self._head()
        except FileNotFoundError as e:
            logging.error(e)
            return self.response_klass(status=404, headers={})
        else:
            with open(self.path, "rb") as f:
                response.body += f.read()
            return response

    def do_HEAD(self):
        try:
            return self._head()
        except FileNotFoundError as e:
            logging.error(e)
            return self.response_klass(status=404, headers={})


class StaticServer(HTTPServer):
    def __init__(self, document_root: pathlib.Path, *args, **kwargs):
        super(StaticServer, self).__init__(*args, **kwargs)
        self.document_root = document_root


if __name__ == "__main__":
    document_root = pathlib.Path("static") / "root"
    server = StaticServer(
        timeout=60,
        document_root=document_root,
        port=5000,
        request_handler_cls=StaticHTTPRequestHandler,
    )
    server.serve_forever()
