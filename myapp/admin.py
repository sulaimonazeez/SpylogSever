from django.contrib import admin
from .models import Wallet, IconModel, ProductType, ProductCredential, TransactionHistory, AccountDetails, FundHistory, Messages

admin.site.register(Wallet)
admin.site.register(IconModel)
admin.site.register(ProductType)
admin.site.register(ProductCredential)
admin.site.register(TransactionHistory)
admin.site.register(AccountDetails)
admin.site.register(FundHistory)
admin.site.register(Messages)
