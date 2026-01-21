from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Student, AuditLog
from .middleware import get_current_user

@receiver(post_save, sender=Student)
def log_student_save(sender, instance, created, **kwargs):
    user = get_current_user()
    print("CURRENT USER IN SIGNAL:", user)

    if created:
    
        action = 'CREATED',
        description=f"Student '{instance.name}' was created"
    else:
        
        action = 'UPDATED',
        description=f"Student '{instance.name}' was updated"

        AuditLog.objects.create(
            user=user,
            action=action,
            description=description
        )


    


@receiver(post_delete, sender=Student)
def log_student_delete(sender, instance, **kwargs):
    user = get_current_user()
    AuditLog.objects.create(
        user=user,
        action='DELETED',
        description=f"Student '{instance.name}' was deleted"
    )


from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    AuditLog.objects.create(
        user=user,
        action='LOGIN',
        #model_name='User',
        #object_id=user.id,
        description=f"User '{user.username}' logged in"
    )


from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver
from .models import AuditLog

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    AuditLog.objects.create(
        user=user,
        action='LOGOUT',
        description=f"User {user.username} logged out"
    )
