import pytest
from model_bakery import baker
from rest_framework.test import APIClient

from core.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def password():
    return 'secret123'


@pytest.fixture
def make_user(password):
    def _make_user(**kwargs):
        kwargs.setdefault('is_active', True)
        user = baker.make(User, **kwargs)
        user.set_password(password)
        user.save(update_fields=['password'])
        return user

    return _make_user


@pytest.fixture
def login_payload():
    return {
        'email': 'jwt@example.com',
        'password': 'secret123',
    }


@pytest.fixture
def login_user(make_user, login_payload):
    return make_user(email=login_payload['email'], is_staff=True)


@pytest.fixture
def access_token(api_client, login_payload, login_user):
    response = api_client.post('/api/core/auth/jwt/login/', login_payload, format='json')
    return response.data['access']


@pytest.fixture
def non_staff_access_token(api_client, make_user, password):
    user = make_user(email='member@example.com', is_staff=False)
    response = api_client.post(
        '/api/core/auth/jwt/login/',
        {
            'email': user.email,
            'password': password,
        },
        format='json',
    )
    return response.data['access']
