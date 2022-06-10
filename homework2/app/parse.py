import datetime
import os.path
import pickle
from http import HTTPStatus

import requests
import typer
from bs4 import BeautifulSoup

from app.relevance import is_relevant

URL = "https://world-weather.ru/pogoda/russia/"
HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) \
    Chrome/96.0.4664.174 YaBrowser/22.1.4.840 Yowser/2.5 Safari/537.36",
    "accept": "*/*",
}


def try_to_load(city_name):
    """
    tries to load temperature
    :param city_name: name of city
    :return: True and str if there is a relevant temperature,
    False and None in opposite
    """
    try:
        with open(f"cache/{city_name}.pickle", "rb") as f:
            data = pickle.load(f)
        caching_time, temperature = data
        relevance = is_relevant(caching_time)
        return relevance, temperature
    except FileNotFoundError:
        pass
    except OSError:
        typer.echo("temperature was not loaded due to OSError")
    except pickle.UnpicklingError:
        typer.echo("temperature was not loaded due to UnpicklingError")
    relevance = False
    return relevance, None


def save_data(city_name, data):
    """
    saves data
    :param city_name: name of city
    :param data: data to save - str and datetime
    :return:
    """
    with open(f"cache/{city_name}.pickle", "wb") as f:
        pickle.dump(data, f)


def create_cache_dir(dir):
    """
    tries to create cache directory
    :param dir: name of dir
    :return: True if OSError
    """
    created = True
    try:
        if not os.path.isdir(dir):
            os.mkdir(dir, mode=0o777)
    except OSError:
        typer.echo("could not create cache directory"
                   " - caching is unavailable")
        created = False
    return created


def cache_weather(get_temperature):
    """
    decorator that allows get_temperature func to get temperature from cache
    :param main: get_temperature function
    :return: None
    """

    def wrapper(city_name):
        created = create_cache_dir("cache")
        relevance = False
        if created:
            relevance, temperature = try_to_load(city_name)
        if relevance:
            weather = get_temperature(city_name, temperature)
        else:
            weather = get_temperature(city_name)
        if weather != 0:
            current_time = datetime.datetime.now()
            data = current_time, weather
            if created:
                save_data(city_name, data)
        return weather

    return wrapper


@cache_weather
def get_temperature(city_name: str, temperature=None):
    """
    Parses html-page and gets temperature in city named 'city-name'
    :param city_name: name of city
    :param temperature: uncached temperature or None if there is no cache
    :return: city temperature in str format or 0 in int format if could not
    get temperature
    """
    if temperature is not None:
        return temperature
    else:
        try:
            requested_html = requests.get(f"{URL}{city_name}/",
                                          headers=HEADERS, params=None)
        except requests.exceptions.ConnectionError:
            return connection_error()
        if requested_html.status_code == HTTPStatus.OK:
            return status_ok(requested_html)
        elif requested_html.status_code == HTTPStatus.NOT_FOUND:
            return incorrect_name()
        else:
            return server_unavailable()


def status_ok(requested_html):
    soup = BeautifulSoup(requested_html.text, "html.parser")
    weather = soup.find("div", id="weather-now-number")
    return weather.get_text(strip=True)


def incorrect_name():
    typer.echo('incorrect city name')
    return 0


def server_unavailable():
    typer.echo('server is unavailable')
    return 0


def connection_error():
    typer.echo('internet connection is unavailable')
    return 0
