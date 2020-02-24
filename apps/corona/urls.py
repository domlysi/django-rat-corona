from django.urls import path
from . import views


urlpatterns = [
    path('new/', views.RegisterClientView.as_view()),
    path('commands/', views.CommandsView.as_view()),
    path('command/result/<uuid>/', views.CommandResultView.as_view()),
    path('command/results/', views.CommandResultListView.as_view()),
]