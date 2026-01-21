from django.urls import path
from . import views

urlpatterns = [
    
    path('', views.read_student, name='read_student'),
    path('create/', views.create_student, name='create_student'),
    path('update/<int:id>/', views.update_student, name='update_student'),
    path('delete/<int:id>/', views.delete_student, name='delete_student'),

    path('signup/', views.signup, name='signup'),

    path('activity-logs/', views.activity_logs, name='activity_logs'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('recycle-bin/', views.recycle_bin, name='recycle_bin'),
    path('restore/<int:id>/', views.restore_student, name='restore_student'),

    path('import/', views.import_students, name='import_students'),
    path('export/excel/', views.export_students_excel, name='export_students_excel'),
    path('export/pdf/', views.export_students_pdf, name='export_students_pdf'),

    
]
