from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()
from adminactions import actions
actions.add_to_site(admin.site)

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'student_reg.views.index', name='home'),
    url(r'^register$', 'student_reg.views.query'),

    # url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'admin/login.html'}),
    # url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^accounts/', include('registration.backends.default.urls')),

    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
