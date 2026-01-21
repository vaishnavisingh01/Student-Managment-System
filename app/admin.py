from django.contrib import admin
from .models import Student, StudentDocument
from .models import ActivityLog


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'serial_no',
        'name',
        'email',
        'age',
        'date_of_joining',
        'internship_period',
        'completion_date',
    )

    def serial_no(self, obj):
        return obj.id

    serial_no.short_description = 'S.No'
    
    search_fields = ('name', 'email')
    list_filter = ('date_of_joining',)


@admin.register(StudentDocument)
class StudentDocumentAdmin(admin.ModelAdmin):
    list_display = ('student',)


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'model_name', 'object_id', 'timestamp')
    list_filter = ('action', 'model_name', 'timestamp')
    search_fields = ('user__username', 'model_name')
    ordering = ('-timestamp',)
