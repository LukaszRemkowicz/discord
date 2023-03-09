import datetime
from types import GeneratorType

from utils.utils import daterange, Validator


def test_date_range_func() -> None:
    start_day: datetime.date = datetime.date(2023, 3, 22)
    end_day: datetime.date = datetime.date(2023, 4, 1)

    res: GeneratorType = daterange(start_date=start_day, end_date=end_day)
    res_list: list = [el for el in res]

    assert isinstance(res, GeneratorType)
    assert len(res_list) == 10
    assert datetime.date(2023, 3, 26) in res_list
    assert datetime.date(2023, 4, 1) not in res_list


def test_validator_context_manager() -> None:

    date: str = "20.01.2023"
    with Validator(date, "Warszawa") as validator:
        assert validator == date

    with Validator(date.replace(".2023", ""), "Warszawa") as validator:
        assert "error" in validator
