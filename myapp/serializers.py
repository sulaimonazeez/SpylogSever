# serializers.py

from rest_framework import serializers
from .models import Wallet, ProductType,TransactionHistory, ProductCredential

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['balance']


class ProductSerializer(serializers.ModelSerializer):
    in_stock_count = serializers.IntegerField(read_only=True)
    icon_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductType
        fields = ['id', 'name', 'price', 'in_stock_count', 'icon_url']

    def get_icon_url(self, obj):
        request = self.context.get('request')
        if obj.icon and obj.icon.icon:
            return request.build_absolute_uri(obj.icon.icon.url)
        return None
        


class ProductCredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCredential
        fields = ["id", "access_info", "is_sold"]

class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = ["id", "name", "description", "price"]

class TransactionHistorySerializer(serializers.ModelSerializer):
    product = ProductCredentialSerializer()
    product_type = ProductTypeSerializer()

    class Meta:
        model = TransactionHistory
        fields = ["id", "amount", "status", "timestamp", "product", "product_type"]