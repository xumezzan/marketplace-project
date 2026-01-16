import time
from django.conf import settings
from .models import PaymeTransaction
from marketplace.models import Deal

class PaymeErrors:
    TRANS_NOT_FOUND = -31003
    INVALID_AMOUNT = -31001
    ORDER_NOT_FOUND = -31050
    CANT_PERFORM_TRANS = -31008
    TRANS_STATE_BAD = -31008

class PaymeService:
    def check_perform_transaction(self, params):
        """
        Проверка возможности проведения транзакции.
        """
        account = params.get('account', {})
        amount = params.get('amount')
        deal_id = account.get('deal_id')

        # 1. Проверка суммы
        if not amount or amount <= 0:
            return {'error': {'code': PaymeErrors.INVALID_AMOUNT, 'message': 'Неверная сумма'}}

        # 2. Проверка заказа (сделки)
        try:
            deal = Deal.objects.get(id=deal_id)
        except Deal.DoesNotExist:
            return {'error': {'code': PaymeErrors.ORDER_NOT_FOUND, 'message': 'Сделка не найдена'}}

        # 3. Проверка суммы сделки (в тийинах)
        # Предполагаем, что deal.amount в сумах, переводим в тийины (* 100)
        expected_amount = int(deal.final_price * 100)
        if amount != expected_amount:
             return {'error': {'code': PaymeErrors.INVALID_AMOUNT, 'message': 'Сумма не совпадает'}}

        # 4. Проверка статуса сделки (можно ли оплачивать)
        if deal.status != Deal.Status.PENDING: # Или другой статус, когда можно платить
             return {'error': {'code': PaymeErrors.CANT_PERFORM_TRANS, 'message': 'Сделка не в статусе оплаты'}}

        return {'result': {'allow': True}}

    def create_transaction(self, params):
        """
        Создание транзакции.
        """
        payme_id = params.get('id')
        time_ms = params.get('time')
        amount = params.get('amount')
        account = params.get('account', {})
        deal_id = account.get('deal_id')

        # Проверяем, есть ли уже такая транзакция
        try:
            trans = PaymeTransaction.objects.get(payme_id=payme_id)
            # Если есть, проверяем состояние
            if trans.state != 1:
                return {'error': {'code': PaymeErrors.CANT_PERFORM_TRANS, 'message': 'Транзакция уже существует и не в ожидании'}}
            
            # Проверяем тайм-аут (43200000 мс = 12 часов)
            if (int(time.time() * 1000) - trans.create_time) > 43200000:
                trans.state = -1 # Отменена по таймауту
                trans.reason = 4
                trans.save()
                return {'error': {'code': PaymeErrors.CANT_PERFORM_TRANS, 'message': 'Тайм-аут транзакции'}}
            
            return {
                'result': {
                    'create_time': trans.create_time,
                    'transaction': str(trans.id),
                    'state': trans.state
                }
            }
        except PaymeTransaction.DoesNotExist:
            # Создаем новую
            # Сначала проверим возможность (check_perform_transaction логика)
            check_res = self.check_perform_transaction(params)
            if 'error' in check_res:
                return check_res

            deal = Deal.objects.get(id=deal_id)
            
            trans = PaymeTransaction.objects.create(
                payme_id=payme_id,
                time=time_ms,
                amount=amount,
                account=account,
                create_time=int(time.time() * 1000),
                state=1, # Ожидание
                deal=deal
            )
            
            return {
                'result': {
                    'create_time': trans.create_time,
                    'transaction': str(trans.id),
                    'state': trans.state
                }
            }

    def perform_transaction(self, params):
        """
        Проведение транзакции (списание средств).
        """
        payme_id = params.get('id')
        
        try:
            trans = PaymeTransaction.objects.get(payme_id=payme_id)
        except PaymeTransaction.DoesNotExist:
             return {'error': {'code': PaymeErrors.TRANS_NOT_FOUND, 'message': 'Транзакция не найдена'}}
        
        if trans.state == 1:
            # Проверяем тайм-аут
            if (int(time.time() * 1000) - trans.create_time) > 43200000:
                trans.state = -1
                trans.reason = 4
                trans.save()
                return {'error': {'code': PaymeErrors.CANT_PERFORM_TRANS, 'message': 'Тайм-аут транзакции'}}
            
            # Выполняем
            trans.state = 2
            trans.perform_time = int(time.time() * 1000)
            trans.save()
            
            # !!! ВАЖНО: Обновляем статус сделки !!!
            # IN_PROGRESS означает "Оплачено, работа идет"
            trans.deal.status = Deal.Status.IN_PROGRESS 
            trans.deal.save()
            
            return {
                'result': {
                    'transaction': str(trans.id),
                    'perform_time': trans.perform_time,
                    'state': trans.state
                }
            }
        elif trans.state == 2:
            # Уже выполнена, возвращаем результат
            return {
                'result': {
                    'transaction': str(trans.id),
                    'perform_time': trans.perform_time,
                    'state': trans.state
                }
            }
        else:
             return {'error': {'code': PaymeErrors.TRANS_STATE_BAD, 'message': 'Неверный статус транзакции'}}

    def cancel_transaction(self, params):
        """
        Отмена транзакции.
        """
        payme_id = params.get('id')
        reason = params.get('reason')
        
        try:
            trans = PaymeTransaction.objects.get(payme_id=payme_id)
        except PaymeTransaction.DoesNotExist:
             return {'error': {'code': PaymeErrors.TRANS_NOT_FOUND, 'message': 'Транзакция не найдена'}}

        if trans.state == 1:
            trans.state = -1
            trans.cancel_time = int(time.time() * 1000)
            trans.reason = reason
            trans.save()
            return {
                'result': {
                    'transaction': str(trans.id),
                    'cancel_time': trans.cancel_time,
                    'state': trans.state
                }
            }
        elif trans.state == 2:
            # Если уже выполнена, можно ли отменить? (обычно Refund)
            # Для простоты пока разрешим отмену и возврат средств (логика возврата сложнее)
            trans.state = -2
            trans.cancel_time = int(time.time() * 1000)
            trans.reason = reason
            trans.save()
            
            # Откатываем сделку?
            trans.deal.status = Deal.Status.CANCELED
            trans.deal.save()
            
            return {
                'result': {
                    'transaction': str(trans.id),
                    'cancel_time': trans.cancel_time,
                    'state': trans.state
                }
            }
        else:
            # Уже отменена
            return {
                'result': {
                    'transaction': str(trans.id),
                    'cancel_time': trans.cancel_time,
                    'state': trans.state
                }
            }

    def check_transaction(self, params):
        """
        Проверка статуса транзакции.
        """
        payme_id = params.get('id')
        
        try:
            trans = PaymeTransaction.objects.get(payme_id=payme_id)
            return {
                'result': {
                    'create_time': trans.create_time,
                    'perform_time': trans.perform_time,
                    'cancel_time': trans.cancel_time,
                    'transaction': str(trans.id),
                    'state': trans.state,
                    'reason': trans.reason
                }
            }
        except PaymeTransaction.DoesNotExist:
             return {'error': {'code': PaymeErrors.TRANS_NOT_FOUND, 'message': 'Транзакция не найдена'}}
