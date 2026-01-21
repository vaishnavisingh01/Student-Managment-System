from django.db import models
from datetime import timedelta, datetime
from django.core.exceptions import ValidationError

# ---------------- VALIDATORS ----------------

def validate_contact_number(value):
    if not value.isdigit():
        raise ValidationError("Contact number must contain only digits.")
    if len(value) != 10:
        raise ValidationError("Contact number must be exactly 10 digits.")
    if value.startswith('0'):
        raise ValidationError("Contact number must not start with 0.")


# ---------------- PARENT CLASS ----------------

class BasePerson(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    age = models.IntegerField()
    contact_no = models.CharField(
        max_length=10,
        validators=[validate_contact_number]
    )

    class Meta:
        abstract = True   # 👈 Parent only, no table created

    def clean(self):
        if self.age <= 17 or self.age >= 100:
            raise ValidationError("Age must be between 18 and 99")


# ---------------- CHILD CLASS ----------------

class Student(BasePerson):
    date_of_joining = models.DateField()
    internship_period = models.IntegerField(help_text="Duration in months")
    completion_date = models.DateField(blank=True, null=True)

    is_deleted = models.BooleanField(default=False)   

    def save(self, *args, **kwargs):
        if isinstance(self.date_of_joining, str):
            self.date_of_joining = datetime.strptime(
                self.date_of_joining, "%Y-%m-%d"
            ).date()

        months = int(self.internship_period)
        self.completion_date = self.date_of_joining + timedelta(days=30 * months)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class StudentDocument(models.Model):
    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        related_name="documents"
    )

    marksheet_10 = models.FileField(
        upload_to='marksheets/10th/',
        blank=True,
        null=True
    )

    marksheet_12 = models.FileField(
        upload_to='marksheets/12th/',
        blank=True,
        null=True
    )
    

    def __str__(self):
        return f"Documents of {self.student.name}"



from django.contrib.auth.models import User

class ActivityLog(models.Model):
    ACTION_CHOICES = (
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=50)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} {self.action} {self.model_name} at {self.timestamp}"
    

from django.db import models
from django.contrib.auth.models import User

class AuditLog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    action = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} at {self.created_at}"
