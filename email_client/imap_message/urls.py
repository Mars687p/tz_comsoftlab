from django.urls import path

from . import views

app_name = 'imap_message'

urlpatterns = [
    path('', views.MessageViews.as_view(), name='index'),
    path('<int:mail_client_id>/', views.MessageViews.as_view()),

]
