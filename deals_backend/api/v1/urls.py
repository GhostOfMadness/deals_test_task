from django.urls import path

from .views import FileUploadView


app_name = 'api_v1'

urlpatterns = [
    path('upload/', FileUploadView.as_view()),
]
