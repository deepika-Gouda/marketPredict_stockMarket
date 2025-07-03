from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('get_general_stock_news/', views.get_general_stock_news, name='get_general_stock_news'),
   
]



