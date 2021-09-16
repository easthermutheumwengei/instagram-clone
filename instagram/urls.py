from.import views
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path

urlpatterns = [
    path('',views.home,name='home'),
    path('accounts/signin', views.LoginView.as_view(), name="signin"),
    path('accounts/signout', views.signout, name='signout'),
    path('accounts/signup',views.signup, name='signup'),
    path('accounts/profile/<int:id>',views.profile, name='profile'),
    path('search/', views.search_results, name='search'),
    path('post/view/<int:id>', views.view_post, name='view_post'),
    path('ajax/post-likes', views.post_likes, name='post_likes'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
