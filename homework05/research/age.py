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
    friend_bdate = get_friends(user_id, fields="bdate").items  # type:ignore
    friends_birthday_year = []
    year_found = False
    current_date = datetime.now().date().year
    for bdate in friend_bdate:
        if "bdate" in bdate.keys():  # type:ignore
            b_year = bdate["bdate"][-4:]  # type:ignore
            if "." not in b_year:
                year_found = True
                friends_birthday_year.append(int(current_date) - int(b_year))
    if year_found:
        return median(friends_birthday_year)
    return None
