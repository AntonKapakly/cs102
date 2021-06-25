import dataclasses
import typing as tp

from httpserver import HTTPResponse


@dataclasses.dataclass
class WSGIResponse(HTTPResponse):
    status: int = 200

    def make_response(self, status: str, response_headers: tp.List[tp.Tuple[str, str]]) -> None:
        self.status = int(status.split(" ")[0])
        for header, value in response_headers:
            self.headers.update({header: value})
