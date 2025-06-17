# filepath: apps/payments/urls.py
"""
URLs para la app Payments.
"""
from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Payment selection and processing
    path('', views.PaymentView.as_view(), name='process'),
    path('method/', views.PaymentMethodView.as_view(), name='method'),
    
    # Stripe payments
    path('stripe/create-intent/', views.StripeCreateIntentView.as_view(), name='stripe_create_intent'),
    path('stripe/confirm/', views.StripeConfirmView.as_view(), name='stripe_confirm'),
    path('stripe/webhook/', views.StripeWebhookView.as_view(), name='stripe_webhook'),
    
    # PayPal payments
    path('paypal/create/', views.PayPalCreateView.as_view(), name='paypal_create'),
    path('paypal/execute/', views.PayPalExecuteView.as_view(), name='paypal_execute'),
    path('paypal/cancel/', views.PayPalCancelView.as_view(), name='paypal_cancel'),
    path('paypal/webhook/', views.PayPalWebhookView.as_view(), name='paypal_webhook'),
    
    # Payment status pages
    path('success/', views.PaymentSuccessView.as_view(), name='success'),
    path('error/', views.PaymentErrorView.as_view(), name='error'),
    path('cancelled/', views.PaymentCancelledView.as_view(), name='cancelled'),
]
