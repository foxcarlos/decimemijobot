from django.conf.urls import url


from . import views
from .views import Login

urlpatterns = [                                                                                                                      
    url(r'^$', views.index, name='index'),
    url(r'^test', views.test, name='test'),
    url(r'login/$', Login.as_view(), name='login'),
]
