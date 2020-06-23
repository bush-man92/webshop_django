from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.generic import ListView, FormView
from django.views.generic.base import View, TemplateView
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib.auth.mixins import LoginRequiredMixin
from braces.views import SuperuserRequiredMixin

from .models import Item, Cart, Purchase, Comment
from .forms import RegistrationForm, LoginForm, PurchaseForm, PurchaseCreditCardForm, CommentForm, CreateItemForm
# Create your views here.

class homeView(ListView):
    """
        lista svih produkta u home page-u
    """
    template_name = 'webshopApp/home.html'
    queryset = Item.objects.all()
    object_list = queryset
    context_object_name = 'allItems'

    def post(self, form):
        if form.POST.get('quantity') == '':
            "ako se posta quantity kao prazan string quantity je 0"
            quantity = 0
        elif form.POST.get('quantity'):
            quantity = int(form.POST.get('quantity'))
        if form.POST.get('item_id'):
            item_id = int(form.POST.get('item_id'))
        user = self.request.user
        if 'Search' in self.request.POST:
            "gleda dali je search integar ili string pa pretražuje cijene ili imena"
            search = self.request.POST.get('Search')
            try:
                search = int(search)
                queryset = Item.objects.filter(price__lte=search)
            except:
                queryset = Item.objects.filter(name__icontains=search)
            context = {'allItems' : queryset}
            return render(self.request, self.template_name, context)
        if 'Delete' in self.request.POST:
            "mogućnost brisanja za admina"
            cart = Cart.objects.filter(item_id=item_id).delete()
            comment = Comment.objects.filter(item_id=item_id).delete()
            item = Item.objects.get(id=item_id).delete()
            queryset = Item.objects.all()
            context = {'allItems' : queryset}
            return render(self.request, self.template_name, context)
        if quantity > 0 and user.is_authenticated:
            "update košarice korisnika"
            cart = Cart.objects.filter(user_id=user.id, item_id=item_id)
            if cart:
                quantity = cart[0].quantity + quantity
                Cart.objects.filter(user_id=user.id, item_id=item_id).update(quantity=quantity)
            else:
                Cart.objects.create(user_id=user.id, item_id=item_id, quantity=quantity)
        return render(self.request, self.template_name, context=self.get_context_data())

class registrationView(FormView):
    """
        registracija korisnika
    """
    template_name = 'webshopApp/registration_form.html'
    form_class = RegistrationForm
    success_url = 'home'

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password1')
        if self.email_check(email) == False:
            form.add_error('email', 'Email is already registered.')
            context = {'form' : form}
            return render(self.request, self.template_name, context)
        else:
            "stvara korisnika i pohranjuje hashani password"
            hashed_password = make_password(password=password, salt=None, hasher='bcrypt_sha256')
            user = User.objects.create(username = username, password = hashed_password, email = email)
            login(self.request, user)
            return redirect(self.success_url)

    def email_check(self, email):
        "provjerava postojanje email-a u bazi podataka"
        try:
            user = User.objects.get(email=email)
            return False
        except:
            return True

class loginView(FormView):
    """
        login korisnika
    """
    template_name = 'webshopApp/login.html'
    form_class = LoginForm
    success_url = 'home'

    def form_valid(self, form):
        "provjerava postojanje username-a, zatim provjerava password te redirecta"
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        redirect_to = self.request.POST['next']
        context = {'form' : form}
        user = None
        try:
            user = User.objects.get(username=username)
        except:
            form.add_error('username', 'Username doesn\t exists.')
            return render(self.request, self.template_name, context)
        if user is not None:
            password_validation = check_password(password, user.password)
            if password_validation:
                login(self.request, user)
                if redirect_to:
                    return redirect(redirect_to)
                else:
                    return redirect(self.success_url)
            else:
                form.add_error('password', 'Wrong password')
                return render(self.request, self.template_name, context)

class logoutView(View):
    """
        logout korisnika
    """
    template_name = 'webshopApp/logout.html'

    def get(self, request):
        logout(self.request)
        return render(self.request, self.template_name)

class shopping_cartView(LoginRequiredMixin, ListView):
    """
        košarica korisnika
    """
    template_name = 'webshopApp/shopping_cart.html'
    login_url = 'login/'

    def get(self, request):
        "pretražuje košaricu vezanu za korisnika i rendera stranicu"
        user = self.request.user
        queryset = Cart.objects.filter(user_id=user.id).select_related('item')
        return render(self.request, self.template_name, context={'cart' : queryset})

    def post(self, form):
        "izbacivanje iz košarice"
        quantity = int(form.POST.get('quantity'))
        if quantity < 0:
            quantity = abs(quantity)
        item_id = int(form.POST.get('item_id'))
        user = self.request.user
        queryset = Cart.objects.filter(user_id=user.id).select_related('item')
        if quantity > 0 and user.is_authenticated:
            cart = Cart.objects.filter(user_id=user.id, item_id=item_id)
            if quantity >= cart[0].quantity:
                Cart.objects.filter(user_id=user.id, item_id=item_id).delete()
            else:
                quantity = cart[0].quantity - quantity
            Cart.objects.filter(user_id=user.id, item_id=item_id).update(quantity=quantity)
        return render(self.request, self.template_name, context={'cart' : queryset})

class purchaseView(LoginRequiredMixin, FormView):
    """
        prva stranica purchasa, upit adrese, načina plaćanja i dostave
    """
    template_name = 'webshopApp/purchase.html'
    login_url = 'login/'
    form_class = PurchaseForm

    def form_valid(self, form):
        address = form.cleaned_data.get('address')
        paying = form.cleaned_data.get('paying')
        delivery = form.cleaned_data.get('delivery')
        user = self.request.user
        total_price = 0
        if 'Abort' in self.request.POST:
            return redirect('home')
        if paying == "BANK":
            self.request.session['address'] = address
            self.request.session['paying'] = paying
            self.request.session['delivery'] = delivery
            return redirect('purchase_credit_card')
        else:
            cart = Cart.objects.filter(user_id=user.id)
            for item in cart:
                total_price += item.item.price * item.quantity
            purchase = Purchase.objects.create(
                address=address, 
                paying=paying, 
                delivery=delivery, 
                user=user, 
                total_price=total_price)
            self.request.session['purchase_id'] = purchase.id
            return redirect('purchase_success')

class purchase_credit_cardView(LoginRequiredMixin, FormView):
    """
        druga stranica purchasa, samo za kreditne kartice
    """
    template_name = 'webshopApp/purchase_credit_card.html'
    login_url = 'login/'
    form_class = PurchaseCreditCardForm

    def form_valid(self, form):
        credit_card = form.cleaned_data.get('credit_card')
        security_number = form.cleaned_data.get('security_number')
        address = self.request.session.get('address')
        paying = self.request.session.get('paying')
        delivery = self.request.session.get('delivery')
        user = self.request.user
        total_price = 0
        if 'Abort' in self.request.POST:
            return redirect('home')
        else:
            cart = Cart.objects.filter(user_id=user.id)
            for item in cart:
                total_price += item.item.price * item.quantity
            purchase = Purchase.objects.create(
                address=address,
                paying=paying,
                delivery=delivery,
                user=user,
                credit_card=credit_card,
                security_number=security_number,
                total_price=total_price
            )
            self.request.session['purchase_id'] = purchase.id
            return redirect('purchase_success')

class purchase_successView(LoginRequiredMixin, ListView):
    """
        stranica potvrde kupnje i slanje maila s potvrdom
    """
    template_name = 'webshopApp/purchase_success.html'
    login_url = 'login/'

    def get(self, request):
        purchase_id = self.request.session.get('purchase_id')
        user = self.request.user
        cart = Cart.objects.filter(user_id=user.id).select_related('item')
        purchase = Purchase.objects.filter(id=purchase_id).select_related('user')
        context = {'cart' : cart, 'purchase' : purchase}
        message_list = []
        for item in context['cart']:
            message_list = item.item.name + " * " + str(item.quantity)
        message = "You " + user.username + " have bought " + message_list + " Total price: " + str(purchase[0].total_price) + " KN Address: " + purchase[0].address
        send_mail(
            subject='Purchase',
            message=message,
            from_email='testing@example.com',
            recipient_list=[user.email]
        )
        return render(self.request, self.template_name, context)

    def post(self, form):
        user = self.request.user
        Cart.objects.filter(user_id=user.id).delete()
        return redirect('home')

class productView(ListView):
    """
        stranica pojedinog produkta s komentarima
    """
    template_name = 'webshopApp/product.html'
    form_class = CommentForm
    paginate_by = 10

    def get(self, request, item_id):
        item = Item.objects.filter(id=item_id)
        comments = Comment.objects.filter(item_id=item_id).order_by('created_at').reverse()
        context = {'item' : item, 'form' : self.form_class, 'comments' : comments}
        return render(self.request, self.template_name, context)

    def post(self, form, item_id):
        item = Item.objects.filter(id=item_id)
        comments = Comment.objects.filter(item_id=item_id)
        context = {'item' : item, 'form' : self.form_class, 'comments' : comments}
        comment = form.POST['comment']
        user = self.request.user
        if user.is_authenticated:
            Comment.objects.create(comment=comment, item_id=item_id, username=user.username, approved=True)
        else:
            Comment.objects.create(comment=comment, item_id=item_id)
        return render(self.request, self.template_name, context)

class adminView(SuperuserRequiredMixin, LoginRequiredMixin, ListView):
    """
        admin pregled komentara, potvrda i brisanje
    """
    template_name = 'webshopApp/admin.html'
    queryset = Comment.objects.filter(approved=False).select_related('item')
    object_list = queryset
    context_object_name = 'comments'
    paginate_by = 10
    login_url = 'login/'

    def post(self, form):
        if 'Approve' in self.request.POST:
            comment = Comment.objects.filter(id=form.POST.get('comment_id')).update(approved=True)
            return render(self.request, self.template_name, self.get_context_data())
        else:
            Comment.objects.filter(id=form.POST.get('comment_id')).delete()
            return render(self.request, self.template_name, self.get_context_data())

class create_itemView(SuperuserRequiredMixin, LoginRequiredMixin, FormView):
    """
        stvaranje novih produkata za admina
    """
    template_name = 'webshopApp/create_item.html'
    login_url = 'login/'
    form_class = CreateItemForm
    success_url = 'home'

    def form_valid(self, form):
        name = form.cleaned_data.get('name')
        price = form.cleaned_data.get('price')
        about = form.cleaned_data.get('about')
        photo = form.cleaned_data.get('photo')
        photo_link = form.cleaned_data.get('photo_link')
        Item.objects.create(
            name=name,
            price=price,
            about=about,
            photo=photo,
            photo_link=photo_link
        )
        return redirect(self.success_url)