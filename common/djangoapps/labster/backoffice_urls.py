from django.conf import settings
from django.conf.urls import patterns, include, url


urlpatterns = patterns('labster',  # nopep8
    url(r'^$', 'backoffice.views.home', name="labster_backoffice"),
    url(r'^licenses/$', 'backoffice.views.home', name="labster_backoffice"),
    url(r'^license/new/group/univ', 'backoffice.views.home', name="labster_backoffice"),
    url(r'^license/new/group/hs', 'backoffice.views.home', name="labster_backoffice"),
    url(r'^purchases/$', 'backoffice.views.home', name="labster_backoffice"),
    url(r'^invoice/(?P<paymentId>\d+)/$', 'backoffice.views.home', name="labster_backoffice"),
    url(r'^invoice/(?P<paymentId>\d+)/thank-you/$', 'backoffice.views.home', name="labster_backoffice"),
    url(r'^invoice/(?P<paymentId>\d+)/cancel-order/$', 'backoffice.views.home', name="labster_backoffice"),
    url(r'^invoice/cancel-order/complete/$', 'backoffice.views.home', name="labster_backoffice"),
    url(r'^renew-license/(.+)/$', 'backoffice.views.home', name="labster_backoffice"),
)
