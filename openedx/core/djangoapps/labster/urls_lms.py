from django.conf.urls import url

urlpatterns = (
    url(
        r'^login/', 'openedx.core.djangoapps.labster.login.views.login',
        name='login'
    ),
)
