from django.conf.urls import patterns, url

from hive_search import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index')
)
