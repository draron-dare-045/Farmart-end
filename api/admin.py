# api/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Animal, Order, OrderItem

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('User Type', {'fields': ('user_type',)}),
        ('Contact Info', {'fields': ('phone_number', 'location')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('user_type', 'phone_number', 'location')}),
    )
    list_display = ('username', 'email', 'user_type', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'groups')
    search_fields = ('username', 'email')

@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('name', 'farmer', 'animal_type', 'price', 'is_sold', 'created_at')
    list_filter = ('animal_type', 'is_sold', 'farmer')
    search_fields = ('name', 'breed', 'farmer__username')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1  
    
    def get_fields(self, request, obj=None):
        if obj:  
            return ('get_animal_details', 'quantity')
        return ('animal', 'quantity')

   
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('get_animal_details', 'quantity')
        return ()

   
    @admin.display(description='Animal Details')
    def get_animal_details(self, obj):
        if obj.animal:
            return f"{obj.animal.name} ({obj.animal.breed}) - Price: ${obj.animal.price}"
        return "Animal not found"

 
    def has_add_permission(self, request, obj=None):
        return obj is None

   
    def has_delete_permission(self, request, obj=None):
        return obj is None

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('id', 'buyer__username')
    ordering = ('-created_at',)
    inlines = [OrderItemInline]

  
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('buyer', 'created_at')
        return ()