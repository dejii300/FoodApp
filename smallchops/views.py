from django.db.models import Sum, F
import decimal
from django.utils import timezone
from venv import logger
from django.shortcuts import get_object_or_404, render, redirect
from django.http import Http404, HttpResponse, JsonResponse
from .models import *
from .forms import *
from django.forms import inlineformset_factory, modelformset_factory
from .filters import OrderFilter
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_users, admin_only
from django.contrib.auth.models import Group
from .utils import *
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView
import json
from django.contrib.auth.forms import PasswordChangeForm
import datetime
from datetime import date, datetime as datetime_module, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
import logging
from django.views.decorators.http import require_GET
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponseBadRequest
from django.core.paginator import Paginator
from django.contrib.auth.forms import PasswordResetForm

@csrf_exempt
def extract_keywords(request):
    text = request.POST.get('text')
    return JsonResponse(text)

#CUSOMER


def Index(request):
    selected_date = timezone.now().date()
    data = cartData(request)
    cartItems = data['cartItems']
    items = data['items']
    
    active_users = None 
    if request.user.is_authenticated:
        active_users = UserActivity.objects.create(user=request.user.customer, timestamp=selected_date, activity_type='Page access')

    categories = Category.objects.all()
    comments = Comment.objects.filter(approved=True)
    form = CommentForm()

    context = {
        'comments': comments, 
        'cartItems': cartItems, 
        'items': items, 'categories': categories,
        'form':form,
        'active_users':active_users
        }

    return render(request, 'chops/index.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def ChopsView(request):
    data = cartData(request)
    cartItems = data['cartItems']
    items = data['items']
    
    categories = Category.objects.all()
    products = Product.objects.all().order_by('name')
    paginator = Paginator(products, 6) 

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for product in products:
        ratings = Rating.objects.filter(product=product)
        if ratings.exists():
            average_rating = sum(rating.rating for rating in ratings) / ratings.count()
            product.average_rating = average_rating
        else:
            product.average_rating = None

    context = {'products':products, 'categories':categories, 'items': items, 'cartItems':cartItems, 'page_obj': page_obj}
    return render(request, "chops/chops.html", context)



def search_suggestions(request):
    query = request.GET.get('query', '')
    if query:
        products = Product.objects.filter(Q(name__icontains=query))[:5] 
        videos = FoodVideo.objects.filter(title__icontains=query)[:5] 
        deliveries = Delivery.objects.filter(location__icontains=query)[:5] 
        evtproducts = EvtProduct.objects.filter(name__icontains=query)[:5]  
        
        product_suggestions = [product.name for product in products]
        video_suggestions = [ video.title for video in videos]
        delivery_suggestions = [delivery.location for delivery in deliveries]
        evtproduct_suggestions = [evtproduct.name for evtproduct in evtproducts]
        
        return JsonResponse({
            'product_suggestions': product_suggestions,
            'video_suggestions': video_suggestions,
            'delivery_suggestions': delivery_suggestions,
            'evtproduct_suggestions': evtproduct_suggestions
        })
    else:
        return JsonResponse({'suggestions': []})
    

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def product_category(request, category):

    data = cartData(request)
    cartItems = data['cartItems']
    items = data['items']
    categories = Category.objects.all()
    products = Product.objects.filter(
        category__name__contains=category
    ).order_by('name') 
    paginator = Paginator(products, 5) 

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for product in products:
        ratings = Rating.objects.filter(product=product)
        if ratings.exists():
            average_rating = sum(rating.rating for rating in ratings) / ratings.count()
            product.average_rating = average_rating
        else:
            product.average_rating = None 
    context = {
        "Category": category,
        "products": products,
        'categories': categories,
        'cartItems': cartItems,
        'items': items,
        'page_obj': page_obj
    }
    return render(request, "chops/products_category.html", context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def ChopsDetail(request, product_id):
    categories = Category.objects.all()
    product = Product.objects.get(pk=product_id)
    ratings = Rating.objects.filter(product=product).select_related('customer')
    data = cartData(request)
    cartItems = data['cartItems']
    items = data['items']  
    print('ratings:', ratings)
    if ratings.exists():
        average_rating = sum(rating.rating for rating in ratings) / ratings.count()
    else:
        average_rating = None

    

    context = {'items': items, 'product':product,  'cartItems': cartItems, 'categories': categories, 'average_rating': average_rating, 'ratings': ratings}
    return render(request, 'chops/chops_detail.html',  context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def rate_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    user = request.user.customer
    existing_rating = Rating.objects.filter(product=product, customer=user).first()

    if request.method == 'POST':
        rating_value = request.POST.get('val')
        if existing_rating:
            # Update existing rating
            existing_rating.rating = rating_value
            existing_rating.save()
        else:
            # Create new rating
            rating_new = Rating.objects.create(product=product, customer=user, rating=rating_value)
            rating_new.save()

        average_rating = Rating.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']    
        Rating.objects.get(product=product, customer=request.user.customer, rating=rating_value) 

        return JsonResponse({'success':'true', 'rating': rating_value, 'average_rating': average_rating}, safe=False)
    return JsonResponse({'success':'false'})



@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def cart(request):
    categories = Category.objects.all()
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']   

    context = {'items': items, 'order': order, 'cartItems': cartItems, 'categories': categories }
    return render(request, "chops/cart.html", context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def updateItem(request):
    data = json.loads(request.body)
    productId = data.get('productId')
    action = data.get('action')
    quantity = data.get('quantity', 1)
    
    print('Before Processing - productId:', productId)
    print('Before Processing - action:', action)
    print('Before Processing - quantity:', quantity)

    if not productId or action not in ['add', 'delete']:
        return JsonResponse({'error': 'Invalid request'}, status=400)

    try:
        customer = request.user.customer
        print('Customer ID:', customer.id)

        product = Product.objects.get(id=productId)
        print('Product Name:', product.name) 

        order, created_order = Order.objects.get_or_create(customer=customer, complete=False)
        orderItem, created_order_item= OrderItem.objects.get_or_create(order=order, product=product)

        print('OrderItem ID:', orderItem.id)  # Debug line
        print('OrderItem Quantity (before):', orderItem.quantity)

        if action == 'add':
            new_quantity = max(0, int(quantity))
            orderItem.quantity = new_quantity
            orderItem.save()

        elif action == 'delete':
            orderItem.delete()
            cartItems = order.get_cart_items
            items = order.get_cart_items
            cartTotal = order.get_cart_total
            return JsonResponse({'message': 'Item deleted successfully', 'cartItems': cartItems, 'items':items, 'cartTotal':cartTotal}, status=200)
    
        cartItems = order.get_cart_items
        items = order.get_cart_items
        cartTotal = order.get_cart_total
        itemTotal = orderItem.get_total
        print('OrderItem Quantity (after):', orderItem.quantity)
        print('cart item:', cartItems)

        return JsonResponse({'message': f'Item {action}ed successfully', 'cartItems': cartItems, 'items':items, 'cartTotal':cartTotal, 'itemTotal':itemTotal}, status=200)

    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=400)

    except Exception as e:
        print('Error:', str(e))  
        return JsonResponse({'error': str(e)}, status=500)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def shipping_view(request):
    data = cartData(request)
    cartItems = data['cartItems']
    items = data['items']
    
    try:
        # Attempt to retrieve the incomplete orders associated with the customer
        orders = Order.objects.filter(customer=request.user.customer, complete=False)

        # Select one of the incomplete orders (e.g., the first one)
        order = orders.first()

        # If no incomplete orders exist, create a new one
        if order is None:
            order = Order.objects.create(customer=request.user.customer, complete=False)

    except ObjectDoesNotExist:
        # If no incomplete order exists, create a new one
        order = Order.objects.create(customer=request.user.customer, complete=False)


    if request.method == 'POST':
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
           
            # Save the shipping address and update the order
            shippingaddress = form.save()
            order.shippingaddress = shippingaddress
            order.save()

            return redirect('checkout')

    else:
        form = ShippingAddressForm()

    context = {'form': form, 'cartItems': cartItems, 'items': items}
    return render(request, 'chops/shipping.html', context)

       
@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def checkout(request):
    categories = Category.objects.all()
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    if not items:
        # Redirect or handle the case where the cart is empty
        return redirect('chops')

    try:
        # Retrieve the delivery price associated with the customer's order
        delivery_price = 0
        if order.shippingaddress:
            # Assuming there's a direct relationship between ShippingAddress and Delivery
            delivery = order.shippingaddress.delivery
            delivery_price = delivery.price if delivery else 0  # Set a default if no delivery is found
    except ShippingAddress.DoesNotExist:
        # Handle the case where the shipping address is not found
        delivery_price = 0
    # Placeholder for updated_total; replace it with the actual calculation
    finaltotal = int(order.get_cart_total + delivery_price)
    print(f"finaltotal : {finaltotal}")
    try:
        # Attempt to retrieve the incomplete orders associated with the customer
        payments = Order.objects.filter(customer=request.user.customer, complete=False)

        # Select one of the incomplete orders (e.g., the first one)
        payment = payments.first()

        # If no incomplete orders exist, create a new one
        if payment is None:
            payment = Order.objects.create(customer=request.user.customer, complete=False)

    except ObjectDoesNotExist:
        # If no incomplete order exists, create a new one
        payment = Order.objects.create(customer=request.user.customer, complete=False)

    
    payment.amount = finaltotal
    payment.save()
    pk = settings.PAYSTACK_PUBLIC_KEY
    context = {'items': items, 'order': order,
                'cartItems': cartItems, 
                'delivery_price': delivery_price,
                'finaltotal': finaltotal,
                'categories': categories,
                'payment': payment,
                'paystack_pub_key':pk,
                'amount_value':payment.amount_value()
    }

    return render(request, "chops/checkout.html", context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def verify_order_payment(request, ref):
    payment = Order.objects.get(ref=ref)
    verified = payment.verify_payment()
    if verified:
        
        
        payment.complete = True
        payment.date_ordered = timezone.localtime(timezone.now())
        payment.save()
        context = {
                   'payment':payment
        }
        return render(request, 'chops/checkout_success.html', context)
    else:
        messages.warning(request, 'Sorry, your order was not processed. Please contact Daily Food support')
        return redirect('chops')




@unauthenticated_user
def registerPage(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid(): 
            email = form.cleaned_data.get('email')
            if User.objects.filter(email=email).exists():
                messages.error(request, 'This email address is already in use.', extra_tags='email')
            else:    
                user = form.save(commit=False)
                user.is_active = False  # User is not active until email is verified
                user.save()
                
                # Generate token for email verification
                token = default_token_generator.make_token(user)

                # Send verification email
                current_site = get_current_site(request)
                mail_subject = 'Activate your account'
                message = render_to_string('account/verification_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': token,
                })
                to_email = form.cleaned_data.get('email')
                email = EmailMessage(mail_subject, message, to=[to_email])
                email.send()

                messages.success(request, f'Please confirm your email address to complete the registration')
                return redirect('login')
    else:
        
        form = CreateUserForm() #creates an empty form
    return render(request, 'account/register.html', {'form': form})


def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()  # Decoding bytes and then converting to string
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        # Create a Customer object associated with the user
        Customer.objects.create(
            user=user,
            username=user.username,
            email=user.email
        )

        # Add the user to the 'customer' group
        group = Group.objects.get(name='customer')
        user.groups.add(group)
        
        user.save()

       

        messages.success(request, 'Your account has been successfully activated. You can now log in.')
        return redirect('login') 


       

    else:
        return HttpResponseBadRequest('Activation link is invalid!')
    

class CustomPasswordResetView(PasswordResetView):
    def form_valid(self, form):
        # Check if the provided email exists in the system
        email = form.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            messages.error(self.request, "This email address does not exist in our system.")
            return self.render_to_response(self.get_context_data(form=form))
        # If the email exists, proceed with the password reset process
        return super().form_valid(form)
    
@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_staff:
                # Admin user
                return redirect('home')
            elif user.last_login is None:
                # First-time user or last login was within the last minute
                return redirect('edit_profile')
            else:
                # For subsequent logins, redirect to index
                return redirect('index')
        else:
            messages.info(request, 'Username or password is incorrect')

    context = {}
    return render(request, 'account/login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('index')

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def ProfilePage(request):
    customer = request.user.customer
    
    context = {'customer':customer}
    
    return render(request, 'account/profile.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def edit_profile(request):
    customer = request.user.customer
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            if 'clear_profile_pic' in request.POST:
                form.instance.profile_pic = 'images/profile_pics/profile1.png'
                print(form.cleaned_data)
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'account/edit_profile.html', {'form': form, 'customer': customer})

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def userOrder(request):
    categories = Category.objects.all()
    data = cartData(request)
    cartItems = data['cartItems']
    items = data['items']
    orders = request.user.customer.order_set.all().order_by('-date_ordered')
    events = request.user.customer.event_set.all().order_by('-date')
    paginator = Paginator(orders, 5) 

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
   
    processing = orders.filter(status='Processing', complete=True).count()
    out_for_delivery = orders.filter(status='Out_for_delivery', complete=True).count()
    delivered = orders.filter(status='Delivered', complete=True).count()
    
    print('ORDERS:', orders)
    context = {
        'orders': orders, 'out_for_delivery': out_for_delivery, 'delivered': delivered,
        'processing': processing, 'cartItems': cartItems, 'items': items, 'categories':categories,
        'events': events, 'page_obj': page_obj
        }
    return render(request, 'chops/user-order.html', context)   

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def event_form(request):
    evtproducts = EvtProduct.objects.all().order_by('name')
    paginator = Paginator(evtproducts, 5)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


         
    if request.method == 'POST':

        
        print(request.POST) 
        
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.customer = request.user.customer
            event.save()
            form.save()
            logger.info(f"Event {event.id} saved successfully.")
            return redirect('review_page', event_id=event.id)
        else:
            print(form.errors)
    else:
        form = EventForm()

    return render(request, 'chops/event_form.html', {'form': form, 'evtproducts': evtproducts, 'page_obj': page_obj})
    
@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def Event_review_page(request, event_id):
    event = Event.objects.get(id=event_id)
    EventItemFormSet = modelformset_factory(EventItem, fields=('chops', 'guest'), extra=0)
    
    if request.method == 'POST':
        formset = EventItemFormSet(request.POST, queryset=EventItem.objects.filter(event=event))
        if formset.is_valid():
            # Custom validation for 'guest' field
            for form in formset:
                guest = form.cleaned_data.get('guest', 0)
                if guest <= 0:
                    messages.error(request, "Guest must be a valid number greater than 0.")
                    return render(request, 'chops/event_review.html', {'event': event, 'formset': formset})

            formset.save()
            return redirect('checkout', event_id=event_id)
    else:
        formset = EventItemFormSet(queryset=EventItem.objects.filter(event=event))

    return render(request, 'chops/event_review.html', {'event': event, 'formset': formset})

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def Event_Checkout(request, event_id):
    event = Event.objects.get(id=event_id)
    event_items = EventItem.objects.filter(event=event)
    finaltotal = 0

    for item in event_items:
        item_total = item.guest * item.chops.price
        finaltotal += item_total
        item.total = item_total
        item.save()
    
    try:
        # Attempt to retrieve the incomplete orders associated with the customer
        payments = Event.objects.filter(customer=request.user.customer, paid=False)

        # Select one of the incomplete orders (e.g., the first one)
        payment = payments.first()

        # If no incomplete orders exist, create a new one
        if payment is None:
            payment = Event.objects.create(customer=request.user.customer, paid=False)

    except ObjectDoesNotExist:
        # If no incomplete order exists, create a new one
        payment = Order.objects.create(customer=request.user.customer, paid=False)
    payment.amount = finaltotal
    payment.save()
    pk = settings.PAYSTACK_PUBLIC_KEY
    
    context= {'event': event, 'event_items': event_items,
            'item_total': item_total, 'finaltotal': finaltotal,
            'payment': payment,
            'paystack_evnt_key':pk,
            'amount_value':payment.amount_value()
    }
    return render(request, 'chops/event_checkout.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def verify_event_payment(request, ref):
    payment = Event.objects.get(ref=ref)
    verified = payment.verify_payment()
    if verified:
        
        
        payment.paid = True
        payment.save()
        context = {
                   'payment':payment
        }
        return render(request, 'chops/event_checkout_success.html', context)
    else:
        messages.warning(request, 'Sorry, your event was not processed. Please contact Daily Food support')
        return redirect('event_form')  


@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def generate_transaction_id():
    # Placeholder function to generate a transaction ID
    import uuid
    return str(uuid.uuid4())

   

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')  # Change 'profile' to the desired redirect URL
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'account/change_password_template.html', {'form': form})

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def submit_comment(request):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.customer = request.user.customer 
            comment.save()
            return JsonResponse({'success': True, 'message': 'Feedback submitted successfully'})
    else:
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def FoodVideolist(request):
    videos = FoodVideo.objects.all().order_by('title') 
    paginator = Paginator(videos, 10) 

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'chops/foodvideo_list.html', {'videos': videos, 'page_obj': page_obj})

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def FoodVideo_detail(request, pk):
    video = get_object_or_404(FoodVideo, pk=pk)
    num_likes = video.liked.count()
    if request.user.is_authenticated:
        customer = request.user.customer
        if customer not in video.viewers.all():
            video.viewers.add(customer)
    return render(request, 'chops/video_detail.html', {'video': video,'num_likes': num_likes})

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def like_unlike_video(request):
    if request.method == "POST":
        customer = request.user
        video_id = request.POST.get('video_id')
        video_obj = get_object_or_404(FoodVideo, id=video_id)
        customer_obj, created = Customer.objects.get_or_create(user=customer)

        # Check if the customer has already liked the video
        if customer_obj in video_obj.liked.all():
            video_obj.liked.remove(customer_obj)
            like_value = 'Unlike'
        else:
            video_obj.liked.add(customer_obj)
            like_value = 'Like'

        # Update or create the Like object
        like, _ = Like.objects.get_or_create(user=customer_obj, video_id=video_id)
        like.value = like_value
        like.save()

        # Calculate the new like count
        new_like_count = video_obj.liked.count()

        # Return JSON response with the new like count
        return JsonResponse({'like_count': new_like_count})
    else:
        # Return error response for disallowed methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    

 

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def AboutUs(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    context = {'cartItems': cartItems, 'items': items, 'order':order }
    return render(request, 'chops/about-us.html', context)    


#ADMIN

@login_required(login_url='login')
@admin_only
def adminD(request):
    today = timezone.now().date()

    selected_date_str = request.GET.get('selected_date')

    if selected_date_str:
        # Parse the selected date from the input
        selected_date = datetime_module.strptime(selected_date_str, "%Y-%m-%d").date()
    else:
        # If no date is provided, use today's date
        selected_date = timezone.now().date()

    orders = Order.objects.filter(date_ordered__date=selected_date).order_by('-date_ordered')
    events = Event.objects.all().order_by('-date')
    customers = Customer.objects.all()
    total_orders = orders.filter(complete=True).count()
    processing = orders.filter(status='Processing', complete=True).count()
    out_for_delivery = orders.filter(status='Out_for_delivery').count()
    delivered = orders.filter(status='Delivered').count()
    
    context = {
        'orders': orders, 'customers': customers, 'total_orders': total_orders, 'delivered': delivered,
        'processing': processing,  'out_for_delivery': out_for_delivery,
        'events': events,
        'today': selected_date, 
        }

    return render(request, 'admin/admin_template.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def orders_by_date(request):
    selected_date_str = request.GET.get('date')
    
    if selected_date_str:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        orders = Order.objects.filter(date_ordered__date=selected_date)
    else:
        orders = Order.objects.all()

    context = {'orders': orders}
    return render(request, 'admin/admin_template.html', context) 

  

# @login_required(login_url='login')
# @allowed_users(allowed_roles=['admin'])
# def products(request):
#     products = Product.objects.all()
#     context = {
#         "products": products
#     }
#     return render(request, 'account/products.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def Events_details(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event_items = EventItem.objects.filter(event=event)

    formset = EventStatusForm( instance=event)
    

    if request.method =='POST':
        formset = EventStatusForm(request.POST, instance=event)
        if formset.is_valid():
            formset.save()
            return redirect('events_detail', event_id=event_id)
        
    context = {
        'event': event, 'event_items': event_items, 'formset':formset,
    }
    return render(request, 'admin/event_details.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customer(request, pk_test):
    customer = Customer.objects.get(id=pk_test)
    orders = customer.order_set.all()
    order_count = orders.count()
    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs
    context = {
        'customer': customer, 'orders': orders, 'order_count': order_count, 'myFilter': myFilter,
        
    }
    return render(request, 'account/customer.html', context) 


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def OrderDetail(request, order_id):
 
    order = get_object_or_404(Order, id=order_id)
    
    formset = OrderStatusForm( instance=order)
    

    if request.method =='POST':
        formset = OrderStatusForm(request.POST, instance=order)
        if formset.is_valid():
            formset.save()
            return redirect('update_order', order_id=order_id)
    context = {'formset': formset, 'order':order, }
    return render(request, 'admin/order_detail.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def product_list(request):
    products = Product.objects.all().order_by('name')
    paginator = Paginator(products, 10) 

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'admin/product_list.html', {'products': products, 'page_obj':page_obj})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'admin/product_detail.html', {'product': product})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'admin/product_form.html', {'form': form})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'admin/product_form.html', {'form': form})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'admin/product_confirm_delete.html', {'product': product})

#Event
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def evtproduct_list(request):
    evtproducts = EvtProduct.objects.all().order_by('name')
    paginator = Paginator(evtproducts, 10) 

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'admin/evtproduct_list.html', {'evtproducts': evtproducts, 'page_obj': page_obj})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def evtproduct_detail(request, pk):
    evtproduct = get_object_or_404(EvtProduct, pk=pk)
    return render(request, 'admin/evtproduct_detail.html', {'evtproduct': evtproduct})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def evtproduct_create(request):
    if request.method == 'POST':
        form = EvtProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('evtproduct_list')
    else:
        form = EvtProductForm()
    return render(request, 'admin/evtproduct_form.html', {'form': form})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def evtproduct_update(request, pk):
    evtproduct = get_object_or_404(EvtProduct, pk=pk)
    if request.method == 'POST':
        form = EvtProductForm(request.POST, request.FILES, instance=evtproduct)
        if form.is_valid():
            form.save()
            return redirect('evtproduct_detail',pk=pk)
    else:
        form = EvtProductForm(instance=evtproduct)
    return render(request, 'admin/evtproduct_form.html', {'form': form})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def evtproduct_delete(request, pk):
    evtproduct = get_object_or_404(EvtProduct, pk=pk)
    if request.method == 'POST':
        evtproduct.delete()
        return redirect('evtproduct_list')
    return render(request, 'admin/evtproduct_confirm_delete.html', {'evtproduct': evtproduct})



    

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def create_category(request, category_id=None):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('create_category')
    else:
        form = CategoryForm()

    # Retrieve all categories for display
    categories = Category.objects.all()

    if category_id:
        # If category_id is provided, it means the user wants to delete an existing category
        if request.GET.get('delete') == 'true':
            category = get_object_or_404(Category, id=category_id)
            category.delete()
            return redirect('create_category')
        else:
            raise Http404("Invalid request")

    return render(request, 'admin/create_category.html', {'form': form, 'categories': categories})


    
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def view_comments(request):
    comments = Comment.objects.filter(approved=False).order_by('content')
    paginator = Paginator(comments, 5) 

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'admin/view_comments.html', {'comments': comments, 'page_obj': page_obj})


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def approve_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    comment.approved = True
    comment.save()
    return redirect('view_comments')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    comment.delete()
    return redirect('view_comments')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def delivery_list(request):
    deliveries = Delivery.objects.all().order_by('location')
    paginator = Paginator(deliveries, 10) 

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'admin/delivery_list.html', {'deliveries': deliveries, 'page_obj': page_obj})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def delivery_create(request):
    if request.method == 'POST':
        form = DeliveryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('delivery-list')
    else:
        form = DeliveryForm()
    return render(request, 'admin/delivery_form.html', {'form': form})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def delivery_update(request, pk):
    delivery = get_object_or_404(Delivery, pk=pk)
    if request.method == 'POST':
        form = DeliveryForm(request.POST, instance=delivery)
        if form.is_valid():
            form.save()
            return redirect('delivery-list')
    else:
        form = DeliveryForm(instance=delivery)
    return render(request, 'admin/delivery_form.html', {'form': form})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def delivery_delete(request, pk):
    delivery = get_object_or_404(Delivery, pk=pk)
    if request.method == 'POST':
        delivery.delete()
        return redirect('delivery-list')
    return render(request, 'admin/delivery_confirm_delete.html', {'delivery': delivery})




@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def daily_total_view(request):
    selected_date_str = request.GET.get('selected_date')

    if selected_date_str:
        # Parse the selected date from the input
        selected_date = datetime_module.strptime(selected_date_str, "%Y-%m-%d").date()
    else:
        # If no date is provided, use today's date
        selected_date = timezone.now().date()

    # Fetching orders and events for the selected date
    orders_today = Order.objects.filter(date_ordered__date=selected_date, status='Delivered')
    events_today = Event.objects.filter(date=selected_date, paid=True)

    customers = Customer.objects.all()
    total_customers = customers.count()

    start_of_day = timezone.make_aware(timezone.datetime.combine(selected_date, timezone.datetime.min.time()))
    end_of_day = timezone.make_aware(timezone.datetime.combine(selected_date, timezone.datetime.max.time()))

    active_users = UserActivity.objects.filter(timestamp__range=(start_of_day, end_of_day))
    total_active_users = active_users.count()


    total_product_amount = 0
    total_delivery_amount = 0

    for order in orders_today:
        shipping_address = order.shippingaddress
        if shipping_address:
            delivery_price = shipping_address.delivery.price
            total_product_amount += order.get_cart_total
            total_delivery_amount += delivery_price

   
    ten_percent_of_product_amount = Decimal(0.1) * total_product_amount
    balance_after_10_percent = total_product_amount - ten_percent_of_product_amount

    ten_percent_of_product_amount = '{:.2f}'.format(ten_percent_of_product_amount)
    balance_after_10_percent = '{:.2f}'.format(balance_after_10_percent)
    
    

    total_sum = 0
    for event in events_today:
        event_items = EventItem.objects.filter(event=event)
        for item in event_items:
            total_sum += item.guest * item.chops.price
    total_sum_10_percent = total_sum * Decimal(0.1)
    balance = total_sum - total_sum_10_percent

    total_sum_10_percent = '{:.2f}'.format(total_sum_10_percent)
    balance = '{:.2f}'.format(balance)
    
    total_percent = Decimal(ten_percent_of_product_amount) + Decimal(total_sum_10_percent)
    total_balance = Decimal(balance_after_10_percent) + Decimal(balance)

    context = {
        'total_product_amount': total_product_amount,
        'total_delivery_amount': total_delivery_amount,
        'ten_percent_of_product_amount': ten_percent_of_product_amount,
        'balance_after_10_percent': balance_after_10_percent,
        'total_sum_10percent': total_sum_10_percent,
        'total_sum': total_sum,
        'balance': balance,
        'total_balance': total_balance,
        'total_percent': total_percent,
        'total_customers':total_customers,
        'total_active_users': total_active_users,
        'today': selected_date
    }

    return render(request, 'admin/daily_total.html', context)


#video view




@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def videos_list(request):
    videos = FoodVideo.objects.all().order_by('title')
    paginator = Paginator(videos, 10) 

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'admin/video_list.html', {'videos': videos, 'page_obj': page_obj})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def videos_detail(request, pk):
    video = get_object_or_404(FoodVideo, pk=pk)
    return render(request, 'admin/video_detail.html', {'video': video})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def video_new(request):
    if request.method == "POST":
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.save()
            return redirect('video_detail', pk=video.pk)
    else:
        form = VideoForm()
    return render(request, 'admin/video_edit.html', {'form': form})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def video_edit(request, pk):
    video = get_object_or_404(FoodVideo, pk=pk)
    if request.method == "POST":
        form = VideoForm(request.POST,request.FILES, instance=video)
        if form.is_valid():
            video = form.save(commit=False)
            video.save()
            return redirect('video_detail', pk=video.pk)
    else:
        form = VideoForm(instance=video)
    return render(request, 'admin/video_edit.html', {'form': form})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def video_delete(request, pk):
    video = get_object_or_404(FoodVideo, pk=pk)
    video.delete()
    return redirect('video_list')


    
   
    
import requests
def proxy_view(request):
    url = request.GET.get('url')
    if url:
        response = requests.get(url)
        return HttpResponse(response.content, content_type=response.headers['Content-Type'])
    else:
        return HttpResponse(status=400)    
    
