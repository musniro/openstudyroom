from django.conf.urls import url

from . import views

app_name = 'tournament'
urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^results$', views.index, name='results'),
]
