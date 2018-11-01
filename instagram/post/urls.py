from django.conf.urls import url

from . import views

app_name = 'post'

urlpatterns = [
    url(r'^$', views.post_list, name='post_list'),
    url(r'^create/$', views.post_create, name='post_create'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^reward/$', views.reward, name='reward'),
    url(r'^reward_list/$', views.reward_list, name='reward_list'),
    url(r'^(?P<post_pk>\d+)/$', views.post_detail, name='post_detail'),
    url(r'^(?P<post_pk>\d+)/like-toggle/$', views.post_like_toggle, name='post_like_toggle'),
    url(r'^(?P<post_pk>\d+)/comment/create/$', views.comment_create, name='comment_create'),
]
