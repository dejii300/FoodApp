from django.db import models
# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
import secrets
from django.db.models import Avg

from .paystack import Paystack

from django.dispatch import receiver
import os
from django.db.models.signals import pre_save




class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE, related_name="customer")
    username = models.CharField(max_length=200, null=True)
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    phone = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True,)
    address = models.CharField(max_length=200, null=True)
    profile_pic = models.ImageField(upload_to="profile_pics/", default="profile_pics/profile1.png", null=True, blank=True)
    date_created =models.DateTimeField(auto_now_add=True, null=True)

    
    @property
    def picURL(self):
        try:
            url = self.profile_pic.url
        except:
            url = ''
        return url 

   

    def __str__(self):
        return str(self.user)
    
    def delete(self, *args, **kwargs):
        # Delete the associated profile picture file from storage
        if self.profile_pic:
            if os.path.isfile(self.profile_pic.path):
                os.remove(self.profile_pic.path)
        super().delete(*args, **kwargs)
    

   

class Category(models.Model):
    name = models.CharField(max_length=200, null=True )
   
    def __str__(self):
        return self.name

    


class Product(models.Model):
    
    name = models.CharField(max_length=200, null=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    description = models.TextField( max_length=500, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    category = models.ManyToManyField(Category, related_name='products')
    image = models.ImageField( upload_to="products/", null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url  
    
    def delete(self, *args, **kwargs):
        # Delete the associated image file from storage
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)
    

    
    
class Rating(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    rating = models.IntegerField(default=0, validators=[MaxValueValidator(5), MinValueValidator(0),])  
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rate by {self.customer} for {self.rating}"    

class EvtProduct(models.Model):
    
    name = models.CharField(max_length=200, null=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    description = models.TextField(max_length=500, null=True, blank=True)
    evtimage = models.ImageField( upload_to="eventproducts/", null=True, blank=True)

    def __str__(self):
        return self.name
    
    @property
    def imageURL(self):
        try:
            url = self.evtimage.url
        except:
            url = ''
        return url      
    
    def delete(self, *args, **kwargs):
        # Delete the associated image file from storage
        if self.evtimage:
            if os.path.isfile(self.evtimage.path):
                os.remove(self.evtimage.path)
        super().delete(*args, **kwargs)





    
class FoodVideo(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    liked = models.ManyToManyField(Customer, blank=True, related_name='likes')
    cover_image = models.ImageField(upload_to='video_image/', null=True,)
    video_file = models.FileField(upload_to='food_videos/', null=True,)
    viewers = models.ManyToManyField(Customer, blank=True, related_name='viewed_videos')

    def __str__(self):
        return self.title 
    
    def nun_likes(self):
        return self.liked.all().count()
    
    @property
    def cover_imageURL(self):
        try:
            url = self.cover_image.url
        except:
            url = ''
        return url
    
    @property
    def video_fileURL(self):
        try:
            url = self.video_file.url
        except:
            url = ''
        return url
    
    def delete(self, *args, **kwargs):
        # Delete the associated cover image file from storage
        if self.cover_image:
            if os.path.isfile(self.cover_image.path):
                os.remove(self.cover_image.path)
        # Delete the associated video file from storage
        if self.video_file:
            if os.path.isfile(self.video_file.path):
                os.remove(self.video_file.path)
        super().delete(*args, **kwargs)
      
LIKE_CHOICES =(
    ('Like', 'Like'),
    ('Unlike', 'Unlike'),
)
class Like(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    video = models.ForeignKey(FoodVideo, on_delete=models.CASCADE)
    value = models.CharField(choices=LIKE_CHOICES, max_length=8)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}-{self.video}-{self.value}"

class Delivery(models.Model):
    location = models.CharField(max_length=200, null=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return self.location    
       
class ShippingAddress(models.Model):
    delivery =  models.ForeignKey(Delivery, on_delete=models.SET_NULL, blank=False, null=True)
    address = models.CharField(max_length=200, null=True, blank=False)
    phone1 = models.CharField(max_length=200, null=True, blank=False)
    phone2 = models.CharField(max_length=200, null=True, blank=False)
    customize = models.ImageField(upload_to="customize/", null=True, blank=True)
    additional_information  = models.TextField(max_length=500, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
            return self.address
    
   
        
class Order(models.Model):
    STATUS = (
        
        ('Processing', 'Processing'),
        ('Out_for_delivery', 'Out for delivery'),
        ('Delivered', 'Delivered'),
    )
    customer = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)
    shippingaddress = models.ForeignKey(ShippingAddress, null=True, on_delete=models.SET_NULL)
    amount = models.PositiveBigIntegerField(null=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    ref = models.CharField(max_length=200, null=True)
    status = models.CharField(max_length=200, null=True, choices=STATUS, default='Processing')

    def __str__(self):
        return str(self.id)

           

    
    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])

        

        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total
    
    def save(self, *args, **kwargs):
            while not self.ref:
                ref = secrets.token_urlsafe(50)
                object_with_similar_ref = Order.objects.filter(ref=ref)
                if not object_with_similar_ref:
                    self.ref = ref
            super().save(*args, **kwargs)        
        
    def amount_value(self):
        return int(self.amount) * 100
    
    def verify_payment(self):
        paystack = Paystack()
        status, result = paystack.verify_payment(self.ref, self.amount)
        if status:
            result_amount_base = result['amount'] / 100
            if result_amount_base == self.amount:
                self.complete = True
                self.save()
        if self.complete:
            return True
        else:
            return False 
        
class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return str(self.product) 

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total






    
    

class Event(models.Model):

    STATUS = (
        
        ('Waiting', 'Waiting'),
        ('Went', 'Went'),
        
    )

    TIME_CHOICES = [
        ('AM', 'AM'),
        ('PM', 'PM'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.TextField(max_length=500)
    date = models.DateField()
    time = models.TimeField()
    time_type = models.CharField(max_length=200, choices=TIME_CHOICES, default='AM')
    status = models.CharField(max_length=200, null=True, choices=STATUS, default='Waiting')
    phone1 = models.CharField(max_length=15)
    phone2 = models.CharField(max_length=15)
    paid = models.BooleanField(default=False, null=True, blank=False)
    amount = models.PositiveBigIntegerField(null=True)
    ref = models.CharField(max_length=200, null=True)
    evtproducts = models.ManyToManyField(EvtProduct, through='EventItem', related_name='event_item')

    def __str__(self):
        return str(self.customer.username)
    
    def save(self, *args, **kwargs):
            while not self.ref:
                ref = secrets.token_urlsafe(50)
                object_with_similar_ref = Event.objects.filter(ref=ref)
                if not object_with_similar_ref:
                    self.ref = ref
            super().save(*args, **kwargs)        
        
    def amount_value(self):
        return int(self.amount) * 100
    
    def verify_payment(self):
        paystack = Paystack()
        status, result = paystack.verify_payment(self.ref, self.amount)
        if status:
            result_amount_base = result['amount'] / 100
            if result_amount_base == self.amount:
                self.paid = True
                self.save()
        if self.paid:
            return True
        else:
            return False 


class EventItem(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    chops = models.ForeignKey(EvtProduct, on_delete=models.CASCADE)
    guest = models.PositiveIntegerField()
    

   
 
class MediaItem(models.Model): 
    file = models.FileField(upload_to='gallery_media/') 

    def __str__(self):
        return self.file
    
    @property
    def fileURL(self):
        try:
            url = self.file.url
        except:
            url = ''
        return url
    


class Comment(models.Model):
    customer =  models.ForeignKey(Customer, on_delete=models.CASCADE)
    content = models.TextField()
    approved = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.customer.username} - {self.timestamp}'   
    


class UserActivity(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    activity_type = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f'{self.user.username} - {self.activity_type} - {self.timestamp}'