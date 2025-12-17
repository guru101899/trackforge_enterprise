from django.contrib import admin
from .models import Supplier, PurchaseOrder, POLineItem


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone','updated_by')
    search_fields = ('name', 'email')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')


    def save_model(self, request, obj, form, change):
        # 1. If we are creating it for the first time
        if not obj.pk:
            obj.created_by = request.user

        # 2. Every time we save (including updates), record the user
        obj.updated_by = request.user

        # 3. Actually save the record to the database
        super().save_model(request, obj, form, change)
class POLineItemInline(admin.TabularInline):
    """Allows adding products directly inside the Purchase Order page"""
    model = POLineItem
    extra = 1  # Shows one empty row by default
    fields = ('product', 'quantity', 'unit_price')


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('reference_number', 'supplier', 'warehouse', 'status', 'order_date')
    list_filter = ('status', 'order_date', 'supplier')
    search_fields = ('reference_number', 'supplier__name')

    # We add the Inline here
    inlines = [POLineItemInline]

    # Safety: These should be filled automatically, not by hand
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')

    # Fieldsets make the form look organized
    fieldsets = (
        ("Order Info", {
            'fields': ('reference_number', 'supplier', 'warehouse', 'status')
        }),
        ("Audit Trail", {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',),  # Hides this section by default
        }),
    )

    def save_model(self, request, obj, form, change):
        """Automatically set the created_by user when saving"""
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)