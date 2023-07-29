from django.urls import path

from .views import FileUploadView, TopCustomersView


app_name = 'api_v1'

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='upload-file'),
    path('top/', TopCustomersView.as_view(), name='top-five'),
]
