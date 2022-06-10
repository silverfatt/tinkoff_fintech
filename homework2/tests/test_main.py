import datetime

import pytest
from freezegun import freeze_time

from app.__main__ import main
from app.parse import (cache_weather, connection_error, create_cache_dir,
                       get_temperature, incorrect_name, save_data,
                       server_unavailable, status_ok, try_to_load)
from app.relevance import is_relevant


@freeze_time("2005-07-14")
@pytest.fixture()
def cur_time():
    current_time = datetime.datetime.now()
    return current_time


def test_is_relevant(cur_time):
    assert is_relevant(cur_time)


def test_is_relevant_old():
    assert not is_relevant(datetime.datetime(2005, 7, 14, 12, 30))


def test_is_relevant_with_incorrect_type():
    with pytest.raises(TypeError):
        is_relevant(1)


def test_get_temperature_error_type():
    assert isinstance(get_temperature("moscowwwww"), int)


def test_get_temperature_with_incorrect_value():
    assert get_temperature("moscowwwwwww") == 0


def test_get_temperature_type():
    assert isinstance(get_temperature("moscow"), str)


def test_main_with_incorrect_type():
    with pytest.raises(TypeError):
        main(1, 4)


@pytest.mark.parametrize("city_name",
                         ["moscow",
                          "moscowwwwwwww"])
def test_main(city_name):
    assert main(city_name) == 0


def test_main_type():
    assert isinstance(main("moscow"), int)


def test_try_to_load_type():
    assert isinstance(try_to_load("moscow")[0], bool)
    assert isinstance(try_to_load("moscow")[1], str) or \
           isinstance(try_to_load("moscow")[1], type(None))


def test_try_to_load_incorrect_file_name():
    assert try_to_load("<>") == (False, None)


def test_get_temperature_incorrect_file_name():
    assert get_temperature("<>") == 0


def test_cache_weather_return_type():
    assert type(cache_weather(get_temperature)) == type(get_temperature)


def test_save_data():
    with pytest.raises(OSError):
        save_data("<>", None)


def test_create_cache_dir():
    assert isinstance(create_cache_dir("cache"), bool)


def test_create_cache_dir_incorrect_file_name():
    assert create_cache_dir("<>") is False


def test_status_ok():
    with pytest.raises(AttributeError):
        status_ok(1)


def test_incorrect_name():
    assert incorrect_name() == 0


def test_server_unavailable():
    assert server_unavailable() == 0


def test_connection_error():
    assert connection_error() == 0
