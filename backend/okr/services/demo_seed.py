from datetime import date
from decimal import Decimal

from core.models import Role, Team, User
from okr.models import CheckIn, Comment, Okr, Quarter
from okr.services.okrs import create_okr

DEFAULT_USER_PASSWORD = 'secret123'


def seed_workspace_demo_data() -> dict[str, int]:
    """
    Наполняет базу абстрактными демонстрационными командами и OKR.

    :return: Сводка по количеству созданных или обновлённых сущностей.
    """
    counters = {
        'roles': 0,
        'teams': 0,
        'users': 0,
        'quarters': 0,
        'okrs': 0,
        'comments': 0,
        'check_ins': 0,
    }

    role_specs = [
        {
            'code': 'project-manager',
            'name': 'Проджект',
            'description': 'Отвечает за delivery, сроки и координацию команды.',
        },
        {
            'code': 'backend-engineer',
            'name': 'Backend',
            'description': 'Разрабатывает серверную логику и внутренние сервисы.',
        },
        {
            'code': 'frontend-engineer',
            'name': 'Frontend',
            'description': 'Разрабатывает пользовательские интерфейсы и клиентские сценарии.',
        },
        {
            'code': 'qa-engineer',
            'name': 'QA',
            'description': 'Отвечает за качество, проверки и регрессию.',
        },
        {
            'code': 'product-manager',
            'name': 'Продакт',
            'description': 'Формирует приоритеты и отвечает за продуктовые решения.',
        },
        {
            'code': 'teamlead',
            'name': 'Тимлид',
            'description': 'Ведёт техническое направление и помогает команде с решениями.',
        },
    ]

    roles: dict[str, Role] = {}
    for role_spec in role_specs:
        role, created = Role.objects.get_or_create(
            code=role_spec['code'],
            defaults={
                'name': role_spec['name'],
                'description': role_spec['description'],
            },
        )
        if not created:
            role.name = role_spec['name']
            role.description = role_spec['description']
            role.save(update_fields=['name', 'description', 'updated_at'])
        else:
            counters['roles'] += 1
        roles[role.code] = role

    team_specs = [
        {
            'code': 'vector',
            'name': 'Vector',
            'description': 'Абстрактная продуктовая команда, сфокусированная на базовых пользовательских сценариях.',
        },
        {
            'code': 'horizon',
            'name': 'Horizon',
            'description': 'Абстрактная команда, развивающая совместную платформу и внутренние процессы.',
        },
        {
            'code': 'spark',
            'name': 'Spark',
            'description': 'Абстрактная команда, которая ускоряет запуск новых инициатив и экспериментов.',
        },
    ]

    teams: dict[str, Team] = {}
    for team_spec in team_specs:
        team, created = Team.objects.get_or_create(
            code=team_spec['code'],
            defaults={
                'name': team_spec['name'],
                'description': team_spec['description'],
            },
        )
        if created:
            counters['teams'] += 1
        else:
            team.name = team_spec['name']
            team.description = team_spec['description']
            team.save(update_fields=['name', 'description', 'updated_at'])
        teams[team.code] = team

    user_specs = [
        {
            'email': 'mira.arlan@vector.local',
            'first_name': 'Мира',
            'last_name': 'Арлан',
            'role_code': 'project-manager',
            'team_code': 'vector',
            'is_staff': True,
        },
        {
            'email': 'lev.orin@vector.local',
            'first_name': 'Лев',
            'last_name': 'Орин',
            'role_code': 'backend-engineer',
            'team_code': 'vector',
            'is_staff': False,
        },
        {
            'email': 'nora.vey@vector.local',
            'first_name': 'Нора',
            'last_name': 'Вей',
            'role_code': 'frontend-engineer',
            'team_code': 'vector',
            'is_staff': False,
        },
        {
            'email': 'tina.korr@vector.local',
            'first_name': 'Тина',
            'last_name': 'Корр',
            'role_code': 'qa-engineer',
            'team_code': 'vector',
            'is_staff': False,
        },
        {
            'email': 'arta.niv@horizon.local',
            'first_name': 'Арта',
            'last_name': 'Нив',
            'role_code': 'project-manager',
            'team_code': 'horizon',
            'is_staff': True,
        },
        {
            'email': 'roman.elg@horizon.local',
            'first_name': 'Роман',
            'last_name': 'Элг',
            'role_code': 'backend-engineer',
            'team_code': 'horizon',
            'is_staff': False,
        },
        {
            'email': 'lina.svero@horizon.local',
            'first_name': 'Лина',
            'last_name': 'Сверо',
            'role_code': 'frontend-engineer',
            'team_code': 'horizon',
            'is_staff': False,
        },
        {
            'email': 'vera.monn@horizon.local',
            'first_name': 'Вера',
            'last_name': 'Монн',
            'role_code': 'qa-engineer',
            'team_code': 'horizon',
            'is_staff': False,
        },
        {
            'email': 'yara.fenn@spark.local',
            'first_name': 'Яра',
            'last_name': 'Фенн',
            'role_code': 'project-manager',
            'team_code': 'spark',
            'is_staff': True,
        },
        {
            'email': 'maks.tero@spark.local',
            'first_name': 'Макс',
            'last_name': 'Теро',
            'role_code': 'backend-engineer',
            'team_code': 'spark',
            'is_staff': False,
        },
        {
            'email': 'sana.irel@spark.local',
            'first_name': 'Сана',
            'last_name': 'Ирел',
            'role_code': 'frontend-engineer',
            'team_code': 'spark',
            'is_staff': False,
        },
        {
            'email': 'oleg.rim@spark.local',
            'first_name': 'Олег',
            'last_name': 'Рим',
            'role_code': 'qa-engineer',
            'team_code': 'spark',
            'is_staff': False,
        },
        {
            'email': 'daria.zen@vector.local',
            'first_name': 'Дарья',
            'last_name': 'Зен',
            'role_code': 'product-manager',
            'team_code': 'vector',
            'is_staff': False,
        },
        {
            'email': 'igor.valn@horizon.local',
            'first_name': 'Игорь',
            'last_name': 'Валн',
            'role_code': 'teamlead',
            'team_code': 'horizon',
            'is_staff': False,
        },
    ]

    users: dict[str, User] = {}
    for user_spec in user_specs:
        team = teams[user_spec['team_code']]
        user = User.objects.filter(email=user_spec['email']).first()
        if user is None:
            user = User.objects.create_user(
                email=user_spec['email'],
                password=DEFAULT_USER_PASSWORD,
                first_name=user_spec['first_name'],
                last_name=user_spec['last_name'],
                role=roles[user_spec['role_code']],
                primary_team=team,
                is_active=True,
                is_staff=user_spec['is_staff'],
            )
            counters['users'] += 1
        else:
            user.first_name = user_spec['first_name']
            user.last_name = user_spec['last_name']
            user.role = roles[user_spec['role_code']]
            user.primary_team = team
            user.is_active = True
            user.is_staff = user_spec['is_staff']
            user.save(
                update_fields=[
                    'first_name',
                    'last_name',
                    'role',
                    'primary_team',
                    'is_active',
                    'is_staff',
                    'updated_at',
                ],
            )

        user.teams.set([team])
        users[user.email] = user

    quarter_specs = [
        {
            'year': 2026,
            'quarter': 2,
            'start_date': date(2026, 4, 1),
            'end_date': date(2026, 6, 30),
            'is_active': True,
        },
        {
            'year': 2026,
            'quarter': 3,
            'start_date': date(2026, 7, 1),
            'end_date': date(2026, 9, 30),
            'is_active': False,
        },
    ]

    quarters: dict[str, Quarter] = {}
    for quarter_spec in quarter_specs:
        quarter, created = Quarter.objects.get_or_create(
            year=quarter_spec['year'],
            quarter=quarter_spec['quarter'],
            defaults={
                'start_date': quarter_spec['start_date'],
                'end_date': quarter_spec['end_date'],
                'is_active': quarter_spec['is_active'],
            },
        )
        quarter.start_date = quarter_spec['start_date']
        quarter.end_date = quarter_spec['end_date']
        quarter.is_active = quarter_spec['is_active']
        quarter.save(update_fields=['start_date', 'end_date', 'is_active'])
        if created:
            counters['quarters'] += 1
        quarters[quarter.name] = quarter

    Okr.objects.filter(team__in=teams.values()).delete()

    okr_specs = [
        {
            'team_code': 'vector',
            'title': 'Сделать базовый цикл поставки предсказуемым',
            'description': 'Собрать устойчивый процесс от постановки задачи до выпуска без привязки к конкретному домену.',
            'owner': users['mira.arlan@vector.local'],
            'period': quarters['Q2 2026'],
            'status': 'on_track',
            'key_results': [
                {
                    'title': 'Сократить средний цикл задачи от старта до релиза',
                    'description': 'Измеряется в рабочих днях по задачам стандартного размера.',
                    'metric_type': 'number',
                    'start_value': Decimal('14.00'),
                    'current_value': Decimal('10.00'),
                    'target_value': Decimal('8.00'),
                    'status': 'on_track',
                },
                {
                    'title': 'Довести долю задач с понятным определением готовности',
                    'description': 'Команда использует единые критерии готовности перед релизом.',
                    'metric_type': 'percent',
                    'start_value': Decimal('45.00'),
                    'current_value': Decimal('72.00'),
                    'target_value': Decimal('85.00'),
                    'status': 'on_track',
                },
            ],
            'comment': 'Процесс выровнялся, но ещё проседает подготовка задач на входе.',
        },
        {
            'team_code': 'vector',
            'title': 'Собрать единый пользовательский контур для ключевых экранов',
            'description': 'Упростить базовые сценарии и снизить число разрывов между ролями внутри команды.',
            'owner': users['daria.zen@vector.local'],
            'period': quarters['Q2 2026'],
            'status': 'on_track',
            'key_results': [
                {
                    'title': 'Провести 6 быстрых проверок сценариев с пользователями',
                    'description': 'Фокус на первых шагах и основных точках отказа.',
                    'metric_type': 'number',
                    'start_value': Decimal('0.00'),
                    'current_value': Decimal('4.00'),
                    'target_value': Decimal('6.00'),
                    'status': 'on_track',
                },
                {
                    'title': 'Снизить число замечаний по навигации в релизах',
                    'description': 'Считаются замечания, попавшие в финальный список перед выпуском.',
                    'metric_type': 'number',
                    'start_value': Decimal('9.00'),
                    'current_value': Decimal('4.00'),
                    'target_value': Decimal('3.00'),
                    'status': 'on_track',
                },
            ],
            'comment': 'Больше всего эффекта дала чистка перегруженных точек входа.',
        },
        {
            'team_code': 'horizon',
            'title': 'Повысить надёжность внутренней платформы команды',
            'description': 'Снизить нестабильность окружений и ускорить реакцию на технические проблемы.',
            'owner': users['igor.valn@horizon.local'],
            'period': quarters['Q2 2026'],
            'status': 'at_risk',
            'key_results': [
                {
                    'title': 'Снизить число критичных сбоев в общих сервисах',
                    'description': 'Учитываются сбои, которые влияют минимум на одну команду целиком.',
                    'metric_type': 'number',
                    'start_value': Decimal('7.00'),
                    'current_value': Decimal('4.00'),
                    'target_value': Decimal('2.00'),
                    'status': 'at_risk',
                },
                {
                    'title': 'Сократить среднее время восстановления сервиса',
                    'description': 'Измеряется в минутах по инцидентам высокой важности.',
                    'metric_type': 'number',
                    'start_value': Decimal('95.00'),
                    'current_value': Decimal('70.00'),
                    'target_value': Decimal('45.00'),
                    'status': 'at_risk',
                },
            ],
            'comment': 'Основной риск сейчас в нестабильных стендах и ручных переключениях.',
        },
        {
            'team_code': 'horizon',
            'title': 'Укрепить инженерное качество перед следующим кварталом',
            'description': 'Сделать регрессию и выпуск изменений более предсказуемыми.',
            'owner': users['vera.monn@horizon.local'],
            'period': quarters['Q2 2026'],
            'status': 'on_track',
            'key_results': [
                {
                    'title': 'Автоматизировать ночной прогон для критичных сценариев',
                    'description': 'Прогоны должны стабильно отрабатывать без ручного вмешательства.',
                    'metric_type': 'percent',
                    'start_value': Decimal('40.00'),
                    'current_value': Decimal('78.00'),
                    'target_value': Decimal('90.00'),
                    'status': 'on_track',
                },
                {
                    'title': 'Снизить число возвратов задач из тестирования',
                    'description': 'Учитываются возвраты по повторяющимся проблемам качества.',
                    'metric_type': 'number',
                    'start_value': Decimal('11.00'),
                    'current_value': Decimal('5.00'),
                    'target_value': Decimal('3.00'),
                    'status': 'on_track',
                },
            ],
            'comment': 'Автотесты уже закрывают основу, но на редких ветках есть нестабильность.',
        },
        {
            'team_code': 'spark',
            'title': 'Ускорить запуск новых инициатив без потери качества',
            'description': 'Сократить путь от идеи до первого рабочего результата в абстрактных продуктовых потоках.',
            'owner': users['yara.fenn@spark.local'],
            'period': quarters['Q2 2026'],
            'status': 'on_track',
            'key_results': [
                {
                    'title': 'Довести до запуска 3 инициативы в ограниченном контуре',
                    'description': 'Считаются только инициативы, прошедшие полный цикл подготовки и выпуска.',
                    'metric_type': 'number',
                    'start_value': Decimal('0.00'),
                    'current_value': Decimal('2.00'),
                    'target_value': Decimal('3.00'),
                    'status': 'on_track',
                },
                {
                    'title': 'Снизить среднее время согласования перед стартом',
                    'description': 'Измеряется в рабочих днях между идеей и подтверждённым запуском.',
                    'metric_type': 'number',
                    'start_value': Decimal('12.00'),
                    'current_value': Decimal('7.00'),
                    'target_value': Decimal('5.00'),
                    'status': 'on_track',
                },
            ],
            'comment': 'Команда стала быстрее стартовать, когда унифицировала шаблон подготовки.',
        },
        {
            'team_code': 'spark',
            'title': 'Подготовить техническую основу Spark к Q3',
            'description': 'Сформировать понятный запас по скорости разработки и качеству интерфейсов к следующему кварталу.',
            'owner': users['maks.tero@spark.local'],
            'period': quarters['Q3 2026'],
            'status': 'draft',
            'key_results': [
                {
                    'title': 'Подготовить план упрощения серверных модулей',
                    'description': 'План должен описывать последовательность работ и ожидаемый эффект.',
                    'metric_type': 'number',
                    'start_value': Decimal('0.00'),
                    'current_value': Decimal('1.00'),
                    'target_value': Decimal('3.00'),
                    'status': 'draft',
                },
                {
                    'title': 'Согласовать набор UI-паттернов для новых потоков',
                    'description': 'Набор нужен, чтобы быстрее запускать новые сценарии без визуального расползания.',
                    'metric_type': 'number',
                    'start_value': Decimal('0.00'),
                    'current_value': Decimal('1.00'),
                    'target_value': Decimal('2.00'),
                    'status': 'draft',
                },
            ],
            'comment': 'Q3 хотим начать с уже согласованной технической рамки.',
        },
    ]

    created_by = users['mira.arlan@vector.local']
    for okr_spec in okr_specs:
        okr = create_okr(
            title=okr_spec['title'],
            description=okr_spec['description'],
            owner_id=okr_spec['owner'].id,
            team_id=teams[okr_spec['team_code']].id,
            period_id=okr_spec['period'].id,
            status=okr_spec['status'],
            created_by=created_by,
            key_results_data=okr_spec['key_results'],
        )
        counters['okrs'] += 1

        Comment.objects.create(
            okr=okr,
            author=okr_spec['owner'],
            text=okr_spec['comment'],
        )
        counters['comments'] += 1

        first_key_result = okr.key_results.order_by('value', 'id').first()
        if first_key_result is not None and first_key_result.current_value != first_key_result.start_value:
            CheckIn.objects.create(
                key_result=first_key_result,
                author=okr_spec['owner'],
                new_value=first_key_result.current_value,
                comment='Актуализировали прогресс по демонстрационному примеру.',
            )
            counters['check_ins'] += 1

    return counters
