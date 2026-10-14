from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('dashpoard/', views.farm_home_view, name='farm_home'),
    path('pair/<int:pair_id>/', views.pair_detail_view, name='pair_detail'),
    
    path('production/add/', views.add_production_view, name='add_production'),
    path('pair/add/', views.add_pair_view, name='add_pair'),
    path('room/add/', views.add_room_view, name='add_room'),
    path('sale/add/', views.add_sale_view, name='add_sale'),
    path('expense/add/', views.add_expense_view, name='add_expense'),
    # ... بقية المسارات الخاصة بك ...
    path('hatch-history/', views.hatch_history_view, name='hatch_history'),
    # ... مساراتك الحالية ...
    path('pairs/', views.pairs_list_view, name='pairs_list'),
    path('pairs/<int:pair_id>/edit/', views.edit_pair_view, name='edit_pair'),

    # ... المسارات الحالية لديك ...
    path('sales-history/', views.sales_history, name='sales_history'),
    path('deaths-history/', views.deaths_history, name='deaths_history'),
    path('production/<int:record_id>/mark-dead/', views.mark_egg_as_dead, name='mark_egg_as_dead'),

    path('expenses-history/', views.expenses_history, name='expenses_history'),

]