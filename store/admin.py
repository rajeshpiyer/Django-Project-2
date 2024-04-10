from django.contrib import admin
from .models import Address, Category,Brand, Product, Cart, Order, Wishlist

# Register your models here.
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'locality', 'city', 'state')
    list_filter = ('city', 'state')
    list_per_page = 10
    search_fields = ('locality', 'city', 'state')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'category_image', 'is_active', 'is_featured', 'updated_at')
    list_editable = ('slug', 'is_active', 'is_featured')
    list_filter = ('is_active', 'is_featured')
    list_per_page = 10
    search_fields = ('title', 'description')
    prepopulated_fields = {"slug": ("title", )}

class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    list_per_page = 10
    search_fields = ('name',)
    

class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category','brand', 'stock', 'is_active', 'is_featured')
    list_editable = ('stock', 'is_active', 'is_featured')
    list_filter = ('category','brand', 'is_active', 'is_featured')
    list_per_page = 20
    search_fields = ('title', 'category','brand', 'short_description')
    prepopulated_fields = {"slug": ("title", )}

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'created_at')
    list_editable = ('quantity',)
    list_filter = ('created_at',)
    list_per_page = 20
    search_fields = ('user', 'product')

class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product')
    list_filter = ('created_at',)
    list_per_page = 20
    search_fields = ('user', 'product')


class OrderAdmin(admin.ModelAdmin):
    list_display = ('user','address','product', 'quantity', 'status', 'ordered_date')
    list_editable = ('status',)
    list_filter = ('status', 'ordered_date')
    list_per_page = 20
    search_fields = ('user', 'product')


admin.site.register(Address, AddressAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Wishlist, WishlistAdmin)
admin.site.register(Order, OrderAdmin)