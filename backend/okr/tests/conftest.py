from decimal import Decimal

import pytest
from model_bakery import baker

from okr.models import KeyResult, Okr, Quarter

pytest_plugins = ('common_utils.pytest.fixtures',)


@pytest.fixture
def auth_api_client(api_client, access_token):
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    return api_client


@pytest.fixture
def team():
    return baker.make('core.Team', name='Platform')


@pytest.fixture
def quarter():
    return baker.make(Quarter, year=2026, quarter=2, is_active=True)


@pytest.fixture
def period():
    return baker.make(Quarter, year=2026, quarter=1)


@pytest.fixture
def okr_owner(make_user, team):
    return make_user(
        email='owner@example.com',
        first_name='Анна',
        last_name='Смирнова',
        primary_team=team,
    )


@pytest.fixture
def owner(make_user, team):
    return make_user(primary_team=team)


@pytest.fixture
def okr(okr_owner, team, quarter):
    return baker.make(
        Okr,
        title='Сократить lead time релизов',
        description='Ускорить поставку изменений.',
        owner=okr_owner,
        team=team,
        period=quarter,
        created_by=okr_owner,
        progress=Decimal('0.7'),
        status='at_risk',
    )


@pytest.fixture
def model_okr(owner, team, period):
    return baker.make(
        Okr,
        owner=owner,
        team=team,
        period=period,
        created_by=owner,
        progress=Decimal('0.0'),
    )


@pytest.fixture
def key_result(okr):
    return baker.make(
        KeyResult,
        okr=okr,
        title='Снизить lead time',
        start_value=Decimal('0.00'),
        current_value=Decimal('80.00'),
        target_value=Decimal('100.00'),
        status='on_track',
        value=Decimal('0.3'),
    )


@pytest.fixture
def model_key_result(model_okr):
    return baker.make(
        KeyResult,
        okr=model_okr,
        start_value=Decimal('0.00'),
        current_value=Decimal('0.00'),
        target_value=Decimal('100.00'),
        value=Decimal('0.3'),
    )
