from django.urls import path
from .views import ChooseSpecialistView, ContactShareView
from .commission_views import GenerateCodeView, ConfirmPaymentView

urlpatterns = [
    path('choose/', ChooseSpecialistView.as_view(), name='deal-choose-specialist'),
    path('<int:pk>/contacts/', ContactShareView.as_view(), name='deal-contacts'),
    # Commission
    path('<int:pk>/generate_code/', GenerateCodeView.as_view(), name='deal-generate-code'),
    path('<int:pk>/confirm_first_payment/', ConfirmPaymentView.as_view(), name='deal-confirm-payment'),
]
