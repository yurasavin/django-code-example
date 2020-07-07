from django.test import TestCase

from tickets.models import Ticket
from tenders.models import Tender
from .models import StartPrice


# class TenderStartPriceTest(TestCase):
#     """
#     Тестирует, что при создании StartPrice,
#     обновляется поле price у связанного Tender
#     """
#     def test_start_price_creating(self):
#         '''
#         При создании связанного StartPrice должен обновляться
#         аттрибут инстанса price
#         '''
#         ticket = Ticket(name='test')
#         ticket.save()
#         tender = Tender(ticket=ticket)
#         tender.save()
#         start_price = StartPrice(money=100, tender=tender)
#         start_price.save()
#         self.assertEqual(tender.price, start_price)
