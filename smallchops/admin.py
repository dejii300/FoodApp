from django.contrib import admin
from .models import *


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

class OrderAdmin(admin.ModelAdmin):
    list_display = ['customer', 'date_ordered', 'status', 'complete']
    inlines = [OrderItemInline]

# Register your models here.
admin.site.register(Customer)
admin.site.register(Event)
admin.site.register(Rating)
admin.site.register(Delivery)
admin.site.register(Order, OrderAdmin)
admin.site.register(ShippingAddress)
admin.site.register(Product)
admin.site.register(EvtProduct)
admin.site.register(EventItem)
admin.site.register(Category)
admin.site.register(MediaItem)
admin.site.register(OrderItem)
admin.site.register(Like)
admin.site.register(FoodVideo)
admin.site.register(Comment)
admin.site.register(UserActivity)
