from django.conf.urls import url
from django.conf.urls.static import static
from web import settings
import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^save/$', views.save, name='save'),
    url(r'^add/$', views.add, name='add'),
    url(r'^delete/$', views.delete, name='delete'),
    url(r'^update/$', views.update, name='update'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

