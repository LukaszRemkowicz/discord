import datetime
from types import GeneratorType

from utils.utils import Validator, daterange, daterange_by_minutes


def test_date_range_func() -> None:
    start_day: datetime.date = datetime.date(2023, 3, 22)
    end_day: datetime.date = datetime.date(2023, 4, 1)

    res: GeneratorType = daterange(start_date=start_day, end_date=end_day)
    res_list: list = [el for el in res]

    assert isinstance(res, GeneratorType)
    assert len(res_list) == 10
    assert datetime.date(2023, 3, 26) in res_list
    assert datetime.date(2023, 4, 1) not in res_list


def test_date_range_by_days_func() -> None:
    sunset: datetime = datetime.datetime.now()
    new_sunset: datetime = sunset.replace(hour=23, minute=10)

    sunrise: datetime = datetime.datetime.now()
    new_sunrise: datetime = sunrise.replace(hour=5, minute=1)

    res: GeneratorType = daterange_by_minutes(
        start_date=new_sunrise, end_date=new_sunset
    )
    res_list: list = [el for el in res]

    now: datetime = datetime.datetime.now()
    new_now: datetime = now.replace(hour=23, minute=20).strftime("%Y-%m-%d %H:%M")

    assert isinstance(res, GeneratorType)
    assert new_now not in res_list

    now = datetime.datetime.now()
    new_now: datetime = now.replace(hour=12).strftime("%Y-%m-%d %H:%M")

    assert new_now in res_list


def test_validator_context_manager() -> None:
    date: str = "20.01.2023"
    with Validator(date, "Warszawa") as validator:
        assert validator == date

    with Validator(date.replace(".2023", ""), "Warszawa") as validator:
        assert "error" in validator
