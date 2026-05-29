from http import HTTPStatus


def test_creat_todo(client, token):
    response = client.post(
        '/todo',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'test',
            'description': 'test',
            'state': 'todo',
        },
    )

    assert response.json() == {
        'id': 1,
        'title': 'test',
        'description': 'test',
        'state': 'todo',
    }
