import random
import time
from decimal import Decimal
from threading import Thread

from app.datab import Base, Values, create_session, engine
from app.views import app

Base.metadata.create_all(engine)

with create_session() as session:  # pragma: no cover
    v1 = Values(name='Alphacoin', value='100')  # pragma: no cover
    v2 = Values(name='Betacoin', value='100')  # pragma: no cover
    v3 = Values(name='Gammacoin', value='100')  # pragma: no cover
    v4 = Values(name='Deltacoin', value='100')  # pragma: no cover
    v5 = Values(name='Epsiloncoin', value='100')  # pragma: no cover
    q = session.query(Values.name).filter(
        Values.name == 'Alphacoin'
    )  # pragma: no cover
    if not session.query(q.exists()).scalar():  # pragma: no cover
        session.add(v1)
        session.add(v2)
        session.add(v3)
        session.add(v4)
        session.add(v5)


def update_values() -> None:  # pragma: no cover
    """
    changes values of crypto every 10 seconds
    :return:
    """
    while True:  # pragma: no cover
        time.sleep(10)
        with create_session() as session:
            v = session.query(Values).all()
            for crypto in v:  # pragma: no cover
                number = Decimal(crypto.value)
                multiplier = Decimal(
                    (100 + (-1) ** random.randint(1, 2) * random.randint(1, 10)) / 100
                )
                crypto.value = str(number * multiplier)
            session.commit()


th = Thread(target=update_values)
th.start()

if __name__ == '__main__':  # pragma: no cover
    app.run(debug=True)
