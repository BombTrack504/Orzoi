from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from marketplace import views as MarkeetplaceViews

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('', include('accounts.urls')),
    path('marketplace/', include('marketplace.urls')),

    # CART
    path('cart/', MarkeetplaceViews.cart, name='cart'),

    # Search
    path('search/', MarkeetplaceViews.search, name='search'),

    # Checkout
    path('checkout/', MarkeetplaceViews.checkout, name='checkout'),

    # ORDERS
    path('orders/', include('orders.urls')),

    path('submit_review/<int:restaurant_id>/',
         views.submit_review, name='submit_review')

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
