from django.contrib import admin
from .models import Category, Property, Loaner, PropertyLoan


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'category', 'quantity_total',
                    'quantity_available', 'status', 'unit_price')
    list_filter = ('status', 'category')
    search_fields = ('code', 'name')


@admin.register(Loaner)
class LoanerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'email', 'is_member')
    search_fields = ('full_name', 'phone', 'id_number')


@admin.register(PropertyLoan)
class PropertyLoanAdmin(admin.ModelAdmin):
    list_display = ('loan_code', 'property_item', 'loaner', 'quantity',
                    'loan_date', 'expected_return_date', 'status')
    list_filter = ('status', 'loan_date')
    search_fields = ('loan_code', 'loaner__full_name', 'property_item__name')