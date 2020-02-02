from django.urls import path, include
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views
from webshopProject import settings

urlpatterns = [
    path('', views.homeView.as_view(), name='home'),
    path('home', views.homeView.as_view(), name='home'),
    path('registration', views.registrationView.as_view(), name='registration'),
    path('login/', views.loginView.as_view(), name='login'),
    path('logout/', views.logoutView.as_view(), name='logout'),
    path('shopping_cart', views.shopping_cartView.as_view(), name='shopping_cart'),
    path('purchase', views.purchaseView.as_view(), name='purchase'),
    path('purchase_credit_card', views.purchase_credit_cardView.as_view(), name='purchase_credit_card'),
    path('purchase_success', views.purchase_successView.as_view(), name='purchase_success'),
    path('product/<int:item_id>', views.productView.as_view(), name='product'),
    path('admin', views.adminView.as_view(), name='admin'),
    path('create_item', views.create_itemView.as_view(), name='create_item'),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)