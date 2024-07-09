from django.urls import path
# from django_paypal_integrations import views
from .views import create_order,capture_order,complete_order




urlpatterns = [
    path('create-order', create_order.as_view(), name='create_order'),
    path('capture-order', capture_order.as_view(), name='capture_order'),
    path('complete-order', complete_order.as_view(), name='complete_order'),
]
