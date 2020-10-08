"""maps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path
from .views import properties, layers, statistics, legends, download

urlpatterns = [
    path('props/<int:pk>', properties, name='wfs-properties'),
    path('layers/<int:pk>', layers, name='wfs-layers'),
    path('legends/<int:pk>', legends, name='wfs-legends'),
    path('stats/<int:pk>', statistics, name='wfs-statistics'),
    path('download/<int:pk>', download, name='ogc-download'),
]
