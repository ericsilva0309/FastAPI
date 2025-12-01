from http import HTTPStatus

from fastapi_zero.schemas import UserPublicSchema


def test_root_deve_retornar_hello_world(client):
    """
    Esse teste tem 3 estapas (AAA)
    - A: Arrage - Arranjo
    - A: Act    - Executa a coisa (SUT - System Under Test)
    - A: Assert - Garanta que o resultado é o esperado
    """
    # arrange
    # client = TestClient(app) # movido para o fixture

    # act
    response = client.get('/')

    # assert
    assert response.json() == {'message': 'Olá mundo!'}
    assert response.status_code == HTTPStatus.OK


def test_root_deve_retornar_html(client):
    response = client.get('/html')

    assert (
        response.text
        == """
    <html>
        <head>
            <title>Olá mundo!</title>
        </head>
        <body>
            <h1>Olá mundo!</h1>
        </body>
    <html>
            """
    )
    assert response.status_code == HTTPStatus.OK


def test_create_user(client):
    response = client.post(
        '/users',
        json={
            'username': 'eric',
            'email': 'eric@gmail.com',
            'password': '123123',
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': 'eric',
        'email': 'eric@gmail.com',
        'id': 1,
    }


def test_read_users_with_users(client, user):
    user_schema = UserPublicSchema.model_validate(user).model_dump()
    response = client.get('/users')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_update_user(client, user):
    response = client.put(
        '/users/1',
        json={
            'username': 'eric_updated',
            'email': 'eric_updated@gmail.com',
            'password': '123123',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'eric_updated',
        'email': 'eric_updated@gmail.com',
        'id': 1,
    }


def test_delete_user(client, user):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted successfully'}
    # Verifica se o usuário foi realmente removido
    # response = client.get('/users')
    # assert response.status_code == HTTPStatus.OK
    # assert response.json() == {
    #     'users': []
    # }


def test_update_integrity_error(client, user):
    client.post(
        '/users',
        json={
            'username': 'fausto',
            'email': 'fausto@example.com',
            'password': 'secret',
        },
    )

    response = client.put(
        f'/users/{user.id}',
        json={
            'username': 'fausto',
            'email': 'fausto@example.com',
            'password': 'secret',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or Email already registered'}
