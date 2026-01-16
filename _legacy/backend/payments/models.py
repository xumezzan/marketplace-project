from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal

class Wallet(models.Model):
    """
    Кошелек пользователя.
    Создается автоматически для каждого пользователя (через сигналы).
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet',
        verbose_name='пользователь'
    )
    balance = models.DecimalField(
        'баланс',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Текущий баланс пользователя"
    )
    created_at = models.DateTimeField('дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('дата обновления', auto_now=True)

    class Meta:
        db_table = 'wallets'
        verbose_name = 'кошелек'
        verbose_name_plural = 'кошельки'

    def __str__(self):
        return f"Кошелек {self.user.username} ({self.balance})"

    def deposit(self, amount):
        """Пополнение кошелька."""
        if amount <= 0:
            raise ValueError("Сумма должна быть положительной")
        self.balance += amount
        self.save()
        Transaction.objects.create(
            wallet=self,
            amount=amount,
            type=Transaction.Type.DEPOSIT,
            description="Пополнение счета"
        )

    def withdraw(self, amount):
        """Списание средств (вывод)."""
        if amount <= 0:
            raise ValueError("Сумма должна быть положительной")
        if self.balance < amount:
            raise ValueError("Недостаточно средств")
        self.balance -= amount
        self.save()
        Transaction.objects.create(
            wallet=self,
            amount=-amount,
            type=Transaction.Type.WITHDRAWAL,
            description="Вывод средств"
        )

    def pay_commission(self, amount, description="Комиссия платформы"):
        """Оплата комиссии."""
        if amount <= 0:
            raise ValueError("Сумма должна быть положительной")
        # Разрешаем уходить в минус или нет?
        # По ТЗ решили блокировать, если недостаточно средств.
        if self.balance < amount:
            raise ValueError("Недостаточно средств для оплаты комиссии")
        
        self.balance -= amount
        self.save()
        Transaction.objects.create(
            wallet=self,
            amount=-amount,
            type=Transaction.Type.FEE,
            description=description
        )


class Transaction(models.Model):
    """
    История транзакций.
    """
    class Type(models.TextChoices):
        DEPOSIT = 'deposit', 'Пополнение'
        WITHDRAWAL = 'withdrawal', 'Вывод'
        FEE = 'fee', 'Комиссия'
        REFUND = 'refund', 'Возврат'

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name='кошелек'
    )
    amount = models.DecimalField(
        'сумма',
        max_digits=10,
        decimal_places=2,
        help_text="Сумма транзакции (положительная для пополнения, отрицательная для списания)"
    )
    type = models.CharField(
        'тип',
        max_length=20,
        choices=Type.choices,
        default=Type.FEE
    )
    description = models.CharField(
        'описание',
        max_length=255,
        blank=True
    )
    created_at = models.DateTimeField('дата создания', auto_now_add=True)

    class Meta:
        db_table = 'transactions'
        verbose_name = 'транзакция'
        verbose_name_plural = 'транзакции'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_type_display()}: {self.amount} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class PaymeTransaction(models.Model):
    """
    Транзакция Payme.
    """
    payme_id = models.CharField('ID транзакции в Payme', max_length=255)
    time = models.BigIntegerField('время создания транзакции в Payme')
    amount = models.BigIntegerField('сумма (в тийинах)')
    account = models.JSONField('параметры аккаунта', null=True, blank=True)
    create_time = models.BigIntegerField('время добавления транзакции в БД', default=0)
    perform_time = models.BigIntegerField('время проведения транзакции', default=0)
    cancel_time = models.BigIntegerField('время отмены транзакции', default=0)
    state = models.IntegerField('состояние транзакции')
    reason = models.IntegerField('причина отмены', null=True, blank=True)
    
    # Связь со сделкой (если оплата идет за сделку)
    deal = models.ForeignKey(
        'marketplace.Deal',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payme_transactions',
        verbose_name='сделка'
    )

    created_at = models.DateTimeField('дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'транзакция Payme'
        verbose_name_plural = 'транзакции Payme'

    def __str__(self):
        return f"Payme {self.payme_id} - {self.amount}"
