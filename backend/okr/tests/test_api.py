from decimal import Decimal

import pytest
from model_bakery import baker

from okr.models import ChangeLog, CheckIn, Comment, Okr, Quarter

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def non_staff_auth_api_client(api_client, non_staff_access_token):
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {non_staff_access_token}')
    return api_client


def test_quarter_list_api_returns_quarters(auth_api_client, quarter):
    """
    Arrange: создаём квартал и аутентифицируем API-клиент.
    Act: запрашиваем список кварталов.
    Assert: endpoint возвращает квартал с ожидаемым названием и статусом активности.
    """
    response = auth_api_client.get('/api/okr/quarters/')

    assert response.status_code == 200
    assert response.data[0]['name'] == 'Q2 2026'
    assert response.data[0]['is_active'] is True


def test_quarter_create_api_creates_quarter(auth_api_client):
    """
    Arrange: аутентифицируем API-клиент и готовим данные нового квартала.
    Act: отправляем запрос на создание квартала.
    Assert: endpoint создаёт квартал и возвращает вычисленное название.
    """
    response = auth_api_client.post(
        '/api/okr/quarters/',
        {
            'year': 2026,
            'quarter': 3,
            'start_date': '2026-07-01',
            'end_date': '2026-09-30',
            'is_active': False,
        },
        format='json',
    )

    assert response.status_code == 201
    assert response.data['name'] == 'Q3 2026'
    assert Quarter.objects.filter(year=2026, quarter=3).exists() is True


def test_quarter_create_api_switches_active_flag(auth_api_client, quarter):
    """
    Arrange: создаём активный квартал и аутентифицируем API-клиент.
    Act: создаём новый квартал с флагом активности.
    Assert: новый квартал становится активным, а предыдущий деактивируется.
    """
    response = auth_api_client.post(
        '/api/okr/quarters/',
        {
            'year': 2026,
            'quarter': 3,
            'start_date': '2026-07-01',
            'end_date': '2026-09-30',
            'is_active': True,
        },
        format='json',
    )

    quarter.refresh_from_db()

    assert response.status_code == 201
    assert response.data['is_active'] is True
    assert quarter.is_active is False


def test_quarter_update_api_updates_existing_quarter(auth_api_client, quarter):
    """
    Arrange: создаём квартал и аутентифицируем API-клиент.
    Act: отправляем запрос на обновление квартала.
    Assert: endpoint сохраняет новые даты, год, номер квартала и активность.
    """
    response = auth_api_client.patch(
        f'/api/okr/quarters/{quarter.id}/',
        {
            'year': 2027,
            'quarter': 1,
            'start_date': '2027-01-01',
            'end_date': '2027-03-31',
            'is_active': False,
        },
        format='json',
    )

    quarter.refresh_from_db()

    assert response.status_code == 200
    assert response.data['name'] == 'Q1 2027'
    assert quarter.name == 'Q1 2027'
    assert quarter.is_active is False


def test_quarter_create_api_forbidden_for_non_staff(non_staff_auth_api_client):
    """
    Arrange: аутентифицируем обычного пользователя без флага is_staff.
    Act: пытаемся создать квартал через API.
    Assert: endpoint возвращает 403 Forbidden.
    """
    response = non_staff_auth_api_client.post(
        '/api/okr/quarters/',
        {
            'year': 2026,
            'quarter': 3,
            'start_date': '2026-07-01',
            'end_date': '2026-09-30',
            'is_active': False,
        },
        format='json',
    )

    assert response.status_code == 403


def test_quarter_update_api_forbidden_for_non_staff(non_staff_auth_api_client, quarter):
    """
    Arrange: создаём квартал и аутентифицируем обычного пользователя.
    Act: пытаемся обновить квартал через API.
    Assert: endpoint возвращает 403 Forbidden.
    """
    response = non_staff_auth_api_client.patch(
        f'/api/okr/quarters/{quarter.id}/',
        {
            'year': 2027,
            'quarter': 1,
            'start_date': '2027-01-01',
            'end_date': '2027-03-31',
            'is_active': False,
        },
        format='json',
    )

    assert response.status_code == 403


def test_okr_list_api_returns_items(auth_api_client, okr, key_result):
    """
    Arrange: создаём OKR с ключевым результатом и аутентифицируем API-клиент.
    Act: запрашиваем список OKR по кварталу.
    Assert: endpoint возвращает цель с командой, владельцем и количеством ключевых результатов.
    """
    baker.make(Comment, okr=okr, author=okr.owner, text='Первый комментарий.')

    response = auth_api_client.get('/api/okr/okrs/', {'quarter': 'Q2 2026'})

    assert response.status_code == 200
    assert response.data[0]['title'] == 'Сократить lead time релизов'
    assert response.data[0]['owner'] == 'Анна Смирнова'
    assert response.data[0]['team'] == 'Platform'
    assert response.data[0]['key_results_count'] == 1
    assert response.data[0]['comments_count'] == 1


def test_okr_detail_api_returns_nested_data(auth_api_client, okr, key_result):
    """
    Arrange: создаём OKR с check-in, комментарием и записью аудита.
    Act: запрашиваем детальную карточку OKR.
    Assert: endpoint возвращает вложенные key results, comments и change logs.
    """
    check_in = baker.make(
        CheckIn,
        key_result=key_result,
        author=okr.owner,
        new_value=Decimal('75.00'),
        comment='Есть прогресс.',
    )
    baker.make(Comment, okr=okr, author=okr.owner, text='Комментарий по цели.')
    baker.make(
        ChangeLog,
        entity_type='okr',
        entity_id=okr.id,
        action='updated',
        author=okr.owner,
        payload={
            'title': okr.title,
            'changes': [{'label': 'Статус', 'from': 'В графике', 'to': 'Под риском'}],
        },
    )
    baker.make(
        ChangeLog,
        entity_type='key_result',
        entity_id=key_result.id,
        action='updated',
        author=okr.owner,
        payload={
            'title': key_result.title,
            'changes': [{'label': 'Цель', 'from': '80.00', 'to': '100.00'}],
        },
    )
    baker.make(
        ChangeLog,
        entity_type='check_in',
        entity_id=check_in.id,
        action='created',
        author=okr.owner,
        payload={
            'key_result_id': key_result.id,
            'key_result_title': key_result.title,
            'new_value': '75.00',
            'comment': 'Есть прогресс.',
        },
    )

    response = auth_api_client.get(f'/api/okr/okrs/{okr.id}/')

    assert response.status_code == 200
    assert response.data['title'] == 'Сократить lead time релизов'
    assert response.data['key_results'][0]['title'] == 'Снизить lead time'
    assert response.data['key_results'][0]['value'] == '0.3'
    assert response.data['key_results'][0]['progress'] == '0.8'
    assert response.data['comments'][0]['text'] == 'Комментарий по цели.'
    change_log_entity_types = {item['entity_type'] for item in response.data['change_logs']}
    assert {'okr', 'key_result', 'check_in'}.issubset(change_log_entity_types)
    assert response.data['change_logs'][0]['details']


def test_okr_comment_create_api_adds_comment(auth_api_client, okr):
    """
    Arrange: создаём OKR и аутентифицируем API-клиент.
    Act: отправляем запрос на создание комментария к OKR.
    Assert: endpoint создаёт комментарий и возвращает обновлённую карточку OKR.
    """
    response = auth_api_client.post(
        f'/api/okr/okrs/{okr.id}/comments/',
        {
            'text': 'Зафиксировали договоренность по следующему релизу.',
        },
        format='json',
    )

    assert response.status_code == 201
    assert response.data['comments'][0]['text'] == 'Зафиксировали договоренность по следующему релизу.'
    assert Comment.objects.filter(okr=okr, text='Зафиксировали договоренность по следующему релизу.').exists() is True


def test_okr_create_api_creates_okr_with_key_results(auth_api_client, okr_owner, team, quarter):
    """
    Arrange: создаём владельца, команду, квартал и аутентифицируем API-клиент.
    Act: отправляем запрос на создание OKR с двумя ключевыми результатами.
    Assert: endpoint создаёт OKR, ключевые результаты и рассчитывает агрегированный прогресс.
    """
    response = auth_api_client.post(
        '/api/okr/okrs/',
        {
            'title': 'Повысить стабильность релизов',
            'description': 'Снизить число проблемных релизов.',
            'owner_id': okr_owner.id,
            'team_id': team.id,
            'period_id': quarter.id,
            'status': 'on_track',
            'key_results': [
                {
                    'title': 'Снизить rollback rate',
                    'description': '',
                    'metric_type': 'percent',
                    'start_value': '0.00',
                    'current_value': '20.00',
                    'target_value': '40.00',
                    'status': 'on_track',
                },
                {
                    'title': 'Увеличить покрытие smoke-checks',
                    'description': '',
                    'metric_type': 'percent',
                    'start_value': '10.00',
                    'current_value': '30.00',
                    'target_value': '50.00',
                    'status': 'on_track',
                },
            ],
        },
        format='json',
    )

    created_okr = Okr.objects.get(title='Повысить стабильность релизов')

    assert response.status_code == 201
    assert response.data['title'] == 'Повысить стабильность релизов'
    assert created_okr.key_results.count() == 2
    assert list(
        created_okr.key_results.order_by('value').values_list('value', flat=True),
    ) == [Decimal('0.3'), Decimal('0.7')]
    assert str(created_okr.progress) == '0.0'
    assert ChangeLog.objects.filter(entity_type='okr', entity_id=created_okr.id, action='created').exists() is True


def test_okr_create_api_requires_key_results(auth_api_client, okr_owner, team, quarter):
    """
    Arrange: создаём владельца, команду, квартал и аутентифицируем API-клиент.
    Act: отправляем запрос на создание OKR без ключевых результатов.
    Assert: endpoint возвращает ошибку валидации.
    """
    response = auth_api_client.post(
        '/api/okr/okrs/',
        {
            'title': 'Пустая цель',
            'description': '',
            'owner_id': okr_owner.id,
            'team_id': team.id,
            'period_id': quarter.id,
            'status': 'draft',
            'key_results': [],
        },
        format='json',
    )

    assert response.status_code == 400
    assert response.data['key_results'][0] == 'Добавьте хотя бы один ключевой результат.'


def test_key_result_update_api_updates_value(auth_api_client, key_result):
    """
    Arrange: создаём ключевой результат и аутентифицируем API-клиент.
    Act: отправляем PATCH-запрос на обновление KR, включая value.
    Assert: endpoint сохраняет новое значение KR и возвращает его в detail payload.
    """
    response = auth_api_client.patch(
        f'/api/okr/key-results/{key_result.id}/',
        {
            'title': key_result.title,
            'description': key_result.description,
            'value': '1.0',
            'metric_type': key_result.metric_type,
            'start_value': str(key_result.start_value),
            'current_value': str(key_result.current_value),
            'target_value': str(key_result.target_value),
            'status': 'completed',
        },
        format='json',
    )

    key_result.refresh_from_db()

    assert response.status_code == 200
    assert response.data['key_results'][0]['value'] == '1.0'
    assert str(key_result.value) == '1.0'
