from fastapi import status
from fastapi.testclient import TestClient

from app.app import app
from app.schemas import UserScheme

client = TestClient(app)


def test_register():
    u_s = UserScheme(login='Existing', password='afdqwsfc')
    msg = {'login': u_s.login, 'password': u_s.password}
    response = client.post('/register', json=msg)
    assert response.status_code == status.HTTP_200_OK
    u_s = UserScheme(login='Existing', password='afdqwsfc')
    msg = {'login': u_s.login, 'password': u_s.password}
    response = client.post('/register', json=msg)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    u_s = UserScheme(login='NotExisting', password='afdqwsfc')
    msg = {'login': u_s.login, 'password': u_s.password}
    response = client.post('/register', json=msg)
    assert response.status_code == status.HTTP_200_OK
