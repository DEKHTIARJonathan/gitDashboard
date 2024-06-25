from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()

import login
import login.views

urlpatterns = patterns('',
   # Examples:
   # url(r'^$', 'gitDashBoard.views.home', name='home'),
   # url(r'^gitDashBoard/', include('gitDashBoard.foo.urls')),

   # Uncomment the admin/doc line below to enable admin documentation:
   url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
   # Uncomment the next line to enable the admin:
   url(r'^admin/', include(admin.site.urls)),
   url(r'^rest/', include('rest.urls')),
   url(r'^login', 'login.views.loginView', name="login_view"),
   url(r'^logout', 'login.views.logoutView', name="logout_view"),
   url(r'', include('gitview.urls')),
)
