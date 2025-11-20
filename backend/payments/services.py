from django.db import transaction
from django.conf import settings
from decimal import Decimal
from marketplace.models import Deal, Escrow
from payments.models import Wallet, Transaction

class PaymentService:
    """
    Сервис для обработки платежей и транзакций.
    """
    
    COMMISSION_RATE = Decimal('0.10')  # 10% комиссия платформы

    @staticmethod
    def process_payment(deal: Deal) -> bool:
        """
        Блокирует средства клиента для сделки (создает Escrow).
        
        Args:
            deal: Сделка, которую нужно оплатить
            
        Returns:
            bool: Успешно ли прошла оплата
        """
        try:
            client_wallet = deal.client.wallet
        except Wallet.DoesNotExist:
            return False

        amount = deal.final_price
        
        if client_wallet.balance < amount:
            return False
            
        with transaction.atomic():
            # Списываем средства у клиента
            client_wallet.withdraw(amount)
            
            # Создаем или обновляем Escrow
            escrow, created = Escrow.objects.get_or_create(deal=deal, defaults={'amount': amount})
            if not created:
                escrow.amount = amount
                escrow.save()
            
            escrow.status = Escrow.Status.RESERVED
            escrow.save()
            
            # Обновляем статус сделки
            deal.status = Deal.Status.IN_PROGRESS
            deal.save()
            
            return True

    @staticmethod
    def release_payment(deal: Deal) -> bool:
        """
        Переводит средства исполнителю за вычетом комиссии.
        
        Args:
            deal: Сделка, которую нужно завершить
            
        Returns:
            bool: Успешно ли переведены средства
        """
        try:
            escrow = deal.escrow
            specialist_wallet = deal.specialist.wallet
        except (Escrow.DoesNotExist, Wallet.DoesNotExist):
            return False
            
        if escrow.status != Escrow.Status.RESERVED:
            return False
            
        amount = escrow.amount
        commission = amount * PaymentService.COMMISSION_RATE
        payout = amount - commission
        
        with transaction.atomic():
            # Пополняем кошелек специалиста
            specialist_wallet.deposit(payout)
            
            # Логируем комиссию (можно перевести на системный кошелек, если он есть)
            # Пока просто создаем запись о комиссии в транзакциях специалиста (или отдельной таблице)
            # В текущей модели Transaction привязана к Wallet. 
            # Можно создать транзакцию "Fee" для специалиста, но деньги уже вычтены.
            # Лучше просто зачислить "чистую" сумму, а комиссию учесть в Escrow или отдельной записи.
            
            # Обновляем Escrow
            escrow.status = Escrow.Status.RELEASED
            escrow.save()
            
            # Обновляем статус сделки
            deal.status = Deal.Status.COMPLETED
            deal.save()
            
            return True

    @staticmethod
    def refund_payment(deal: Deal) -> bool:
        """
        Возвращает средства клиенту.
        
        Args:
            deal: Сделка, которую нужно отменить
            
        Returns:
            bool: Успешно ли возвращены средства
        """
        try:
            escrow = deal.escrow
            client_wallet = deal.client.wallet
        except (Escrow.DoesNotExist, Wallet.DoesNotExist):
            return False
            
        if escrow.status != Escrow.Status.RESERVED:
            return False
            
        amount = escrow.amount
        
        with transaction.atomic():
            # Возвращаем средства клиенту
            client_wallet.deposit(amount)
            
            # Обновляем Escrow
            escrow.status = Escrow.Status.REFUNDED
            escrow.save()
            
            # Обновляем статус сделки
            deal.status = Deal.Status.CANCELED
            deal.save()
            
            return True
