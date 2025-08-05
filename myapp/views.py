from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.db.models import Sum
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
import random
import traceback  # for debugging
from rest_framework.permissions import IsAuthenticated
from .models import Wallet, ProductType, AccountDetails, FundHistory, Messages
from .service import PayVesselService
from .serializers import WalletSerializer, ProductSerializer, TransactionHistorySerializer
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import Wallet, IconModel, ProductType, ProductCredential, TransactionHistory
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404



class WalletBalanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            wallet = Wallet.objects.get(user=request.user)
        except Wallet.DoesNotExist:
            raise NotFound("Wallet not found.")

        serializer = WalletSerializer(wallet)
        return Response(serializer.data)
        
class ProductDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        product = get_object_or_404(ProductType, id=pk)
        serializer = ProductSerializer(product, context={"request": request})
        return Response(serializer.data)
    def post(self, request, pk):
        product = get_object_or_404(ProductType, id=pk)
        wallet = Wallet.objects.get(user=request.user)
        price = request.data.get("price")
        # Get all unsold credentials for the product type
        if price and float(price) >= wallet.balance:
          wallet.balance -= float(price)
          wallet.save()
          available_credentials = product.credentials.filter(is_sold=False)

          if not available_credentials.exists():
            return Response({"error": "No credentials available for this product."}, status=404)

          # Pick one random credential
          selected_credential = random.choice(list(available_credentials))

          # Optional: mark it as sold (only if you're actually purchasing here)
          selected_credential.is_sold = True
          selected_credential.save()

          # Optional: save transaction history (if you're doing the purchase logic)
          TransactionHistory.objects.create(
             user=request.user,
             product=selected_credential,
             product_type=product,
             amount=product.price,
             status="completed"
          )

          # Return the product info + credential
          serializer = ProductSerializer(product, context={"request": request})
          return Response({
            "product": serializer.data,
            "credential": {
                "id": selected_credential.id,
                "access_info": selected_credential.access_info
            }
          })
        else:
          return Response({"error":"insufficient balance"})



def admin_dashboard(request):
    context = {
        'icon_count': IconModel.objects.count(),
        'product_count': ProductType.objects.count(),
        'credential_count': ProductCredential.objects.count(),
        'wallet_count': Wallet.objects.count(),
        'transaction_count': TransactionHistory.objects.count()
    }
    return render(request, 'admin/dashboard.html', context)


# ==== ICON MODEL ====
def icon_list(request):
    icons = IconModel.objects.all()
    return render(request, 'admin/icon_list.html', {'icons': icons})

def add_icon(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        icon = request.FILES.get('icon')
        IconModel.objects.create(name=name, icon=icon)
        return redirect('icon_list')
    return render(request, 'admin/add_icon.html')

def delete_icon(request, pk):
    icon = get_object_or_404(IconModel, pk=pk)
    icon.delete()
    return redirect('icon_list')


# ==== PRODUCT TYPE ====
def product_list(request):
    products = ProductType.objects.all()
    return render(request, 'admin/product_list.html', {'products': products})

def add_product(request):
    icons = IconModel.objects.all()
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST.get('description', '')
        price = request.POST['price']
        icon_id = request.POST.get('icon')
        icon = IconModel.objects.get(id=icon_id) if icon_id else None
        ProductType.objects.create(name=name, description=description, price=price, icon=icon)
        return redirect('product_list')
    return render(request, 'admin/add_product.html', {'icons': icons})

def delete_product(request, pk):
    product = get_object_or_404(ProductType, pk=pk)
    product.delete()
    return redirect('product_list')


# ==== PRODUCT CREDENTIAL ====
def credential_list(request):
    credentials = ProductCredential.objects.all()
    return render(request, 'admin/credential_list.html', {'credentials': credentials})

def add_credential(request):
    products = ProductType.objects.all()
    if request.method == 'POST':
        product_type_id = request.POST['product_type']
        access_info = request.POST['access_info']
        ProductCredential.objects.create(product_type_id=product_type_id, access_info=access_info)
        return redirect('credential_list')
    return render(request, 'admin/add_credential.html', {'products': products})

def delete_credential(request, pk):
    cred = get_object_or_404(ProductCredential, pk=pk)
    cred.delete()
    return redirect('credential_list')


# ==== WALLET LIST ====
def wallet_list(request):
    wallets = Wallet.objects.all()
    return render(request, 'admin/wallet_list.html', {'wallets': wallets})


# ==== TRANSACTION HISTORY ====
def transaction_list(request):
    transactions = TransactionHistory.objects.select_related('user', 'product_type').all()
    return render(request, 'admin/transaction_list.html', {'transactions': transactions})


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Get wallet
        try:
            wallet = Wallet.objects.get(user=user)
        except Wallet.DoesNotExist:
            return Response({"error": "Wallet not found."}, status=404)

        wallet_data = WalletSerializer(wallet).data

        # Get products
        products = ProductType.objects.all()
        product_data = ProductSerializer(products, many=True, context={"request": request}).data

        return Response({
            "user": {
                "username": user.username,
                "email": user.email
            },
            "wallet": wallet_data,
            "products": product_data
        })


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Fetch completed transactions only
        transactions = TransactionHistory.objects.filter(user=user, status="completed")

        total_spent = transactions.aggregate(total=Sum("amount"))["total"] or 0
        total_orders = transactions.count()

        return Response({
            "username": user.username,
            "email": user.email,
            "total_spent": float(total_spent),  # Optional: cast Decimal to float
            "total_orders": total_orders
        })



class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            username = request.data.get('username')
            email = request.data.get('email')
            password = request.data.get('password')

            if not username or not email or not password:
                return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

            if User.objects.filter(username=username).exists():
                return Response({"error": "Username already taken."}, status=status.HTTP_400_BAD_REQUEST)

            if User.objects.filter(email=email).exists():
                return Response({"error": "Email already in use."}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.create(
                username=username,
                email=email,
                password=make_password(password)
            )

            return Response({
                "message": "User created successfully.",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            # print traceback in the terminal
            traceback.print_exc()
            return Response({"error": f"Internal server error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
  



class TransactionHistoryList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transactions = TransactionHistory.objects.filter(user=request.user)\
            .select_related("product", "product_type")\
            .order_by("-timestamp")  # This ensures latest first
        serializer = TransactionHistorySerializer(transactions, many=True)
        return Response(serializer.data)
        

class VirtualAccountGenerate(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            account_qs = AccountDetails.objects.filter(user=request.user)
            if not account_qs.exists():
                return Response({"message": "account not found", "generate": False}, status=status.HTTP_404_NOT_FOUND)
            
            account_details = account_qs.first()
            return Response({
                "account_number": account_details.account,
                "bank_name": account_details.bank_name
            })
        except Exception as e:
            print("GET error:", e)
            return Response({"error": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        phone_number = request.data.get("phone_number")

        try:
            if not AccountDetails.objects.filter(user=request.user).exists():
                processing = PayVesselService.generate_virtual_account(
                    user=request.user,
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=phone_number
                )
                details = processing['banks'][0]
                created = AccountDetails.objects.create(
                    user=request.user,
                    account=details["accountNumber"],
                    bank_name=details["bankName"],
                    order_ref=details["trackingReference"]
                )
                res = created
            else:
                res = AccountDetails.objects.get(user=request.user)

            return Response({
                "account_number": res.account,
                "bank_name": res.bank_name
            })

        except Exception as e:
            print("POST error:", e)
            return Response({"error": "Something went wrong"}, status=status  .HTTP_500_INTERNAL_SERVER_ERROR)
            
            


@require_POST
@csrf_exempt
def payvessel_payment_done(request):
        payload = request.body
        payvessel_signature = request.META.get('HTTP_PAYVESSEL_HTTP_SIGNATURE')
        
        #this line maybe be differ depends on your server
        #ip_address = u'{}'.format(request.META.get('HTTP_X_FORWARDED_FOR'))
        ip_address = u'{}'.format(request.META.get('REMOTE_ADDR'))
        secret = bytes("PVSECRET-", 'utf-8')
        hashkey = hmac.new(secret,request.body, hashlib.sha512).hexdigest()
        ipAddress = ["3.255.23.38", "162.246.254.36"]
        if payvessel_signature == hashkey  and ip_address in ipAddress:
                data = json.loads(payload)
                amount = float(data['order']["amount"])
                reference = data['transaction']["reference"]
                if not FundHistory.objects.filter(reference=reference).exists():
                   FundHistory.objects.create(user=request.user, amount=amount, reference=reference)
                   wallets = Wallet.objects.get(user=request.user)
                   wallets.balance = wallets.balance + amount
                   wallets.save()
                   
                   return JsonResponse({"message": "success",},status=200) 
                        
                else:
                    return JsonResponse({"message": "transaction already exist",},status=200) 
        
        else:
            return JsonResponse({"message": "Permission denied, invalid hash or ip address.",},status=400) 
            
            

class MyMessage(APIView):
  permission_classes = [AllowAny]
  
  def post(self, request):
    name = request.data.get("name")
    email = request.data.get("email")
    message = request.data.get("message")
    
    if (name and email and message):
      Messages.objects.create(name=name, email=email, message=message)
      return Response({"message":"Sucessfully sent"},status=status.HTTP_201_CREATED)
    else:
      return Response({"message":"failed to send message"}, status=status.HTTP_400_BAD_REQUEST)
  