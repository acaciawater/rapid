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
from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from django.conf import settings
from django.conf.urls.static import static
from .views import MapDetailView, HomeView, BrowseView, OverlayView,\
    map_proxy, toggle, reorder, get_map, docs2tree

urlpatterns = [
    path('', HomeView.as_view()),
    path('home', HomeView.as_view(),name='home'),
    path('browse', BrowseView.as_view(),name='browse'),
    path('view', OverlayView.as_view(),name='view'),
    path('admin/', admin.site.urls),
    path('ows/', include('ogc.urls')),
    path('map/<int:pk>/reorder/', reorder,name='map-reorder'),
    path('map/<int:mapid>/toggle/<int:layid>', toggle,name='map-toggle'),
    path('map/<int:pk>/config/', get_map, name='map-config'),
    path('map/<int:pk>/', MapDetailView.as_view(),name='map-detail'),
    path('map', map_proxy, name='cluster-view'),
    path('tree', docs2tree),
    
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
