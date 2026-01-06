import django
from django.contrib.auth.models import User
from store.models import Address, Cart, Category, Order, Product
from django.shortcuts import redirect, render, get_object_or_404
from .forms import RegistrationForm, AddressForm
from django.contrib import messages
from django.views import View
from django.conf import settings
import decimal
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator # for Class Based Views
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Q


# Create your views here.

def home(request):
    categories = Category.objects.filter(is_active=True, is_featured=True)
    best_sellers = Product.objects.filter(is_active=True, is_featured=True).order_by('?')[:4]
    new_arrivals = Product.objects.filter(is_active=True).order_by('-created_at')[:4]
    context = {
        'categories': categories,
        'best_sellers': best_sellers,
        'new_arrivals': new_arrivals,
    }
    return render(request, 'store/index.html', context)


def detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.exclude(id=product.id).filter(is_active=True, category=product.category)
    context = {
        'product': product,
        'related_products': related_products,

    }
    return render(request, 'store/detail.html', context)


def all_categories(request):
    categories = Category.objects.filter(is_active=True)
    return render(request, 'store/categories.html', {'categories':categories})


def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(is_active=True, category=category)
    categories = Category.objects.filter(is_active=True)

    # Sorting Logic
    sorting = request.GET.get('sorting')
    if sorting == 'low-high':
        products = products.order_by('price')
    elif sorting == 'high-low':
        products = products.order_by('-price')
    elif sorting == 'newest':
         products = products.order_by('-created_at')

    context = {
        'category': category,
        'products': products,
        'categories': categories,
    }
    return render(request, 'store/category_products.html', context)


# Authentication Starts Here

class RegistrationView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'account/register.html', {'form': form})
    
    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request, "Congratulations! Registration Successful!")
            form.save()
        return render(request, 'account/register.html', {'form': form})
        

@login_required
def profile(request):
    addresses = Address.objects.filter(user=request.user)
    orders = Order.objects.filter(user=request.user)
    return render(request, 'account/profile.html', {'addresses':addresses, 'orders':orders})


@method_decorator(login_required, name='dispatch')
class AddressView(View):
    def get(self, request):
        form = AddressForm()
        return render(request, 'account/add_address.html', {'form': form})

    def post(self, request):
        form = AddressForm(request.POST)
        if form.is_valid():
            user=request.user
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            reg = Address(user=user, locality=locality, city=city, state=state)
            reg.save()
            reg.save()
            messages.success(request, "New Address Added Successfully.")
            
            # Check for 'next' parameter to redirect back to checkout
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('store:profile')


@login_required
def remove_address(request, id):
    a = get_object_or_404(Address, user=request.user, id=id)
    a.delete()
    messages.success(request, "Address removed.")
    return redirect('store:profile')

@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = get_object_or_404(Product, id=product_id)

    # Check whether the Product is alread in Cart or Not
    item_already_in_cart = Cart.objects.filter(product=product_id, user=user)
    if item_already_in_cart:
        cp = get_object_or_404(Cart, product=product_id, user=user)
        cp.quantity += 1
        cp.save()
    else:
        Cart(user=user, product=product).save()
    
    return redirect('store:cart')


@login_required
def cart(request):
    user = request.user
    cart_products = Cart.objects.filter(user=user)

    # Display Total on Cart Page
    amount = decimal.Decimal(0)
    shipping_amount = decimal.Decimal(10)
    # using list comprehension to calculate total amount based on quantity and shipping
    cp = [p for p in Cart.objects.all() if p.user==user]
    if cp:
        for p in cp:
            temp_amount = (p.quantity * p.product.price)
            amount += temp_amount

    # Customer Addresses
    addresses = Address.objects.filter(user=user)

    context = {
        'cart_products': cart_products,
        'amount': amount,
        'shipping_amount': shipping_amount,
        'total_amount': amount + shipping_amount,
        'addresses': addresses,
    }
    return render(request, 'store/cart.html', context)


@login_required
def remove_cart(request, cart_id):
    if request.method == 'GET':
        c = get_object_or_404(Cart, id=cart_id)
        c.delete()
        messages.success(request, "Product removed from Cart.")
    return redirect('store:cart')


@login_required
def plus_cart(request, cart_id):
    if request.method == 'GET':
        cp = get_object_or_404(Cart, id=cart_id)
        cp.quantity += 1
        cp.save()
    return redirect('store:cart')


@login_required
def minus_cart(request, cart_id):
    if request.method == 'GET':
        cp = get_object_or_404(Cart, id=cart_id)
        # Remove the Product if the quantity is already 1
        if cp.quantity == 1:
            cp.delete()
        else:
            cp.quantity -= 1
            cp.save()
    return redirect('store:cart')



@login_required
def checkout(request):
    user = request.user
    addresses = Address.objects.filter(user=user)
    cart_products = Cart.objects.filter(user=user)
    
    # Calculate Totals
    amount = decimal.Decimal(0)
    shipping_amount = decimal.Decimal(10)
    cp = [p for p in Cart.objects.all() if p.user==user]
    if cp:
        for p in cp:
            temp_amount = (p.quantity * p.product.price)
            amount += temp_amount
    
    total_amount = amount + shipping_amount

    # Razorpay Integration
    payment = None
    try:
        if settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            payment = client.order.create({
                'amount': int(total_amount * 100), 
                'currency': 'INR', 
                'payment_capture': '1' 
            })
    except Exception as e:
        print(f"Razorpay Integration Error: {e}")

    context = {
        'addresses': addresses,
        'cart_products': cart_products,
        'amount': amount,
        'shipping_amount': shipping_amount,
        'total_amount': total_amount,
        'payment': payment,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
    }
    return render(request, 'store/checkout.html', context)


@csrf_exempt
def payment_completed(request):
    if request.method == 'POST':
        # Verify specific details of the incoming request
        # In a real scenario, you'd verify the signature with razorpay client
        
        # Here we assume success for testing logic
        user = request.user
        cart = Cart.objects.filter(user=user)
        
        # We need to get address_id from somewhere. 
        # Typically passed via 'notes' in Razorpay order or stored in session.
        # For simplicity, let's grab the first address or last used one.
        # OR better, the frontend sends it. 
        # But Razorpay callback comes from Razorpay server or redirect.
        # Let's rely on the frontend form submission to 'checkout_process' for simpler integration relative to user request 
        # OR handle it here if using standard Razorpay checkout form submit.
        
        # ACTUALLY, checking the user requirement: "add razorpay testing script".
        # We will make the frontend handle the payment success and redirect to this view or 'checkout_process'.
        return redirect('store:orders') 

@csrf_exempt
@login_required
def payment_success(request):
    # 1. Retrieve the parameters from the request
    razorpay_payment_id = request.POST.get('razorpay_payment_id') or request.GET.get('razorpay_payment_id')
    razorpay_order_id = request.POST.get('razorpay_order_id') or request.GET.get('razorpay_order_id')
    razorpay_signature = request.POST.get('razorpay_signature') or request.GET.get('razorpay_signature')
    
    # We also need the address_id. We'll pass it from the frontend form.
    address_id = request.POST.get('address_id') or request.GET.get('address_id')

    # 2. Verify the Signature
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    params_dict = {
        'razorpay_order_id': razorpay_order_id,
        'razorpay_payment_id': razorpay_payment_id,
        'razorpay_signature': razorpay_signature
    }

    try:
        # verify_payment_signature raises an error if signature is invalid
        client.utility.verify_payment_signature(params_dict)
        
        # 3. Signature is valid -> Create the Order
        user = request.user
        if address_id:
            address = get_object_or_404(Address, id=address_id)
            cart = Cart.objects.filter(user=user)
            for c in cart:
                Order(user=user, address=address, product=c.product, quantity=c.quantity).save()
                c.delete()
            messages.success(request, "Payment Verified & Order Placed Successfully!")
            return redirect('store:orders')
        else:
            messages.error(request, "Payment Verified but Address missing!")
            return redirect('store:checkout')

    except razorpay.errors.SignatureVerificationError:
        messages.error(request, "Payment Verification Failed! Signature Mismatch.")
        return redirect('store:payment-failed')
    except Exception as e:
        print(f"Error: {e}")
        messages.error(request, "An error occurred during payment verification.")
        return redirect('store:payment-failed')

@login_required
def payment_failed(request):
    messages.error(request, "Payment Failed. Please try again.")
    return redirect('store:checkout')


@login_required
def checkout_process(request):
    user = request.user
    address_id = request.POST.get('address')
    
    # Validate address selection
    if not address_id:
        messages.error(request, "Please select a shipping address before checkout.")
        return redirect('store:checkout')

    address = get_object_or_404(Address, id=address_id)
    # Get all the products of User in Cart
    cart = Cart.objects.filter(user=user)
    for c in cart:
        # Saving all the products from Cart to Order
        Order(user=user, address=address, product=c.product, quantity=c.quantity).save()
        # And Deleting from Cart
        c.delete()
    return redirect('store:orders')


@login_required
def orders(request):
    all_orders = Order.objects.filter(user=request.user).order_by('-ordered_date')
    return render(request, 'store/orders.html', {'orders': all_orders})





@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status == 'Pending' or order.status == 'Accepted':
        order.status = 'Cancelled'
        order.save()
        messages.success(request, 'Order Cancelled Successfully')
    else:
        messages.error(request, 'Order Cannot Be Cancelled')
    return redirect('store:orders')



def shop(request):
    categories = Category.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True)

    # Sorting Logic
    sorting = request.GET.get('sorting')
    if sorting == 'low-high':
        products = products.order_by('price')
    elif sorting == 'high-low':
        products = products.order_by('-price')
    elif sorting == 'newest':
         products = products.order_by('-created_at')

    context = {
        'categories': categories,
        'products': products,
    }
    return render(request, 'store/shop.html', context)





def test(request):
    return render(request, 'store/test.html')

def search(request):
    query = request.GET.get('q')
    categories = Category.objects.filter(is_active=True)
    if query:
        products = Product.objects.filter(
            Q(title__icontains=query) | 
            Q(short_description__icontains=query) | 
            Q(detail_description__icontains=query)
        , is_active=True)
    else:
        products = Product.objects.filter(is_active=True)
    
    context = {
        'categories': categories,
        'products': products,
        'search_query': query,
    }
    return render(request, 'store/shop.html', context)

def search_suggestions(request):
    query = request.GET.get('term')
    if query:
        products = Product.objects.filter(title__icontains=query, is_active=True)[:5]
        results = []
        for product in products:
            product_json = {}
            product_json['id'] = product.id
            product_json['label'] = product.title
            product_json['value'] = product.title
            product_json['slug'] = product.slug
            if product.product_image:
                 product_json['image'] = product.product_image.url
            results.append(product_json)
        return JsonResponse(results, safe=False)
    return JsonResponse([], safe=False)
