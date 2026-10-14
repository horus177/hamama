from django.contrib import admin
from .models import LoftOrRoom, ProductionRecord, Expense, Sale

admin.site.register(LoftOrRoom)
admin.site.register(ProductionRecord)
admin.site.register(Expense)
admin.site.register(Sale)