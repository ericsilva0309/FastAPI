from http import HTTPStatus

from fastapi.testclient import TestClient

from fastapi_zero.app import app

client = TestClient(app)


def test_root_deve_retornar_hello_world():
    """
    Esse teste tem 3 estapas (AAA)
    - A: Arrage - Arranjo
    - A: Act    - Executa a coisa (SUT - System Under Test)
    - A: Assert - Garanta que o resultado é o esperado
    """
    # arrange
    client = TestClient(app)

    # act
    response = client.get('/')

    # assert
    assert response.json() == {'Hello': 'World'}
    assert response.status_code == HTTPStatus.OK
