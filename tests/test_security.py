from jwt import decode

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
