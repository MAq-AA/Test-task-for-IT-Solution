from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('add-quote/', views.add_quote, name='add_quote'),
    path('popular-quotes/', views.popular_quotes, name='popular_quotes'),
    path('toggle-like-dislike/<int:quote_id>/', views.toggle_like_dislike, name='toggle_like_dislike')
]