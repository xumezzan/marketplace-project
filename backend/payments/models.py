from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

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
        default=0.00,
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
