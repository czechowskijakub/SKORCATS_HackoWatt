import datetime


class TimeHandler:

    @staticmethod
    def get_server_date() -> str:
        return str(datetime.date.today())

    @staticmethod
    def get_weekly_labels() -> list:
        """Zwraca listę 7 kolejnych dni tygodnia zaczynając od dzisiaj (np. ['Mon', 'Tue', ...])."""
        today = datetime.date.today()
        days_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        return [days_names[(today.weekday() + i) % 7] for i in range(7)]