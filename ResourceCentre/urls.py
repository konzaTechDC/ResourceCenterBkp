"""
Definition of urls for ResourceCentre.
"""

from datetime import datetime
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from app import forms, views
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

admin.site.site_header = "KOTDA Admin"
admin.site.site_title = "KOTDA Admin Portal"
admin.site.index_title = "Welcome to KOTDA Resource Centre"

urlpatterns = [
    url(r'^$', views.landing_page, name='home-page'),
    url('dashboard/', views.home, name='dashboard'),
    #url(r'^login/$', auth_views.login, {'template_name': 'auth/signin.html'}, name='login'),
    #url(r'^logout/$', auth_views.logout, {'next_page': 'login'}, name='logout'),
    path('signup/', views.signup, name='signup'),
    url(r'^account_activation_sent/$', views.account_activation_sent, name='account_activation_sent'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),

    path('', include(('app.urls', "app"), "appurls")),
    path('contact', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('seed/', views.seed, name='seed'),
    path('seed/department/', views.seed_departments, name='seed_department'),
    path('login/', 
        LoginView.as_view
        (
            template_name='auth/signin.html', 
            #authentication_form=forms.BootstrapAuthenticationForm,
            extra_context =
            {
                'title': 'Log in',
                'year': datetime.now().year,
            }
         ),
        name='login'),


    path('password-reset/', 
        auth_views.PasswordResetView.as_view(
            template_name='user_auth/password_reset.html'
            ), 
        name='password_reset'),
    path('password-reset/done/', 
        auth_views.PasswordResetDoneView.as_view(
            template_name='user_auth/password_reset_done.html'
            ), 
        name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(
            template_name='user_auth/password_reset_confirm.html'
            ), 
        name='password_reset_confirm'),
    path('password-reset-complete/', 
        auth_views.PasswordResetCompleteView.as_view(
            template_name='user_auth/password_reset_complete.html'
            ), 
        name='password_reset_complete'),

     #update user password
    path('user/update/password/', views.change_password, name='change_password'),


    path('profile/update/post/', views.update_user_profile, name='update_user_profile'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('admin/', admin.site.urls),
    url('^', include('django.contrib.auth.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    path('summernote/', include('django_summernote.urls')),

     #####################################################################################
    #######=============Learning resource urls=======#####

    
    path('create_learning_resource/post/', views.create_learning_resource, name='create_learning_resource'),
    path('update_learning_resource/<int:resource_id>', views.get_update_learning_resource, name='get_update_learning_resource'),
    path('update_learning_resource/post/', views.post_update_learning_resource, name='post_update_learning_resource'),
    path('list_learning_resource/<int:creator_id>/', views.list_creator_courses, name='list_creator_courses'),
    path('list_published_courses/<int:creator_id>/', views.list_creator_published_courses, name='list_creator_published_courses'),
    path('list_pending_courses/<int:creator_id>/', views.list_creator_pending_courses, name='list_creator_pending_courses'),
    path('list_draft_courses/<int:creator_id>/', views.list_creator_draft_courses, name='list_creator_draft_courses'),
    path('list_saved_courses/<int:creator_id>/', views.list_creator_saved_courses, name='list_creator_saved_courses'),
    path('list_courses/all/published', views.list_all_courses, name='list_all_courses'),
    #search courses
    path('search_learning_resource/post/key/', views.search_learning_resource, name='search_learning_resource'),
    #mark module as finished
    path('learning_module/post/complete/', views.module_mark_complete, name='module_mark_complete'),

    path('view_learning_resource/<int:id>', views.view_learning_resource, name='view_learning_resource'),
    path('remove_learning_resource/<int:id>', views.remove_learning_resource, name='remove_learning_resource'),
    path('learning_resource_analytics/<int:id>', views.learning_resource_analytics, name='learning_resource_analytics'),
    #enrol course button
    path('learning_resource/enrol/<int:resource_id>', views.enrol_course, name='enrol_course'),
    #enrol course button
    path('learning_resource/quit/<int:resource_id>', views.unrol_course, name='unrol_course'),
    #subimt course review
    path('create_learning_resource/post/review', views.post_course_review, name='post_course_review'),
    path('create_learning_module/<int:id>', views.create_learning_module, name='create_learning_module'),
    path('update_learning_module/<int:id>', views.update_learning_module, name='update_learning_module'),
    path('list_learning_module/<int:id>', views.list_learning_module, name='list_learning_module'),
    path('view_learning_module/<int:id>', views.view_learning_module, name='view_learning_module'),
    path('remove_learning_module/<int:id>', views.remove_learning_module, name='remove_learning_module'),
    #####################################################################################


         #####################################################################################
    #######=============Repository resource urls=======#####
    path('create_repository_resource/', views.get_create_repo_resource, name='get_create_repo_resource'),
    path('create_repository_resource/<str:upload_type>', views.get_create_repo_resource, name='get_create_repo_resource'),
    path('create_repository_resource/post', views.create_repo_resource, name='create_repo_resource'),
    #create document type / folder
    path('create_repo_doc_type/post', views.create_document_folder, name='create_document_folder'),
    #create document type / folder
    path('update/folder/post', views.update_document_folder, name='update_document_folder'),
    path('update_repository_resource/<int:repository_id>', views.get_update_repo_resource, name='get_update_repo_resource'),
    #publish resource
    path('publish/<int:resource_id>', views.publish_resource, name='publish_resource'),
    #get by tab/step
    path('update_repository_resource/<int:repository_id>/<str:step>', views.get_update_repo_resource, name='get_update_repo_resource'),
    path('update_repository_resource/post/', views.post_update_repo_resource, name='post_update_repo_resource'),
    #view repository media
    path('view_repository/<int:resource_id>/media', views.view_repository_media, name='view_repository_media'),
     #search repository
    path('search/repository/', views.search_repository, name='search_repository'),

    #get repository index
    path('repository/index', views.repository_index, name='repository_index'),
    #get repository articles by dept
    path('repository/articles/<int:dept_id>/', views.get_repo_articles_by_dept, name='get_repo_articles_by_dept'),
    #get repository resources by dept
    path('repository/department/<int:dept_id>/', views.filter_repo_by_dept, name='filter_repo_by_dept'),
    #get repository images by dept
    path('repository/images/<int:dept_id>/', views.get_repo_images_by_dept, name='get_repo_images_by_dept'),
     #get repository videos by dept
    path('repository/videos/<int:dept_id>/', views.get_repo_videos_by_dept, name='get_repo_videos_by_dept'),
    #get repository by folder
    path('repository/folder/<int:folder_id>/', views.filter_repo_by_folder, name='filter_repo_by_folder'),
    
    #download a document
    path('repository/document/download/<int:document_id>/', views.download_file, name='download_file'),
     #play video
    path('play_repo_video/<int:video_id>', views.play_repo_video, name='play_repo_video'),
     #view image
    path('view/image/<int:image_id>', views.view_image, name='view_image'),
     #view document
    path('view/document/<int:document_id>', views.view_document, name='view_document'),
    
     #get user dashboard
    path('repository/user/dashboard/<int:user_id>/<str:tab>/', views.get_user_dashboard, name='get_user_dashboard'),

    #check repo capacity
    path('check_repo_capacity/<int:resource_id>', views.check_repo_capacity, name='check_repo_capacity'),
    #delete image
    path('remove_repo_image/<int:image_id>', views.delete_repo_image, name='delete_repo_image'),
    #delete document
    path('remove_repo_document/<int:document_id>', views.delete_repo_document, name='delete_repo_document'),
     #delete video
    path('remove_repo_video/<int:video_id>', views.delete_repo_video, name='delete_repo_video'),
     #delete folder
    path('remove_repo_folder/<int:folder_id>', views.delete_repo_folder, name='delete_repo_folder'),
    
     #bookmark a document
    path('repository/bookmark/post/document/', views.bookmark_document, name='bookmark_document'),
    #bookmark a document
    path('repository/bookmark/post/image/', views.bookmark_image, name='bookmark_image'),
    #bookmark a video
    path('repository/bookmark/post/video/', views.bookmark_video, name='bookmark_video'),
     #go to my bookmark
    path('repository/bookmark/get/all/', views.get_my_bookmarks, name='get_my_bookmarks'),



    #basic upload
    url(r'^basic-upload/$', views.BasicUploadView.as_view(), name='basic_upload'),

    #file upload
    #path('file-upload/', views.file_upload, name='file_upload'),
    #####################################################################################


    #####################################################################################
    #######=============Password reset urls=======##### url(r'^password_reset/$', auth_views.PasswordChangeView.as_view(), name='password_reset'),
    url(r'^password_reset/done/$', auth_views.PasswordChangeDoneView.as_view(), name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    #####################################################################################################################
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

        
admin.site.site_header = "KoTDA | Resource Center Admin"
admin.site.site_title = "KoTDA | Resource Center Admin Portal"
admin.site.index_title = "KoTDA | Resource Center Admin Portal"