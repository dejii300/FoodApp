from django.forms import ModelForm
from .models import *

from django.contrib.auth.models import User 
from django.contrib.auth.forms import UserCreationForm

from django import forms
from django.contrib.auth.forms import  SetPasswordForm


class CreateUserForm(UserCreationForm):
    
    class Meta:
        model = User
        fields = ['username','email', 'password1', 'password2']

class ProductForm(forms.ModelForm): 
    class Meta:
        model = Product
        fields = '__all__' 
        
class EvtProductForm(forms.ModelForm):
    class Meta:
        model = EvtProduct
        fields = '__all__'  

class CustomSetPasswordForm(SetPasswordForm):
    # Add any additional fields or customizations you may need
    pass


class EventForm(ModelForm):

    evtproducts = forms.ModelMultipleChoiceField(queryset=EvtProduct.objects.all(), widget=forms.CheckboxSelectMultiple(attrs={'class': 'inputr'}))
  
    class Meta:
        model = Event
        fields = '__all__'
        exclude = ['ref', 'paid', 'customer','status' , 'amount']
    
    
    
    def save(self, commit=True):
        event = super().save(commit=False)

        if commit:
            event.save()

            # Create EventItem instances for each selected product
            for chops in self.cleaned_data['evtproducts']:
                guest = int(self.cleaned_data.get('evtproducts_' + str(chops.id), 0))
                EventItem.objects.create(event=event, chops=chops, guest=guest)

        return event

class EventStatusForm(ModelForm):
    class Meta:
        model = Event
        fields = ['status']

class CustomerForm(ModelForm): 
    class Meta:
        model = Customer
        fields = '__all__'
        exclude = ['user']
    clear_profile_pic = forms.BooleanField(required=False)
    change_profile_pic = forms.ImageField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        clear_profile_pic = cleaned_data.get('clear_profile_pic')
        change_profile_pic = cleaned_data.get('change_profile_pic')

        if clear_profile_pic and change_profile_pic:
            raise forms.ValidationError("You can't both clear and change the profile picture.")

        return cleaned_data

class OrderStatusForm(ModelForm):
    class Meta:
        model = Order
        fields = ['status']






class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']


class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ['location', 'price']

class ShippingAddressForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['delivery'].queryset = Delivery.objects.order_by('location')

    class Meta:
        model = ShippingAddress
        fields = ['delivery','address','phone1','phone2','customize','additional_information']
        labels = {
            'customize': 'Customize (Optional)',
            'additional_information': 'Additional Information (Optional)',
        }


class VideoForm(forms.ModelForm):       
    class Meta:
        model = FoodVideo
        fields = ('title', 'description', 'video_file', 'cover_image' )
