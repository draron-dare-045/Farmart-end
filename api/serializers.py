from rest_framework import serializers
from .models import User, Animal, Order, OrderItem
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from .models import User

class CustomUserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ('id', 'username', 'email', 'password', 'user_type', 'phone_number', 'location')

# serializers.py
from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    re_password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 're_password', 'user_type', 'phone_number', 'location']
        extra_kwargs = {
            'password': {'write_only': True, 'style': {'input_type': 'password'}},
            'email': {'required': True}
        }

    def validate(self, data):
        if data['password'] != data['re_password']:
            raise serializers.ValidationError({"re_password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('re_password')  # Remove re_password before creating the user
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user



class AnimalSerializer(serializers.ModelSerializer):
    farmer_username = serializers.CharField(source='farmer.username', read_only=True)

    class Meta:
        model = Animal
        fields = [
            'id', 'farmer', 'farmer_username', 'name', 'animal_type', 'breed',
            'age', 'price', 'description', 'image', 'is_sold', 'created_at'
        ]
        read_only_fields = ['farmer', 'is_sold']

class OrderItemReadSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='animal.name', read_only=True)
    price = serializers.DecimalField(source='animal.price', max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'animal', 'name', 'price', 'quantity']

class OrderItemWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['animal', 'quantity']

class OrderReadSerializer(serializers.ModelSerializer):
    items = OrderItemReadSerializer(many=True, read_only=True)
    buyer_username = serializers.CharField(source='buyer.username', read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'buyer_username', 'status', 'created_at', 'items', 'total_price']

    def get_total_price(self, obj):
        return sum(item.animal.price * item.quantity for item in obj.items.all())

class OrderWriteSerializer(serializers.ModelSerializer):
    items = OrderItemWriteSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'items', 'status']
        read_only_fields = ['status']

    def create(self, validated_data):
        items_data = validated_data.pop('items')

        order = Order.objects.create(**validated_data, status=Order.OrderStatus.PENDING)
        
        for item_data in items_data:
            animal = item_data['animal']
            if animal.is_sold:
                raise serializers.ValidationError(f"Cannot add to cart. Animal '{animal.name}' is already sold.")
            
            OrderItem.objects.create(order=order, **item_data)
        
        return order