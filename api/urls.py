from django.urls import path, include

app_name = 'api'

urlpatterns = [
    path('items/', include('api.items.urls'), name='items'),
]
