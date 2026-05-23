from jwt import decode

from fastapi_zero.security import create_access_token, SECRET_KEY, ALGORITHM


def test_jwt():
    data = {'test': 'test'}

    token = create_access_token(data)

    decoded = decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert decoded['test'] == data['test']
    assert 'exp' in decoded
