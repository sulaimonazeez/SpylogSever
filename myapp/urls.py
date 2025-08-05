from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views
from django.urls import path

urlpatterns = [
    path("create/", views.SignupView.as_view(), name="signup"),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("api/product/<int:pk>/", views.ProductDetailView.as_view(), name="product_detail"),
    # All custom admin views should come from views now
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('icons/', views.icon_list, name='icon_list'),
    path('icons/add/', views.add_icon, name='add_icon'),
    path("api/profile", views.UserDetailView.as_view(), name="profile_detail"),
    path('icons/delete/<int:pk>/', views.delete_icon, name='delete_icon'),
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/delete/<int:pk>/', views.delete_product, name='delete_product'),
    path('credentials/', views.credential_list, name='credential_list'),
    path('credentials/add/', views.add_credential, name='add_credential'),
    path('credentials/delete/<int:pk>/', views.delete_credential, name='delete_credential'),
    path('wallets/', views.wallet_list, name='wallet_list'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    path("api/transactions/", views.TransactionHistoryList.as_view(), name="transaction_historys"),
    path("api/wallet/", views.WalletBalanceView.as_view(), name="wallet_balance"),
    path("api/account/details/", views.VirtualAccountGenerate.as_view(), name="AccountDetail"),
    path("api/secret/payment/done/", views.payvessel_payment_done, name="payment_success"),
    path("api/message/", views.MyMessage.as_view(), name="mymessage"),
]