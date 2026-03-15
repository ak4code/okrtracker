from django.core.management.base import BaseCommand

from okr.services.demo_seed import seed_workspace_demo_data


class Command(BaseCommand):
    help = 'Наполняет базу абстрактными демонстрационными командами и OKR.'

    def handle(self, *args, **options) -> None:
        """
        Запускает заполнение базы демонстрационными OKR.

        :param args: Позиционные аргументы команды.
        :param options: Именованные аргументы команды.
        """
        counters = seed_workspace_demo_data()
        self.stdout.write(
            self.style.SUCCESS(
                'Готово: '
                f'ролей {counters["roles"]}, '
                f'команд {counters["teams"]}, '
                f'пользователей {counters["users"]}, '
                f'кварталов {counters["quarters"]}, '
                f'OKR {counters["okrs"]}, '
                f'комментариев {counters["comments"]}, '
                f'check-in {counters["check_ins"]}.',
            ),
        )
