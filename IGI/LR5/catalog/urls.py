from django.urls import path, re_path
from . import views
app_name = 'catalog'
urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('news/', views.news_list, name='news'),
    path('news/<int:pk>/', views.news_detail, name='news_detail'),
    path('glossary/', views.glossary, name='glossary'),
    path('contacts/', views.contacts, name='contacts'),
    path('privacy/', views.privacy, name='privacy'),
    path('vacancies/', views.vacancies, name='vacancies'),
    path('reviews/', views.reviews, name='reviews'),
    path('promo-codes/', views.promo_codes, name='promo_codes'),
    path('products/', views.product_list, name='products'),
    re_path(r'^products/code/(?P<code>[\w-]+)/$', views.product_detail_by_code, name='product_detail_by_code'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('stats/', views.stats, name='stats'),
    path('apis/', views.api_demo, name='api_demo'),
    path('api/summary/', views.api_summary, name='api_summary'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    re_path(r'^manage/(?P<model_key>[\w-]+)/$', views.model_list, name='model_list'),
    re_path(r'^manage/(?P<model_key>[\w-]+)/add/$', views.model_create, name='model_create'),
    re_path(r'^manage/(?P<model_key>[\w-]+)/(?P<pk>\d+)/edit/$', views.model_update, name='model_update'),
    re_path(r'^manage/(?P<model_key>[\w-]+)/(?P<pk>\d+)/delete/$', views.model_delete, name='model_delete'),
]
