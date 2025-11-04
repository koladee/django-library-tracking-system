from celery import shared_task
from .models import Loan
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db.models import Q

@shared_task
def send_loan_notification(loan_id):
    try:
        loan = Loan.objects.get(id=loan_id)
        member_email = loan.member.user.email
        book_title = loan.book.title
        send_mail(
            subject='Book Loaned Successfully',
            message=f'Hello {loan.member.user.username},\n\nYou have successfully loaned "{book_title}".\nPlease return it by the due date.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[member_email],
            fail_silently=False,
        )
    except Loan.DoesNotExist:
        pass

@shared_task
def check_overdue_loans():
    today = timezone.now().date()
    overdue_qs = Loan.objects.filter(
        is_returned=False,
        due_date__lt=today
    ).select_related('member__user', 'book')

    for loan in overdue_qs:
        member_email = loan.member.user.email
        book_title = loan.book.title
        send_mail(
            subject='Overdue Book Loan Reminder',
            message=f'Hello {loan.member.user.username},\n\nThis is a reminder that your loan for "{book_title}" is due.\nPlease return it asap.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[member_email],
            fail_silently=False,
        )