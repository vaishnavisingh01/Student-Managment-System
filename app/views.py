from django.shortcuts import render, redirect,get_object_or_404
from .models import Student, StudentDocument
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import ActivityLog


@login_required
def create_student(request):
    if request.method == "POST":
        try:
            # Create Student object (NOT saved yet)
            student = Student(
                name=request.POST['name'],
                email=request.POST['email'],
                age=request.POST['age'],
                contact_no=request.POST['contact_no'],
                date_of_joining=request.POST['date_of_joining'],
                internship_period=request.POST['internship_period'],
            )

            # Run validations
            student.full_clean()

            # Save student
            student.save()

            ActivityLog.objects.create(
                user=request.user if request.user.is_authenticated else None,
                action='CREATE',
                model_name='Student',
                object_id=student.id
            )


            # Save marksheets (child model)
            StudentDocument.objects.create(
                student=student,
                marksheet_10=request.FILES.get('marksheet_10'),
                marksheet_12=request.FILES.get('marksheet_12'),
            )

            # SUCCESS MESSAGE (THIS IS WHERE IT GOES)
            messages.success(request, "Student added successfully!")

            return redirect('read_student')

        except ValidationError as e:
            # Validation failed → show error
            return render(
                request,
                'create_student.html',
                {'errors': e.message_dict}
            )

    return render(request, 'create_student.html')



#update_student view
from django.shortcuts import get_object_or_404
@login_required
def update_student(request, id):
    student = get_object_or_404(Student, id=id)

    # Get or create related document (child)
    document, created = StudentDocument.objects.get_or_create(student=student)

    if request.method == "POST":
        try:
            # Update student fields
            student.name = request.POST['name']
            student.email = request.POST['email']
            student.age = request.POST['age']
            student.contact_no = request.POST['contact_no']
            student.date_of_joining = request.POST['date_of_joining']
            student.internship_period = request.POST['internship_period']

            # Run validations
            student.full_clean()

            # Save student
            student.save()


            ActivityLog.objects.create(
                user=request.user if request.user.is_authenticated else None,
                action='UPDATE',
                model_name='Student',
                object_id=student.id
            )


            # Update marksheets if uploaded
            if 'marksheet_10' in request.FILES:
                document.marksheet_10 = request.FILES['marksheet_10']

            if 'marksheet_12' in request.FILES:
                document.marksheet_12 = request.FILES['marksheet_12']

            document.save()

            # SUCCESS MESSAGE (THIS IS THE LINE YOU ASKED ABOUT)
            messages.success(request, "Student updated successfully!")

            return redirect('read_student')

        except ValidationError as e:
            # Validation failed → show errors on same page
            return render(
                request,
                'update_student.html',
                {
                    'student': student,
                    'document': document,
                    'errors': e.message_dict
                }
            )

    return render(request, 'update_student.html', {
        'student': student,
        'document': document
    })

from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

@login_required
def read_student(request):

    # ✅ 1. BASE QUERYSET — ONLY NON-DELETED STUDENTS
    students = Student.objects.filter(is_deleted=False)

    # 🔍 2. SEARCH
    query = request.GET.get('q', '')
    if query:
        students = students.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(contact_no__icontains=query)
        )

    # 🔽 3. SORTING
    sort = request.GET.get('sort', '')
    direction = request.GET.get('dir', 'asc')

    order_prefix = '' if direction == 'asc' else '-'

    if sort == 'name':
        students = students.order_by(f'{order_prefix}name')
    elif sort == 'age':
        students = students.order_by(f'{order_prefix}age')
    elif sort == 'joining':
        students = students.order_by(f'{order_prefix}date_of_joining')
    elif sort == 'completion':
     students = students.order_by(f'{order_prefix}completion_date')

    age_filter = request.GET.get('age_filter')

    if age_filter == '18-25':
        students = students.filter(age__range=(18, 25))
    elif age_filter == '26-40':
        students = students.filter(age__range=(26, 40))
    elif age_filter == '41-60':
        students = students.filter(age__range=(41, 60))



    # 🎯 4. FILTER (TOP N)
    limit = request.GET.get('limit')
    if limit in ['5', '10', '20']:
        students = students[:int(limit)]

    # 📄 5. PAGINATION
    paginator = Paginator(students, 7)  # 7 students per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 📦 6. CONTEXT
    context = {
        'students': page_obj,
        'page_obj': page_obj,
        'query': query,
        'sort': sort,
        'limit': limit,
        'dir':direction,
        'age_filter':age_filter,
    }

    return render(request, 'read_student.html', context)




'''def update_student(request, id):
    student = get_object_or_404(Student, id=id)

    if request.method == "POST":
        student.name = request.POST['name']
        student.email = request.POST['email']
        student.age = request.POST['age']
        student.date_of_joining = request.POST['date_of_joining']
        student.internship_period = request.POST['internship_period']
        student.save()

        return redirect('read_student')

    return render(request, 'update_student.html', {'student': student})'''

from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.contrib import messages

def delete_student(request, id):
    if not request.user.is_superuser:
        raise PermissionDenied

    student = get_object_or_404(Student, id=id)

    # ✅ SOFT DELETE
    student.is_deleted = True
    student.save()

    # ✅ ACTIVITY LOG
    AuditLog.objects.create(
        user=request.user,
        action='DELETE',
        description=f"Student '{student.name}' moved to Recycle Bin"
    )
    messages.success(request, "Student moved to Recycle Bin")
    return redirect('read_student')


def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Basic validations
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect('signup')

        # Create user
        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Account created successfully. Please login.")
        return redirect('login')

    return render(request, 'signup.html')

from django.contrib.auth.decorators import login_required
from .models import AuditLog


@login_required
def activity_logs(request):
    logs = AuditLog.objects.select_related('user').order_by('-created_at')

    return render(request, 'activity_logs.html', {'logs': logs})

@login_required
def export_students(request):
    if not (request.user.is_superuser or request.user.is_staff):
        raise PermissionDenied
    # export logic

from django.utils.timezone import now
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    from .models import Student

    total_students = Student.objects.count()

    active_internships = Student.objects.filter(
        completion_date__gte=now().date()
    ).count()

    completed_internships = Student.objects.filter(
        completion_date__lt=now().date()
    ).count()

    joined_this_month = Student.objects.filter(
        date_of_joining__month=now().month,
        date_of_joining__year=now().year
    ).count()

    context = {
        'total_students': total_students,
        'active_internships': active_internships,
        'completed_internships': completed_internships,
        'joined_this_month': joined_this_month,
    }

    return render(request, 'dashboard.html', context)


from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

@login_required
def recycle_bin(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    students = Student.objects.filter(is_deleted=True)

    return render(request, 'recycle_bin.html', {
        'students': students
    })

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

@login_required
def restore_student(request, id):
    if not request.user.is_superuser:
        raise PermissionDenied

    student = get_object_or_404(Student, id=id, is_deleted=True)
    student.is_deleted = False
    student.save()

    # Activity log
    AuditLog.objects.create(
        user=request.user,
        action='RESTORE',
        description=f"Restored student {student.name}"
    )

    return redirect('recycle_bin')

from .models import Student, AuditLog
from django.contrib.auth.decorators import login_required
import csv

@login_required
def import_students(request):
    if request.method == "POST":
        csv_file = request.FILES.get('file')

        if not csv_file or not csv_file.name.endswith('.csv'):
            return render(request, 'import_students.html', {
                'error': 'Please upload a valid CSV file'
            })

        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)

        created_count = 0

        for row in reader:
            Student.objects.create(
                name=row['name'],
                email=row['email'],
                age=row['age'],
                contact_no=row['contact_no'],
                date_of_joining=row['date_of_joining'],
                internship_period=row['internship_period'],
            )
            created_count += 1

        # ✅ LOG IMPORT ACTION (THIS WAS MISSING)
        AuditLog.objects.create(
            user=request.user,
            action="IMPORT",
            description=f"Imported {created_count} students via CSV"
        )

        return redirect('read_student')

    return render(request, 'import_students.html')


import openpyxl
from openpyxl import Workbook

from django.http import HttpResponse
from .models import Student
from django.contrib.auth.decorators import login_required


@login_required
def export_students_excel(request):
    students = get_filtered_students(request)

    wb = Workbook()
    ws = wb.active
    ws.title = "Students"

    headers = [
        "Name", "Email", "Contact", "Age",
        "Joining Date", "Internship Period", "Completion Date",
        "10th Marksheet", "12th Marksheet"
    ]
    ws.append(headers)

    for s in students:
        ws.append([
            s.name,
            s.email,
            s.contact_no,
            s.age,
            s.date_of_joining,
            s.internship_period,
            s.completion_date,
            s.documents.marksheet_10.url if hasattr(s, 'documents') and s.documents.marksheet_10 else "Not Uploaded",
            s.documents.marksheet_12.url if hasattr(s, 'documents') and s.documents.marksheet_12 else "Not Uploaded",
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=students.xlsx'
    wb.save(response)

    return response


from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


@login_required
def export_students_pdf(request):
    students = get_filtered_students(request)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=students.pdf'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 40

    p.setFont("Helvetica-Bold", 14)
    p.drawString(40, y, "Student Records (Filtered)")
    y -= 30

    p.setFont("Helvetica", 10)

    for s in students:
        lines = [
            f"Name: {s.name}",
            f"Email: {s.email}",
            f"Contact: {s.contact_no}",
            f"Age: {s.age}",
            f"Joining Date: {s.date_of_joining}",
            f"Internship Period: {s.internship_period} months",
            f"Completion Date: {s.completion_date}",
            "-" * 90,
        ]

        for line in lines:
            if y < 40:
                p.showPage()
                p.setFont("Helvetica", 10)
                y = height - 40

            p.drawString(40, y, line)
            y -= 15

    p.showPage()
    p.save()
    return response


from django.db.models import Q

def get_filtered_students(request):
    students = Student.objects.filter(is_deleted=False)

    # SEARCH
    query = request.GET.get('q', '')
    if query:
        students = students.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(contact_no__icontains=query)
        )

    # SORT
    sort = request.GET.get('sort', '')
    if sort == 'name':
        students = students.order_by('name')
    elif sort == 'age':
        students = students.order_by('age')
    elif sort == 'joining':
        students = students.order_by('date_of_joining')
    elif sort == 'completion':
        students = students.order_by('completion_date')
    else:
        students = students.order_by('id')

    # FILTER (TOP N)
    limit = request.GET.get('limit')
    if limit in ['5', '10', '20']:
        students = students[:int(limit)]

    return students
