from datetime import datetime, time
from decimal import Decimal
import json
from django.utils import timezone
from .models import *

from django.contrib.auth import get_user_model


def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except KeyError:
        cart = {}

    print('Cart:', cart)

    items = []
    order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
    cart_items_count = order['get_cart_items']

    for product_id, item_data in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            quantity = item_data["quantity"]
            item_total = product.price * quantity

            cart_items_count += quantity
            order['get_cart_total'] += item_total
            order['get_cart_items'] += quantity

            item = {
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'imageURL': product.imageURL,
                },
                'quantity': quantity,
                'get_total': item_total
            }
            items.append(item)

        except Product.DoesNotExist:
            # Handle the case when a product with the given ID is not found
            pass

    return {'items': items, 'order': order, 'cart_items_count': cart_items_count}

def cartData(request):

    items = [] 
    order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
    cartItems = order['get_cart_items']

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False,)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        
    return {'items': items, 'order': order, 'cartItems': cartItems}

