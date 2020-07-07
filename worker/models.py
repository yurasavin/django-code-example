from django.contrib.auth.models import User


class Worker(User):
    """
    Прокси класс для Юзера, расширяет базового юзера методами,
    связанными с закупками, относящимися к юзеру.
    """

    class Meta:
        proxy = True
