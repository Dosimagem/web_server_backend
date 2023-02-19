from datetime import date, timedelta


def new_test_period(days: int = 30) -> dict:
    """
    New trial period using now with start date
    """

    day = date.today()
    delta = timedelta(days=days)

    return {'test_period_initial': day, 'test_period_end': day + delta}
