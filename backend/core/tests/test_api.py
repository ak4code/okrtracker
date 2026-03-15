import pytest
from model_bakery import baker

from core.models import Role, Team, User

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def auth_api_client(api_client, access_token):
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    return api_client


@pytest.fixture
def non_staff_auth_api_client(api_client, non_staff_access_token):
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {non_staff_access_token}')
    return api_client


def test_role_list_api_returns_roles(auth_api_client):
    """
    Arrange: создаём роль и аутентифицируем API-клиент.
    Act: запрашиваем список ролей.
    Assert: endpoint возвращает созданную роль.
    """
    baker.make(Role, name='Тимлид', code='teamlead')

    response = auth_api_client.get('/api/core/roles/')

    assert response.status_code == 200
    assert response.data[0]['code'] == 'teamlead'


def test_role_create_api_creates_role(auth_api_client):
    """
    Arrange: аутентифицируем API-клиент и готовим данные роли.
    Act: создаём роль.
    Assert: endpoint возвращает созданную роль и сохранённый код.
    """
    response = auth_api_client.post(
        '/api/core/roles/',
        {'name': 'Руководитель', 'code': 'leader', 'description': 'Роль руководителя.'},
        format='json',
    )

    assert response.status_code == 201
    assert response.data['name'] == 'Руководитель'
    assert Role.objects.filter(code='leader').exists() is True


def test_role_update_api_updates_role(auth_api_client):
    """
    Arrange: создаём роль и аутентифицируем API-клиент.
    Act: обновляем роль.
    Assert: endpoint сохраняет новые данные роли.
    """
    role = baker.make(Role, name='Сотрудник', code='employee')

    response = auth_api_client.patch(
        f'/api/core/roles/{role.id}/',
        {'name': 'Тимлид', 'code': 'teamlead', 'description': 'Роль тимлида.'},
        format='json',
    )

    role.refresh_from_db()

    assert response.status_code == 200
    assert role.name == 'Тимлид'
    assert role.code == 'teamlead'


def test_role_create_api_forbidden_for_non_staff(non_staff_auth_api_client):
    """
    Arrange: аутентифицируем обычного пользователя без флага is_staff.
    Act: пытаемся создать роль через API.
    Assert: endpoint возвращает 403 Forbidden.
    """
    response = non_staff_auth_api_client.post(
        '/api/core/roles/',
        {'name': 'Руководитель', 'code': 'leader', 'description': 'Роль руководителя.'},
        format='json',
    )

    assert response.status_code == 403


def test_team_create_api_creates_team(auth_api_client):
    """
    Arrange: аутентифицируем API-клиент и готовим данные команды.
    Act: создаём команду.
    Assert: endpoint возвращает созданную команду и сохранённый код.
    """
    response = auth_api_client.post(
        '/api/core/teams/',
        {'name': 'Platform', 'code': 'platform', 'description': 'Платформенная команда.'},
        format='json',
    )

    assert response.status_code == 201
    assert response.data['name'] == 'Platform'
    assert Team.objects.filter(code='platform').exists() is True


def test_team_update_api_updates_team(auth_api_client):
    """
    Arrange: создаём команду и аутентифицируем API-клиент.
    Act: обновляем команду.
    Assert: endpoint сохраняет новые данные команды.
    """
    team = baker.make(Team, name='Platform', code='platform')

    response = auth_api_client.patch(
        f'/api/core/teams/{team.id}/',
        {'name': 'Frontend', 'code': 'frontend', 'description': 'Новая команда.'},
        format='json',
    )

    team.refresh_from_db()

    assert response.status_code == 200
    assert team.name == 'Frontend'
    assert team.code == 'frontend'


def test_team_update_api_forbidden_for_non_staff(non_staff_auth_api_client):
    """
    Arrange: создаём команду и аутентифицируем обычного пользователя.
    Act: пытаемся обновить команду через API.
    Assert: endpoint возвращает 403 Forbidden.
    """
    team = baker.make(Team, name='Platform', code='platform')

    response = non_staff_auth_api_client.patch(
        f'/api/core/teams/{team.id}/',
        {'name': 'Frontend', 'code': 'frontend', 'description': 'Новая команда.'},
        format='json',
    )

    assert response.status_code == 403


def test_user_list_api_returns_users(auth_api_client):
    """
    Arrange: создаём пользователя с ролью и командой.
    Act: запрашиваем список пользователей.
    Assert: endpoint возвращает пользователя со связанными данными.
    """
    role = baker.make(Role, name='Сотрудник', code='employee')
    team = baker.make(Team, name='Platform', code='platform')
    user = baker.make(User, email='member@example.com', role=role, primary_team=team)
    user.teams.add(team)

    response = auth_api_client.get('/api/core/users/')

    assert response.status_code == 200
    user_payload = next(item for item in response.data if item['email'] == 'member@example.com')
    assert user_payload['role'] == 'Сотрудник'
    assert user_payload['primary_team'] == 'Platform'


def test_user_create_api_creates_user(auth_api_client):
    """
    Arrange: создаём роль и команду.
    Act: создаём пользователя через API.
    Assert: endpoint создаёт пользователя и связывает его с командами.
    """
    role = baker.make(Role, name='Сотрудник', code='employee')
    team = baker.make(Team, name='Platform', code='platform')

    response = auth_api_client.post(
        '/api/core/users/',
        {
            'email': 'new@example.com',
            'first_name': 'Иван',
            'last_name': 'Петров',
            'role_id': role.id,
            'primary_team_id': team.id,
            'team_ids': [team.id],
            'is_active': True,
            'is_staff': False,
            'password': 'secret123',
        },
        format='json',
    )

    user = User.objects.get(email='new@example.com')

    assert response.status_code == 201
    assert user.role_id == role.id
    assert user.primary_team_id == team.id
    assert list(user.teams.values_list('id', flat=True)) == [team.id]


def test_user_update_api_updates_user(auth_api_client):
    """
    Arrange: создаём пользователя, роль и команды.
    Act: обновляем пользователя через API.
    Assert: endpoint сохраняет новые связанные данные пользователя.
    """
    role = baker.make(Role, name='Тимлид', code='teamlead')
    team = baker.make(Team, name='Platform', code='platform')
    next_team = baker.make(Team, name='Frontend', code='frontend')
    user = baker.make(User, email='member@example.com', primary_team=team)
    user.teams.add(team)

    response = auth_api_client.patch(
        f'/api/core/users/{user.id}/',
        {
            'email': 'member@example.com',
            'first_name': 'Анна',
            'last_name': 'Иванова',
            'role_id': role.id,
            'primary_team_id': next_team.id,
            'team_ids': [team.id, next_team.id],
            'is_active': True,
            'is_staff': True,
            'password': '',
        },
        format='json',
    )

    user.refresh_from_db()

    assert response.status_code == 200
    assert user.first_name == 'Анна'
    assert user.role_id == role.id
    assert user.primary_team_id == next_team.id
    assert sorted(user.teams.values_list('id', flat=True)) == sorted([team.id, next_team.id])


def test_user_create_api_forbidden_for_non_staff(non_staff_auth_api_client):
    """
    Arrange: создаём роль и команду для payload обычного пользователя.
    Act: пытаемся создать пользователя через API.
    Assert: endpoint возвращает 403 Forbidden.
    """
    role = baker.make(Role, name='Сотрудник', code='employee')
    team = baker.make(Team, name='Platform', code='platform')

    response = non_staff_auth_api_client.post(
        '/api/core/users/',
        {
            'email': 'new@example.com',
            'first_name': 'Иван',
            'last_name': 'Петров',
            'role_id': role.id,
            'primary_team_id': team.id,
            'team_ids': [team.id],
            'is_active': True,
            'is_staff': False,
            'password': 'secret123',
        },
        format='json',
    )

    assert response.status_code == 403
