from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

from .models import Cart, Purchase, Comment, Item

PAYING_CHOICES = [
    ('BANK', "Credit card"),
    ('HOME', "Cash on delivery")
]

DELIVERY_CHOICES = [
    ('HOME', "To your home"),
    ('PICK', "To pickup address")
]

"izgled formi koje se koriste u stranicama"

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, help_text='Enter a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )

class LoginForm(forms.Form):
    username = forms.CharField(required=True, max_length=50)
    password = forms.CharField(required=True, widget=forms.PasswordInput())

    class Meta:
        model = User

class PurchaseForm(forms.Form):
    address = forms.CharField(required=True)
    paying = forms.ChoiceField(required=True, widget=forms.RadioSelect, choices=PAYING_CHOICES)
    delivery = forms.ChoiceField(required=True, widget=forms.RadioSelect, choices=DELIVERY_CHOICES)

    class Meta:
        model = Purchase

class PurchaseCreditCardForm(forms.Form):
    credit_card = forms.CharField(required=True, max_length=50)
    security_number = forms.CharField(required=True, widget=forms.PasswordInput(), max_length=3)

    class Meta:
        model = Purchase

class CommentForm(forms.Form):
    comment = forms.CharField(required=True, widget=forms.Textarea, max_length=300)
    username = forms.CharField(required=True)

    class Meta:
        model = Comment

class CreateItemForm(forms.Form):
    name = forms.CharField(required=True, max_length=50)
    price = forms.IntegerField(required=True)
    about = forms.CharField(required=False)
    photo = forms.ImageField(required=False)
    photo_link = forms.URLField(required=False)

    class Meta:
        model = Item