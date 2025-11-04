from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from library.models import Author, Book, Member, Loan

class Command(BaseCommand):
    help = "Seed demo data for testing API features"

    def handle(self, *args, **options):
        today = timezone.now().date()

        # Users & Members
        u1, _ = User.objects.get_or_create(username='john', defaults={'email':'john@example.com'})
        u2, _ = User.objects.get_or_create(username='jane', defaults={'email':'jane@example.com'})
        u3, _ = User.objects.get_or_create(username='alex', defaults={'email':'alex@example.com'})
        m1, _ = Member.objects.get_or_create(user=u1)
        m2, _ = Member.objects.get_or_create(user=u2)
        m3, _ = Member.objects.get_or_create(user=u3)

        # Authors
        a1, _ = Author.objects.get_or_create(first_name='George', last_name='Orwell', defaults={'biography':'Author of 1984'})
        a2, _ = Author.objects.get_or_create(first_name='Harper', last_name='Lee', defaults={'biography':'Author of TKAM'})

        # Books
        b1, _ = Book.objects.get_or_create(title='1984', author=a1, isbn='9780451524935', defaults={'genre':'fiction','available_copies':3})
        b2, _ = Book.objects.get_or_create(title='Animal Farm', author=a1, isbn='9780451526342', defaults={'genre':'fiction','available_copies':2})
        b3, _ = Book.objects.get_or_create(title='To Kill a Mockingbird', author=a2, isbn='9780061120084', defaults={'genre':'fiction','available_copies':4})
        b4, _ = Book.objects.get_or_create(title='Go Set a Watchman', author=a2, isbn='9780062409850', defaults={'genre':'fiction','available_copies':1})

        # Loans
        ln1, _ = Loan.objects.get_or_create(book=b1, member=m1, is_returned=False, defaults={})
        ln1.due_date = today + timedelta(days=7)       # not overdue
        ln1.save()

        ln2, _ = Loan.objects.get_or_create(book=b2, member=m1, is_returned=False, defaults={})
        ln2.due_date = today - timedelta(days=5)       # overdue
        ln2.save()

        ln3, _ = Loan.objects.get_or_create(book=b3, member=m2, is_returned=False, defaults={})
        ln3.due_date = today + timedelta(days=10)
        ln3.save()

        ln4, _ = Loan.objects.get_or_create(book=b4, member=m2, is_returned=False, defaults={})
        ln4.due_date = today + timedelta(days=1)
        ln4.save()

        ln5, _ = Loan.objects.get_or_create(book=b3, member=m3, is_returned=True, defaults={})
        ln5.return_date = today - timedelta(days=2)
        ln5.due_date = today - timedelta(days=3)
        ln5.save()

        # Simple stock adjust to reflect active loans
        for bk in (b1, b2, b3, b4):
            active = bk.loans.filter(is_returned=False).count()
            bk.available_copies = max(bk.available_copies - active, 0)
            bk.save(update_fields=['available_copies'])

        self.stdout.write(self.style.SUCCESS("Seed data created successfully."))
