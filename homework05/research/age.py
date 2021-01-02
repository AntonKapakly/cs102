import datetime as dt
import typing as tp
from datetime import datetime
from statistics import median

from vkapi.friends import get_friends


def age_predict(user_id: int) -> tp.Optional[float]:
    """
    Наивный прогноз возраста пользователя по возрасту его друзей.

    Возраст считается как медиана среди возраста всех друзей пользователя

    :param user_id: Идентификатор пользователя.
    :return: Медианный возраст пользователя.
    """
    lists = get_friends(user_id, fields="bdate").items  # type:ignore
    mas = []
    c = 0
    current_date = datetime.now().date().year
    for dicts in lists:
        if "bdate" in dicts.keys():  # type:ignore
            b_year = dicts["bdate"][-4:]  # type:ignore
            if "." not in b_year:
                c = 1
                mas.append(int(current_date) - int(b_year))
    if c:
        return median(mas)
    return None
