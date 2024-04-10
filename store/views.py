from io import BytesIO
import random
import django
from django.contrib.auth.models import User
from ecommerce.settings import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET
from store.models import Address, Cart, Category, Order, Product, Wishlist,Review,Brand
from django.shortcuts import redirect, render, get_object_or_404
from .forms import RegistrationForm, AddressForm
from django.contrib import messages
from django.views import View
import decimal
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator # for Class Based Views
from django.views.decorators.csrf import csrf_exempt
import razorpay
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse
client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
from django.core.mail import send_mail
from django.core.mail import EmailMessage



# Create your views here.

def home(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        status = request.POST.get('status')
        order = get_object_or_404(Order,id=order_id)
        order.status = status
        order.save()
        
    categories = Category.objects.filter(is_active=True, is_featured=True)[:3]
    products = Product.objects.filter(is_active=True, is_featured=True)[:8]
    orders = Order.objects.all()
    choices = ['Pending','Accepted','Packed','On The Way','Delivered','Cancelled',]
    context = {
        'STATUS_CHOICES' : choices,
        'categories': categories,
        'products': products,
        'orders' : orders,
    }
    return render(request, 'store/index.html', context)

from django.db.models import Q

def search(request):
    search_text = request.POST.get('search', '').strip()

    # Fetch categories and products that match the search query
    categories = Category.objects.filter(is_active=True).order_by('created_at')
    products = Product.objects.filter(is_active=True)

    # If search query is not empty, filter products based on search query
    if search_text:
        # Search across multiple fields (title, description, etc.) using OR condition
        products = products.filter(
            Q(title__icontains=search_text) |
            Q(short_description__icontains=search_text) |
            Q(category__title__icontains=search_text)
        ).distinct()

    context = {
        'search_text': search_text,
        'categories': categories,
        'products': products,
    }

    return render(request, 'store/search_result.html', context)



def detail(request, slug):
    if request.method == 'POST':
        user = request.user
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product,id=product_id)
        rating = request.POST.get('rating')
        text = request.POST.get('text')
        Review(user=user,product=product,rating=rating,text=text).save()

    product = get_object_or_404(Product, slug=slug)
    category = get_object_or_404(Category,id=product.category.id)
    related_products = Product.objects.exclude(id=product.id).filter(is_active=True, category=product.category)
    reviews = Review.objects.filter(product=product)
    sum=0
    count=0
    for i in reviews:
        sum+=i.rating
        count+=1
    if count>0:
        average_rating = int(sum/count)
    else:
        average_rating=0

    context = {
        'category' : category,
        'product': product,
        'related_products': related_products,
        'reviews' : reviews,
        'average_rating' : average_rating,

    }

    return render(request, 'store/detail.html', context)


def all_categories(request):
    categories = Category.objects.filter(is_active=True).order_by('created_at')
    return render(request, 'store/categories.html', {'categories':categories})


def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(is_active=True, category=category)
    categories = Category.objects.filter(is_active=True).order_by('created_at')
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
            email = form.cleaned_data['email']
            request.session['data'] = form.cleaned_data

            # Generate OTP
            otp = ''.join(random.choices('0123456789', k=6))
            request.session['otp'] = otp

            # Send OTP to user's email
            sender = "prajeshiyer@gmail.com"
            recipient = [email]
            subject_to_applicant = "E-Commerce - OTP For Registration"
            message_to_applicant = "Use this OTP while registration : "+otp
            send_mail(subject_to_applicant, message_to_applicant, sender, recipient)

            return redirect('store:verify_otp')
        
        return render(request, 'account/register.html', {'form': form})

class OTPVerificationView(View):
    def get(self, request):
        return render(request, 'account/verify_otp.html')
    
    def post(self, request):
        otp = request.POST.get('otp')
        if 'otp' in request.session and request.session['otp'] == otp:
            # OTP is valid, proceed with registration
            form = RegistrationForm(request.session['data'])
            if form.is_valid():
                form.save()
                messages.success(request, "Congratulations! Registration Successful!")
                del request.session['otp']  # Clear OTP from session
                del request.session['data']  # Clear form data from session
                return redirect('store:home')
        # Invalid OTP or no OTP found in session
        messages.error(request, "Invalid OTP. Please try again.")
        return redirect('verify_otp')

    
def chatbot(request):
    return render(request, 'store/chatbot.html')
        

@login_required
def profile(request):
    if request.user.is_staff == True:
        return redirect('store:home')
    
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
            messages.success(request, "New Address Added Successfully.")
        return redirect('store:profile')


@login_required
def remove_address(request, id):
    a = get_object_or_404(Address, user=request.user, id=id)
    a.delete()
    messages.success(request, "Address removed.")
    return redirect('store:profile')

#### ---- WISHLIST ----####

@login_required
def add_to_wishlist(request, product_id):
    user = request.user
    product = get_object_or_404(Product, id=product_id)
    item_already_in_wishlist = Wishlist.objects.filter(product=product_id, user=user)
    if item_already_in_wishlist:
        return redirect('store:wishlist')
    else:
        Wishlist(user=user, product=product).save()
        return redirect('store:wishlist')

@login_required
def wishlist(request):
    user = request.user
    cart_products = Wishlist.objects.filter(user=user)

    context = {
        'cart_products': cart_products,
    }
    return render(request, 'store/wishlist.html', context)


@login_required
def remove_wishlist(request, wishlist_id):
    if request.method == 'GET':
        c = get_object_or_404(Wishlist, id=wishlist_id)
        c.delete()
        messages.success(request, "Product removed from Wishlist.")
    return redirect('store:wishlist')

#### ---- CART ----####

@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = get_object_or_404(Product, id=product_id)
    # Check whether the Product is alread in Cart or Not
    item_already_in_cart = Cart.objects.filter(product=product_id, user=user)
    if item_already_in_cart:
        # cp = get_object_or_404(Cart, product=product_id, user=user)
        # product = get_object_or_404(Product, id=cp.product.id)
        # if product.stock > cp.quantity:
        #     cp.quantity += 1
        #     cp.save()
        # else:
        messages.success(request, "Item already in cart!!")
    else:
        if product.stock > 0:
            Cart(user=user, product=product).save()
        else:
            messages.success(request, "Product is out of stock")   
    
    return redirect('store:cart')


@login_required
def cart(request):
    user = request.user
    cart_products = Cart.objects.filter(user=user)

    # Display Total on Cart Page
    amount = decimal.Decimal(0)
    
    # using list comprehension to calculate total amount based on quantity and shipping
    cp = [p for p in Cart.objects.all() if p.user==user]
    if cp:
        for p in cp:
            temp_amount = (p.quantity * p.product.price)
            amount += temp_amount

    # Customer Addresses
    addresses = Address.objects.filter(user=user)
    shipping_amount = float(amount)*0.05
    gst_amount = float(amount)*0.18
    total_amount = float(amount) + float(shipping_amount) + gst_amount

    if int(total_amount) == 0:
        total_amount = 1
    

    ##--Razorpay integration--##
    
    DATA = {
        "amount": int(total_amount)*100,
        "currency": "INR",
        "receipt": "receipt#1",
        "notes": {
             "key1": "value3",
            "key2": "value2"
        }
    }
    payment=client.order.create(data=DATA)

    context = {
        'cart_products': cart_products,
        'amount': amount,
        'gst_amount' : int(gst_amount),
        'shipping_amount': int(shipping_amount),
        'total_amount': int(total_amount),
        'addresses': addresses,
         'payment' : payment,
         'user' : user,
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
        product = get_object_or_404(Product, id=cp.product.id)
        if product.stock > cp.quantity:
            cp.quantity +=1
            cp.save()
        else:
            messages.success(request, "Only "+str(product.stock)+" available!")
    return redirect('store:cart')

@login_required
def update_cart(request, cart_id):
    if request.method == 'GET':
        qty = request.GET.get('qty')
        cp = get_object_or_404(Cart, id=cart_id)
        product = get_object_or_404(Product, id=cp.product.id)
        if product.stock >= int(qty):
            cp.quantity = int(qty)
            cp.save()
        else:
            messages.success(request, "Only "+str(product.stock)+" available!")
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
    address_id = request.GET.get('address')
    
    address = get_object_or_404(Address, id=address_id)
    # Get all the products of User in Cart
    cart = Cart.objects.filter(user=user)
    for c in cart:
        # Saving all the products from Cart to Order
        Order(user=user, address=address, product=c.product, quantity=c.quantity).save()
        product = c.product
        product.stock -= c.quantity
        if product.stock == 0:
            product.is_active=False
        product.save()
        # And Deleting from Cart
        c.delete()
    
    # Generate and send invoice
    generate_and_send_invoice(user, address)
    return redirect('store:orders')

def generate_and_send_invoice(user, address):
    order = Order.objects.last()  # Get the latest order
    product = order.product
    sub_total = product.price * order.quantity
    gst = round(float(sub_total) * 0.18, 3)
    total = float(sub_total) + gst

    # Render the HTML template with a context
    context = {'user': user, 'product': product, 'order': order, 'sub_total': sub_total, 'gst': gst, 'total': total,
               'address': address}
    template = get_template('store/invoice2.html')
    html_content = template.render(context)

    # Create PDF from HTML
    pdf = BytesIO()
    pisa.CreatePDF(BytesIO(html_content.encode('UTF-8')), pdf)

    # Create email message
    email_subject = 'E-Commerce : Order Summary'
    email_body = 'Please find attached Order Summary for Your Latest Order.'
    from_email = 'prajeshiyer@gmail.com'
    to_email = [user.email]

    # Attach PDF to email
    email = EmailMessage(email_subject, email_body, from_email, to_email)
    email.attach('summary.pdf', pdf.getvalue(), 'application/pdf')
    # Send email
    email.send()

def generate_invoice(request,order_id):
    order = get_object_or_404(Order,id=order_id)
    product = get_object_or_404(Product,id=order.product.id)
    user = get_object_or_404(User,id=order.user.id)
    address_list = Address.objects.filter(user=user)
    for a in address_list:
        ad = a
    address = ad.locality+", "+ad.city+", "+ad.state

    sub_total = product.price*order.quantity
    gst = round(float(sub_total)*0.18,3)
    total = float(sub_total) + gst

    # Render the HTML template with a context
    template = get_template('store/invoice2.html')
    context = {'user': user, 'product': product, 'order': order, 'sub_total':sub_total, 'gst':gst, 'total':total, 'address':address}
    html = template.render(context)

    # Create a PDF object, and write the HTML to it
    pdf = BytesIO()
    pisa.CreatePDF(BytesIO(html.encode('UTF-8')), pdf)

    # Return the PDF as a response
    response = HttpResponse(pdf.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'filename="Summary.pdf"'
    return response

@login_required
def orders(request):
    all_orders = Order.objects.filter(user=request.user).order_by('-ordered_date')
    return render(request, 'store/orders.html', {'orders': all_orders})

def shop(request):
    return render(request, 'store/shop.html')

def test(request):
    return render(request, 'store/test.html')

#---ADMIN-----#
from .forms import BrandForm, CategoryForm, ProductForm

#CATEGORY
def admin_category(request):
    categories = Category.objects.all()
    return render(request, 'admin/category.html', {'categories': categories})

def admin_add_cat(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # Redirect or do something else
    else:
        form = CategoryForm()
    return render(request, 'admin/add_cat.html', {'form': form})

#BRAND
def admin_brand(request):
    brands = Brand.objects.all()
    return render(request, 'admin/brand.html', {'brands': brands})

def admin_add_brand(request):
    if request.method == 'POST':
        form = BrandForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # Redirect or do something else
    else:
        form = BrandForm()
    return render(request, 'admin/add_brand.html', {'form': form})

#PRODUCT
def admin_product(request):
    products = Product.objects.all()
    return render(request, 'admin/product.html', {'products': products})

def admin_add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # Redirect or do something else
    else:
        form = ProductForm()
    return render(request, 'admin/add_product.html', {'form': form})

