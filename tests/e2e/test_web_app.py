import pytest


def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'User Accounts' in response.data


def test_happy_path_returns_200_and_adds_new_user(client):
    response = client.get('/?user=ian&email=ian@police.govt.nz')
    assert response.status_code == 200
    assert b'User Accounts' in response.data
    assert b'ian' in response.data
    assert b'ian@police.govt.nz' in response.data


def test_unhappy_path_returns_error_message_when_username_taken(client):
    client.get('/?user=ian&email=ian@police.govt.nz')

    response = client.get('/?user=ian&email=ian@police.govt.nz')
    assert b'already created!' in response.data