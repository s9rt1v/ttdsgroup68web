from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('detail/<m_id>', views.detail, name='detail'),
    path('signup/', views.signUp, name='signup'),
    path('login/', views.Login, name='login'),
    path('logout/', views.Logout, name='logout'),
    path('watch/', views.watch, name='watch'),
    path('list/', views.list, name='list')
]
