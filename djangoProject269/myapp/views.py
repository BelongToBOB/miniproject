from django.shortcuts import render,redirect,get_object_or_404 
from django.http import HttpResponse
from myapp.models import Category,Product,Cart,CartItem,Order,OrderItem
from myapp.forms import SignUpFrom
from django.contrib.auth.models import Group,User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login,authenticate,logout
from django.core.paginator import Paginator,EmptyPage,InvalidPage
from django.contrib.auth.decorators import login_required
from django.conf import settings
import stripe
from django.contrib import messages
# Create your views here.

def sample(request):
    return HttpResponse("<H1>Hello World</H1> <br> This is Sample Page.")

def home2(request):
    return render(request,"home2.html")

def home3(request):
    return render(request,"customer/home3.html")

def header(request):
    return render(request,"customer/header.html")

def choosemobile(request,category_slug=None):
    products=None
    category_page=None
    if category_slug!=None:
        category_page=get_object_or_404(Category,slug=category_slug)
        products=Product.objects.all().filter(category=category_page,available=True)
    else:
        products=Product.objects.all().filter(available=True)

    paginator=Paginator(products,8)
    try:
        page=int(request.GET.get('page','1'))
    except:
        page=1
    
    try:
        productperPage=paginator.page(page)
    except (EmptyPage,InvalidPage):
        productperPage=paginator.page(paginator.num_pages)

    return render(request,"customer/choosemobile.html",{'products':productperPage, 'category':category_page})

def phone(request):
    return render(request,"phone.html")

def productPage(request,category_slug,product_slug):
    try:
        product=Product.objects.get(category__slug=category_slug,slug=product_slug)
    except Exception as e :
        raise e
    return render(request,'customer/product.html',{'product':product})

def _cart_id(request):
    cart=request.session.session_key
    if not cart:
        cart=request.session.create()
    return cart

@login_required(login_url="logIn")
def addCart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
    except CartItem.DoesNotExist:
        if product.stock > 0:
            CartItem.objects.create(
                product=product,
                cart=cart,
                quantity=1
            )

    return redirect('choosemobile')


def cartdetail(request):
    total=0
    counter=0
    cart_items=None
    try:
        cart=Cart.objects.get(cart_id=_cart_id(request))
        cart_items=CartItem.objects.filter(cart=cart,active=True)
        for item in cart_items:
            total+=(item.product.price*item.quantity)
            counter+=item.quantity
    except Exception as e :
        pass
    stripe.api_key=settings.SECRET_KEY
    stripe_total=int(total*100)
    description="Payment Online"
    data_key=settings.PUBLIC_KEY

    if request.method=='POST':
        try :
            token=request.POST['stripeToken']
            email=request.POST['stripeEmail']
            name=request.POST['stripeBillingName']
            address=request.POST['stripeBillingAddressLine1']
            city=request.POST['stripeBillingAddressCity']
            postcode=request.POST['stripeShippingAddressZip']
            customer=stripe.Customer.create(
                email=email,
                source=token
            )
            charge=stripe.Charge.create(
                amount=stripe_total,
                currency='thb',
                description=description,
                customer=customer.id
            )
            order=Order.objects.create(
                name=name,
                address=address,
                city=city,
                postcode=postcode,
                total=total,
                email=email,
                token=token
            )
            order.save()
            
            for item in cart_items:
                order_item=OrderItem.objects.create(
                    product=item.product.name,
                    quantity=item.quantity,
                    price=item.product.price,
                    order=order
                )
                order_item.save()
            
                product=Product.objects.get(id=item.product.id)
                product.stock=int(item.product.stock-order_item.quantity)
                product.save()
                item.delete()
            return redirect('thankyou')

        except stripe.error.CardError as e :
            return False , e

    return render(request,"customer/cartdetail.html",dict(cart_items=cart_items,total=total,counter=counter,data_key=data_key,stripe_total=stripe_total,description=description))

def removeCart(request,product_id):
    cart=Cart.objects.get(cart_id=_cart_id(request))
    product=get_object_or_404(Product,id=product_id)
    cartItem=CartItem.objects.get(product=product,cart=cart)
    cartItem.delete()
    return redirect('cartdetail')

def signUpView(request):
    if request.method=='POST':
        form=SignUpFrom(request.POST)
        
        if form.is_valid():
            form.save()
            username=form.cleaned_data.get('username')
            signUpUser=User.objects.get(username=username)
            customer_group=Group.objects.get(name='Customer')
            customer_group.user_set.add(signUpUser)

    else:    
        form=SignUpFrom()
    return render(request,"customer/signup.html",{'form':form})

def logInView(request):
    if request.method=='POST':
        form=AuthenticationForm(data=request.POST)
        if form.is_valid():
            username=request.POST['username']
            password=request.POST['password']
            user=authenticate(username=username,password=password)
            if user is not None:
                login(request,user)
                return redirect('home3')
            else:
                return redirect('signUp')
    else:
        form=AuthenticationForm()
    return render(request,'customer/logIn.html',{'form':form})

def logOutView(request):
    logout(request)
    return redirect('logIn')

def search(request):
    products=Product.objects.filter(name__contains=request.GET['title'])
    return render(request,'customer/choosemobile.html',{'products':products})

def orderHistory(request):
    if request.user.is_authenticated:
        email=str(request.user.email)
        orders=Order.objects.filter(email=email)
    return render(request,'customer/orders.html',{'orders':orders})

def viewOrder(request,order_id):
    if request.user.is_authenticated:
        email=str(request.user.email)
        order=Order.objects.get(email=email,id=order_id)
        orderitem=OrderItem.objects.filter(order=order)
    return render(request,'customer/viewOrder.html',{'order':order,'order_items':orderitem})

def thankyou(request):
    return render(request,'customer/thankyou.html')