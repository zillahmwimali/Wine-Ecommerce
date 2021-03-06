from django.shortcuts import render, redirect,HttpResponseRedirect
from django.views import View
from .models import Product,Order,Customer,Category
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password


	# views of the products and the category functionality
class Prod(View):
	def get(self,request):
		cart = request.session.get('cart')
		categories = Category.getAllCategory()
		products = Product.getAllProduct().order_by('-id')

		if request.GET.get('id'):
			filterProductById = Product.objects.get(id=int(request.GET.get('id')))
			return render(request, 'productDetail.html',{"product":filterProductById,"categories":categories})

		if not cart:
			request.session['cart'] = {}

		if request.GET.get('category_id'):
			filterProduct = Product.getProductByFilter(request.GET['category_id'])
			return render(request, 'prods.html',{"products":filterProduct,"categories":categories})

		return render(request, 'prods.html',{"products":products,"categories":categories})
	# add to cart functionality that will update the cart as per the users request
	def post(self,request):
		product = request.POST.get('product')

		cart = request.session.get('cart')
		if cart:
			quantity = cart.get(product)
			if quantity:
				cart[product] = quantity+1
			else:
				cart[product] = 1
		else:
			cart = {}
			cart[product] = 1

		print(cart)
		request.session['cart'] = cart
		return redirect('cart')
#cart page functionality
class Cart(View):
	def get(self,request):
		productList = list(request.session.get('cart').keys())
		if request.GET.get('increase'):
			pId = request.GET.get('increase')
			products = request.session.get('cart')
			products[pId] += 1
			request.session['cart'] = products

		if request.GET.get('decrease'):
			pId = request.GET.get('decrease')
			products = request.session.get('cart')
			print(products[pId])
			if products[pId] > 1:
				products[pId] -= 1
				request.session['cart'] = products
				productList = list(request.session.get('cart').keys())
			else :
				del products[pId]
				request.session['cart'] = products
				productList = list(request.session.get('cart').keys())
				

		allProduct = Product.getProductById(productList)
		return render(request,'cart.html',{"allProduct":allProduct})
#customers ordered products list functionality
class Orders(View):
	def get(self,request):
		customer_id = request.session.get('customer')
		orders = Order.objects.filter(customer = customer_id).order_by("-date").order_by("-id")
		print(orders)
		return render(request,'order.html',{"orders":orders})

class Checkout(View):
	def get(self,request):
		return redirect('cart')
	
	def post(self,request):
		address = request.POST.get('address')
		phone = request.POST.get('phone')
		cart = request.session.get('cart')
		products = Product.getProductById(list(cart.keys()))
		customer = request.session.get('customer')
		print(address,phone,cart,products,customer)

		for product in products:
			newOrder = Order(product=product,customer=Customer(id=customer),
					quantity=cart[str(product.id)],
					price=product.price,
					address=address,
					phone=phone,
				)

		request.session['cart'] = {}
		return redirect('order')
# a user should be able to sign up
class Signup(View):

	def get(self,request):
		return render(request,'signup.html')
			
	def post(self,request):
		userData = request.POST
		# validation of credentials
		error = self.validateData(userData)
		if error :
			return render(request,'signup.html',{"error":error,"userData":userData})
		else:
			if Customer.emailExits(userData['email']):
				error["emailExits_error"] = "Email already exits. Try again"
				return render(request,'signup.html',{"error":error,"userData":userData})
			else:
				customer = Customer(
					name=userData['name'],
					email=userData['email'],
					phone=userData['phone'],
					password=make_password(userData['password']),
				)
				customer.save()
				return redirect('prod')

	# Validatio of form method
	def validateData(self,userData):
		error = {}
		if not userData['name'] or not userData['email']  or not userData['phone']  or not userData['password'] or not userData['confirm_password']:
			error["field_error"] = "All fields are required"
		elif len(userData['password']) < 8 and len(userData['confirm_password'])<8 :
			error['minPass_error'] = "Password must be 8 characters"
		elif len(userData['name']) > 25 or len(userData['name']) < 3 :
			error["name_error"] = "Name must be 3-25 characters"
		elif len(userData['phone']) != 10:
			error["phoneNumber_error"] = "Enter valid phone number."
		elif userData['password'] != userData['confirm_password']:
			error["notMatch_error"] = "Passwords don't match.Try again"	

		return error

# user needs to login before they complete the order
class Login(View):
	return_url = None

	def get(self,request):
		Login.return_url = request.GET.get('return_url')
		return render(request,'login.html')

	def post(self,request):
		userData = request.POST
		customerEmail = Customer.emailExits(userData["email"])
		if customerEmail:
			if check_password(userData["password"],customerEmail.password):
				request.session["customer"] = customerEmail.id
				if Login.return_url:
					return HttpResponseRedirect(Login.return_url)
				else:
					Login.return_url = None
					return redirect('prod')
			else:
				return render(request,'login.html',{"userData":userData,"error":"Email or password doesn't match"})
		else:
			return render(request,'login.html',{"userData":userData,"error":"Email or password doesn't match"})



def logout(request):
	request.session.clear()
	return redirect('home')