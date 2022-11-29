from django.core.mail import send_mail
from auctions.config import my_email


def send(user_email):
    send_mail(
        'Congratulations!',
        'Your bid was the winning one.',
        my_email,
        [user_email],
        fail_silently=False,
    )
