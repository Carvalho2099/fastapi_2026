from jwt import decode
from http import HTTPStatus
from freezegun import freeze_time

from fastapi_zero.security import create_access_token
from fastapi_zero.settings import Settings

settings = Settings()


def test_jwt():
    data = {'test': 'test'}

    token = create_access_token(data)

    decoded = decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )

    assert decoded['test'] == data['test']
    assert 'exp' in decoded


def test_token_expired_after_time(client, user):
    with freeze_time('2023-07-14 12:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.clean_password},
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json()['access_token']
