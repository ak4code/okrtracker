from datetime import date

from okr.models import Quarter


def create_quarter(
    *,
    year: int,
    quarter_number: int,
    start_date: date,
    end_date: date,
    is_active: bool,
) -> Quarter:
    """
    Создаёт квартал OKR-планирования.

    :param year: Год квартала.
    :param quarter_number: Номер квартала от 1 до 4.
    :param start_date: Дата начала квартала.
    :param end_date: Дата окончания квартала.
    :param is_active: Флаг активного квартала.
    :return: Созданный квартал.
    """
    if is_active:
        Quarter.objects.filter(is_active=True).update(is_active=False)

    return Quarter.objects.create(
        year=year,
        quarter=quarter_number,
        start_date=start_date,
        end_date=end_date,
        is_active=is_active,
    )


def update_quarter(
    *,
    quarter: Quarter,
    year: int,
    quarter_number: int,
    start_date: date,
    end_date: date,
    is_active: bool,
) -> Quarter:
    """
    Обновляет квартал OKR-планирования.

    :param quarter: Экземпляр квартала для обновления.
    :param year: Год квартала.
    :param quarter_number: Номер квартала от 1 до 4.
    :param start_date: Дата начала квартала.
    :param end_date: Дата окончания квартала.
    :param is_active: Флаг активного квартала.
    :return: Обновлённый квартал.
    """
    if is_active:
        Quarter.objects.exclude(id=quarter.id).filter(is_active=True).update(is_active=False)

    quarter.year = year
    quarter.quarter = quarter_number
    quarter.start_date = start_date
    quarter.end_date = end_date
    quarter.is_active = is_active
    quarter.save(update_fields=['year', 'quarter', 'name', 'start_date', 'end_date', 'is_active'])
    return quarter
