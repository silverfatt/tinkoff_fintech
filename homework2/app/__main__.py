import typer

from app.parse import get_temperature


def main(city_name: str):
    """
    main function, that prints temperature
    :param city_name:
    name of city
    """
    temperature = get_temperature(city_name)
    if temperature != 0:
        typer.echo(f"Current weather in {city_name} is {temperature}")
    return 0


if __name__ == "__main__":
    typer.run(main)
