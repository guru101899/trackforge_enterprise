from django.contrib import admin
from .models import Category, Warehouse, Product, Stock, StockTransaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    prepopulated_fields = {'slug': ('name',)}  # Automatically fills slug while you type name


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'code','location','is_active')
    list_filter = ('is_active',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('sku', 'name', 'category', 'cost_price', 'reorder_level')
    # Add a search bar for name and SKU
    search_fields = ('name', 'sku')
    # Filter by category on the right side
    list_filter = ('category',)


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('product', 'warehouse', 'quantity', 'updated_at')


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_type', 'stock', 'quantity_changed', 'stock_after_transaction', 'created_at')
    readonly_fields = ('created_at',)  # Transactions should never be edited