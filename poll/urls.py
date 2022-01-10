from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from poll import views

app_name = 'poll'

urlpatterns = [
    # Login Pages
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_page, name='logout'),
    path('register/', views.register_page, name='register'),

    # Election Pages
    path('', views.hello, name='hello'),
    path('vote/', views.vote, name='vote'),
    path('notifications/', views.notifications, name='notifications'),
    path('choice/', views.candidates, name='choice', kwargs={'template_name': 'poll/choice.html'}),
    path('access-is-forbidden/', views.notice_access_is_forbidden, name='notice-access-is-forbidden'),
    path('results/', views.candidates, name='results', kwargs={'template_name': 'poll/results.html'}),
    path('candidates/', views.candidates, name='candidates', kwargs={'template_name': 'poll/candidates.html'}),
    path('detail/<int:candidate_id>/', views.detail, name='detail', kwargs={'template_name': 'poll/detail.html'}),

    # Participate Pages
    path('participate-sent/', views.notice_participate_sent, name='participate-sent'),
    path('participate/', views.create_participate_form, name='create-participate-form'),
    path('update-sent/', views.notice_participate_update_sent, name='participate-update-sent'),
    path('participate/<str:author>/', views.update_participate_form, name='update-participate-form'),
    path('change-status/', views.notice_participate_change_status, name='participate-warning-change-status'),
    path('candidate-already-exists', views.notice_participate_candidate_already_exists,
         name='participate-warning-candidate-already-exists'),

    # Moderator's Pages
    path('moderator-hello/', views.moderator_page, name='moderator-hello'),
    path('moderate/', views.moderator_moderate, name='moderator-moderate'),
    path('instruction/', views.moderator_instruction, name='moderator-instruction'),
    path('refuse/<int:candidate_id>/', views.moderator_refuse, name='moderator-refuse'),
    path('edit-instruction/', views.moderator_edit_instruction, name='moderator-edit-instruction'),
    path('candidate-refused/', views.notice_moderator_candidate_refused, name='notice-moderator-candidate-refused'),
    path('instruction-saved/', views.notice_moderator_instruction_saved, name='notice-moderator-instruction-saved'),
    path('candidate-accepted/', views.notice_moderator_candidate_accepted, name='notice-moderator-candidate-accepted'),
    path('moderator-candidates/', views.candidates, name='moderator-candidates',
         kwargs={'template_name': 'poll/moderator-candidates.html'}),
    path('moderator-detail/<int:candidate_id>', views.detail, name='moderator-detail',
         kwargs={'template_name': 'poll/moderator-detail.html'}),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
