"""
URL configuration for djangoProject269 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sample', views.sample, name='sample'),
    path('home2',views.home2,name='home2'),
    path('',views.home3,name='home3'),
    path('header',views.header,name='header'),
    path('phone',views.phone,name='phone'),
    path('sample',views.sample,name='sample'),
    path('choosemobile',views.choosemobile,name='choosemobile'),
    path('cartdetail/',views.cartdetail,name='cartdetail'),

    path('cart/add/<int:product_id>',views.addCart,name='addCart'),
    path('cart/remove/<int:product_id>',views.removeCart,name='removeCart'),
    path('category/<slug:category_slug>',views.choosemobile,name="product_by_category"),
    path('product/<slug:category_slug>/<slug:product_slug>',views.productPage,name='productDetail'),

    path('account/create',views.signUpView,name="signUp"),
    path('account/login',views.logInView,name="logIn"),
    path('account/logout',views.logOutView,name="logOut"),
    path('orderHistory/',views.orderHistory,name="orderHistory"),
    path('order/<int:order_id>',views.viewOrder,name="orderDetails"),

    path('search/',views.search,name='search'),
    path('cart/thankyou',views.thankyou,name='thankyou')
]
