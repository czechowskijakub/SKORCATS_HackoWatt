"""
URL configuration for HWServer project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import hello_world, receive_json, graph_data, weather_data

urlpatterns = [
    path('admin/', admin.site.urls),
    path('helloworld/', hello_world, name='helloworld'),
    path('receive-json', receive_json, name='receive_json_no_slash'),
    path('receive-json/', receive_json, name='receive_json'),
    path('receive_json', receive_json, name='receive_json_legacy_no_slash'),
    path('receive_json/', receive_json, name='receive_json_legacy'),
    path('graph-data', graph_data, name='graph_data_no_slash'),
    path('graph-data/', graph_data, name='graph_data'),
    path('weather-data', weather_data, name='weather_graph_data_no_slash'),
    path('weather-data/', weather_data, name='weather_graph_data'),
]
