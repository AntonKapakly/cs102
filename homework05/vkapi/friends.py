import dataclasses
import math
import time
import typing as tp

import requests
from tqdm import tqdm
from vkapi import session
from vkapi.config import VK_CONFIG
from vkapi.exceptions import APIError

QueryParams = tp.Optional[tp.Dict[str, tp.Union[str, int]]]


@dataclasses.dataclass(frozen=True)
class FriendsResponse:
    count: int
    items: tp.Union[tp.List[int], tp.List[tp.Dict[str, tp.Any]]]


def get_friends(
    user_id: int,
    count: int = 5000,
    offset: int = 0,
    fields: tp.Optional[tp.List[str]] = None,  # type:ignore
) -> FriendsResponse:
    """
    Получить список идентификаторов друзей пользователя или расширенную информацию
    о друзьях пользователя (при использовании параметра fields).

    :param user_id: Идентификатор пользователя, список друзей для которого нужно получить.
    :param count: Количество друзей, которое нужно вернуть.
    :param offset: Смещение, необходимое для выборки определенного подмножества друзей.
    :param fields: Список полей, которые нужно получить для каждого пользователя.
    :return: Список идентификаторов друзей пользователя или список пользователей.
    """
    params = {
        "user_id": user_id if user_id is not None else "",
        "count": count,
        "offset": offset,
        "fields": ",".join(fields) if fields is not None else "",
    }
    res = session.get("friends.get", params=params)
    if "error" in res.json():
        raise APIError(res.json()["error"]["error_msg"])
    return FriendsResponse(**res.json()["response"])


class MutualFriends(tp.TypedDict):
    id: int
    common_friends: tp.List[int]
    common_count: int


def get_mutual(
    source_uid: tp.Optional[int] = None,
    target_uid: tp.Optional[int] = None,
    target_uids: tp.Optional[tp.List[int]] = None,
    order: str = "",
    count: tp.Optional[int] = None,
    offset: int = 0,
    progress=None,
) -> tp.Union[tp.List[int], tp.List[MutualFriends]]:
    """
    Получить список идентификаторов общих друзей между парой пользователей.

    :param source_uid: Идентификатор пользователя, чьи друзья пересекаются с друзьями пользователя с идентификатором target_uid.
    :param target_uid: Идентификатор пользователя, с которым необходимо искать общих друзей.
    :param target_uids: Cписок идентификаторов пользователей, с которыми необходимо искать общих друзей.
    :param order: Порядок, в котором нужно вернуть список общих друзей.
    :param count: Количество общих друзей, которое нужно вернуть.
    :param offset: Смещение, необходимое для выборки определенного подмножества общих друзей.
    :param progress: Callback для отображения прогресса.
    """
    if target_uids is None:
        if target_uid is None:
            raise Exception
        target_uids = [target_uid]

    responses = []

    if progress is None:
        progress = lambda x: x
    prog = progress(range(math.ceil(len(target_uids) / 100)))
    for p in prog:
        params = {
            "target_uid": target_uid if target_uid is not None else "",
            "source_uid": source_uid if source_uid is not None else "",
            "target_uids": ", ".join(map(str, target_uids)),
            "order": order,
            "count": count if count is not None else "",
            "offset": offset,
        }
        response = session.get(f"friends.getMutual", params=params)
        if "error" in response.json():
            raise APIError(response.json()["error"]["error_msg"])
        offset += 100

        if isinstance(response.json()["response"], list):
            responses.extend(response.json()["response"])
        else:
            responses.append(
                MutualFriends(
                    id=response.json()["response"]["id"],
                    common_friends=response.json()["response"]["common_friends"],
                    common_count=response.json()["response"]["common_count"],
                )
            )
        time.sleep(1)
    return responses
