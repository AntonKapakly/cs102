import json
import math
import textwrap
import time
import typing as tp
from string import Template

import pandas as pd
from pandas import json_normalize
from vkapi import session
from vkapi.config import VK_CONFIG
from vkapi.exceptions import APIError


def get_posts_2500(
    owner_id: str = "",
    domain: str = "",
    offset: int = 0,
    count: int = 10,
    max_count: int = 2500,
    filter: str = "owner",
    extended: int = 0,
    fields: tp.Optional[tp.List[str]] = None,
) -> tp.Dict[str, tp.Any]:
    if max_count > 2500:
        max_count = 2500
    if max_count <= 100:
        code = Template(
            """ return API.wall.get({
            "owner_id" : "$owner_id",
            "domain" : "$domain",
            "offset" : "$offset",
            "count" : "$count",
            "filter" : "$filter",
            "extended" : "$extended",
            "fields" : "$fields",
            "v" : "5.126"
        }); """
        )
        code_s = code.substitute(
            max_count=max_count,
            offset=offset,
            owner_id=owner_id,
            domain=domain,
            count=count,
            filter=filter,
            extended=extended,
            fields=fields,
        )
    else:
        code = Template(
            """
            var wall_records = [];
            wall_records = wall_records + API.wall.get({
            "owner_id" : "$owner_id",
            "domain" : "$domain",
            "offset" : $offset,
            "count" : "$count",
            "filter" : "$filter",
            "extended" : "$extended",
            "fields" : "$fields",
            "v" : "5.126"
        });
            var offset = 100 + $offset;
            var count = 100;
            var max_offset = offset + $max_count;
            while (offset < max_offset && wall_records.length <= offset && offset - $offset < $max_count){
                if ($max_count - wall_records.length < 100) {
                count = $max_count - wall_records.length;
                } 
                wall_records = wall_records + API.wall.get({
                    "owner_id" : "$owner_id",
                    "domain" : "$domain",
                    "offset" : offset,
                    "count" : count,
                    "filter" : "$filter",
                    "extended" : "$extended",
                    "fields" : "$fields",
                    "v" : "5.126"
                    });
                offset = offset + 100;
            };
            return wall_records;
            """
        )
        code_s = code.substitute(
            max_count=max_count,
            offset=offset,
            owner_id=owner_id,
            domain=domain,
            count=count,
            filter=filter,
            extended=extended,
            fields=fields,
        )
    access_token = VK_CONFIG["access_token"]
    data = {"code": code_s, "access_token": access_token, "v": VK_CONFIG["version"]}

    response = session.post("execute", data=data).json()["response"]
    if "error" in response:
        raise APIError(response["error"]["error_msg"])
    return response["items"]


def get_wall_execute(
    owner_id: str = "",
    domain: str = "",
    offset: int = 0,
    count: int = 10,
    max_count: int = 2500,
    filter: str = "owner",
    extended: int = 0,
    fields: tp.Optional[tp.List[str]] = None,
    progress=None,
) -> pd.DataFrame:
    """
    Возвращает список записей со стены пользователя или сообщества.
    @see: https://vk.com/dev/wall.get
    :param owner_id: Идентификатор пользователя или сообщества, со стены которого необходимо получить записи.
    :param domain: Короткий адрес пользователя или сообщества.
    :param offset: Смещение, необходимое для выборки определенного подмножества записей.
    :param count: Количество записей, которое необходимо получить (0 - все записи).
    :param max_count: Максимальное число записей, которое может быть получено за один запрос.
    :param filter: Определяет, какие типы записей на стене необходимо получить.
    :param extended: 1 — в ответе будут возвращены дополнительные поля profiles и groups, содержащие информацию о пользователях и сообществах.
    :param fields: Список дополнительных полей для профилей и сообществ, которые необходимо вернуть.
    :param progress: Callback для отображения прогресса.
    """
    posts = pd.DataFrame()
    code = Template(
        """
        return API.wall.get({"owner_id": "$owner_id",
                 "domain": "$domain",
                 "offset": "$offset",
                 "count": "1",
                 "filter": "$filter",
                 "extended": "$extended",
                 "v": "5.126"});
        """
    )
    code_s = code.substitute(
        max_count=max_count,
        offset=offset,
        owner_id=owner_id,
        domain=domain,
        count=count,
        filter=filter,
        extended=extended,
        fields=fields,
    )

    data = {"code": code_s, "access_token": VK_CONFIG["access_token"], "v": VK_CONFIG["version"]}
    response = session.post("execute", data=data).json()
    # fmt: off
    max_requests = math.ceil(count / max_count if count != 0 else response["response"]["count"] / max_count)
    # fmt: on
    if "error" in response:
        raise APIError(response["error"]["error_msg"])
    if progress is None:
        progress = lambda x: x
    for n in progress(range(max_requests)):
        posts = posts.append(
            json_normalize(
                get_posts_2500(
                    owner_id,
                    domain,
                    offset + n * max_count,
                    count,
                    max_count,
                    filter,
                    extended,
                    fields,
                )
            )
        )
        time.sleep(1)
    return posts
