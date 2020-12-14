from django.contrib import admin

from .models import Item, OrderItem, Order, UserProfile



class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ordered'
                    ]
    list_display_links = [
        'user'
    ]
    list_filter = ['ordered']
    search_fields = [
        'user__username',
        'ref_code'
    ]


admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(UserProfile)
