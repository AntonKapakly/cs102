import dataclasses
import typing as tp
from http import HTTPStatus


@dataclasses.dataclass
class HTTPResponse:
    status: int
    headers: tp.Dict[str, str] = dataclasses.field(default_factory=dict)
    body: bytes = b""

    def to_http1(self) -> bytes:
        headers = "\n".join([f"{k}: {v}" for k, v in self.headers.items()])
        headers = f"HTTP/1.1 {self.status} {HTTPStatus(self.status).phrase}\r\n{headers}\n\n"
        return headers.encode() + self.body + b"\r\n"
