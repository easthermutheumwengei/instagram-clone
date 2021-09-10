from django.conribs import admin
from django.urls import path,include
from.import views

urlpatterns=[
    path('',views.home,name='home'),

]