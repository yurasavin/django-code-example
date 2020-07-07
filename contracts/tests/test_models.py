import datetime

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.core.cache import cache

from contracts.models import Contract, ContractChange, ContractNum
from core.cache import get_md5_int_hash
from tickets.models import Ticket
from tenders.models import Tender
from limits.models import Limit, Source, LimitArticle, IndustryCode, LimitMoney, Subdivision


class ContractTestCase(TestCase):
    """Тестирует поведение контракта"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='test_user',
            password='123'
        )
        self.limit = Limit.objects.create(year=2019)
        self.source = Source.objects.create(num=2, name='2', limit=self.limit)
        self.article = LimitArticle.objects.create(
            num=221,
            name='221',
            source=self.source
        )
        self.industry = IndustryCode.objects.create(
            num=9999,
            name='9999',
            limit_article=self.article
        )
        self.limit_money = LimitMoney.objects.create(
            name='no_name',
            sybsidy_code='00000',
            money=5000,
            industry_code=self.industry
        )
        self.subdivision = Subdivision.objects.create(
            name='01', num='01', source=self.source
        )
        date = datetime.date(2019, 5, 2)
        self.ticket = Ticket.objects.create(
            name='test_ticket',
            date=date,
            worker=self.user,
            initiator=1,
        )
        self.ticket.year.set([self.limit, ])
        self.ticket.save()
        self.contract = Contract.objects.create(
            num='1',
            date=date,
            specif='',
            ticket=self.ticket,
            bank_guar=False,
            pledge=0,
            kontragent='OOO "Romashka"'
        )

    def make_tender(self):
        """Создает тендер"""
        self.tender = Tender.objects.create(
            num='1',
            status='done',
            smp=False,
            ticket=self.ticket
        )
        self.tender.contract = self.contract
        self.contract.save()

    def test_contract_func_str(self):
        """Проверяет корректность работы функции __str__"""
        self.assertEqual('Контракт №1 от 02.05.2019', self.contract.__str__())

    def test_contract_delete_cache_on_save_or_delete_instance(self):
        """Проверяет что кэш реестра удаляeтся при сохранении контракта"""
        key_reestr = f'template.cache.reestr.{get_md5_int_hash(2019)}'
        self.contract.save()
        self.assertFalse(cache.get(key_reestr))
        client = Client()
        client.login(username='test_user', password='123')
        client.get('/reestr/')
        client.get('/limit/')
        self.assertTrue(cache.get(key_reestr))
        self.contract.delete()
        self.assertFalse(cache.get(key_reestr))

    def test_contract_get_economy_with_tender_and_one_price(self):
        """
        Проверяет правильность работы фукции get_economy если создана
        одна цена контракта и одна начальная цена
        """
        self.make_tender()
        self.tender.startprice_set.create(
            limit=self.limit_money,
            subdivision=self.subdivision,
            money=5000
        )
        contract_price = self.tender.startprice_set.first().contractprice
        contract_price.money = 4000
        contract_price.save()

        self.assertEqual(self.contract.get_economy(), 1000)

    def test_contract_get_economy_with_tender_and_two_prices(self):
        """
        Проверяет правильность работы фукции get_economy если созданы
        две цены контракта и две начальные цены
        """
        self.make_tender()
        self.tender.startprice_set.create(
            limit=self.limit_money,
            subdivision=self.subdivision,
            money=5000
        )
        self.tender.startprice_set.create(
            limit=self.limit_money,
            subdivision=self.subdivision,
            money=5000
        )
        for start_price in self.tender.startprice_set.all():
            contract_price = start_price.contractprice
            contract_price.money = 4000
            contract_price.save()

        self.assertEqual(self.contract.get_economy(), 2000)

    def test_contract_get_economy_without_tender(self):
        """
        Проверяет правильность работы фукции get_economy, если
        tender и start_price отсутствуют
        """
        self.contract.contractprice_set.create(
            limit=self.limit_money,
            subdivision=self.subdivision,
            money=4000
        )
        self.assertEqual(self.contract.get_economy(), 0)

    def test_contract_get_economy_with_tender_and_cp_changed_positive(self):
        """
        Проверяет правильность работы фукции get_economy,
        после увеличения цены контракта
        """
        self.make_tender()
        self.tender.startprice_set.create(
            limit=self.limit_money,
            subdivision=self.subdivision,
            money=5000
        )
        self.tender.startprice_set.create(
            limit=self.limit_money,
            subdivision=self.subdivision,
            money=5000
        )
        for start_price in self.tender.startprice_set.all():
            contract_price = start_price.contractprice
            contract_price.money = 4000
            contract_price.save()

        for price in self.contract.contractprice_set.all():
            price.money += 500
            price.save()

        self.assertEqual(self.contract.get_economy(), 1000)

    def test_contract_get_economy_with_tender_and_cp_changed_negative(self):
        """
        Проверяет правильность работы фукции get_economy,
        после уменьшения цены контракта
        """
        self.make_tender()
        self.tender.startprice_set.create(
            limit=self.limit_money,
            subdivision=self.subdivision,
            money=5000
        )
        self.tender.startprice_set.create(
            limit=self.limit_money,
            subdivision=self.subdivision,
            money=5000
        )
        for start_price in self.tender.startprice_set.all():
            contract_price = start_price.contractprice
            contract_price.money = 4000
            contract_price.save()

        for price in self.contract.contractprice_set.all():
            price.money -= 500
            price.save()

        self.assertEqual(self.contract.get_economy(), 3000)

    def test_contract_get_economy_with_tender_and_sp_changed_positive(self):
        """
        Проверяет правильность работы фукции get_economy,
        после увеличении начальной цены
        """
        self.make_tender()
        self.tender.startprice_set.create(
            limit=self.limit_money,
            subdivision=self.subdivision,
            money=5000
        )
        self.tender.startprice_set.create(
            limit=self.limit_money,
            subdivision=self.subdivision,
            money=5000
        )
        for start_price in self.tender.startprice_set.all():
            contract_price = start_price.contractprice
            contract_price.money = 4000
            contract_price.save()

        for price in self.tender.startprice_set.all():
            price.money += 500
            price.save()

        self.assertEqual(self.contract.get_economy(), 3000)

    def test_contract_get_economy_with_tender_and_sp_changed_negative(self):
        """
        Проверяет правильность работы фукции get_economy,
        после уменьшения начальной цены
        """
        self.make_tender()
        self.tender.startprice_set.create(
            limit=self.limit_money,
            subdivision=self.subdivision,
            money=5000
        )
        self.tender.startprice_set.create(
            limit=self.limit_money,
            subdivision=self.subdivision,
            money=5000
        )
        for start_price in self.tender.startprice_set.all():
            contract_price = start_price.contractprice
            contract_price.money = 4000
            contract_price.save()

        for price in self.tender.startprice_set.all():
            price.money -= 500
            price.save()

        self.assertEqual(self.contract.get_economy(), 1000)
