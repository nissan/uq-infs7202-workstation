from django.contrib import admin
from .models import Subscription, Revenue

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscription_type', 'status', 'start_date', 'end_date', 'price')
    list_filter = ('subscription_type', 'status')
    search_fields = ('user__username', 'user__email')
    date_hierarchy = 'start_date'

@admin.register(Revenue)
class RevenueAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'amount', 'date', 'payment_method', 'transaction_id')
    list_filter = ('payment_method', 'date')
    search_fields = ('transaction_id', 'subscription__user__username')
    date_hierarchy = 'date'
