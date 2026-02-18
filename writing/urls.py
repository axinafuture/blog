from django.urls import path
from . import views

urlpatterns = [
    path('write/', views.write, name='write'),
    path('write/ai-suggest/', views.ai_suggest, name='ai_suggest'),
    path('write/<int:pk>/', views.write, name='write_edit'),
    path('manage/', views.manage, name='manage'),
    path('manage/post/<int:pk>/update/', views.post_update, name='post_update'),
    path('manage/category/', views.category_manage, name='category_manage'),
    path('manage/tag/', views.tag_manage, name='tag_manage'),
    path('delete/<int:pk>/', views.delete, name='delete'),
    path('image-upload/', views.image_upload, name='image_upload'),
    path('manage/ai-summary/', views.generate_ai_summary, name='generate_ai_summary'),
    path('manage/ai-suggest-prompt/', views.save_suggest_prompt, name='save_suggest_prompt'),
    path('manage/contact/<int:pk>/', views.contact_action, name='contact_action'),
]
