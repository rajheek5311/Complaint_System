"""
utils/email_utils.py
---------------------
This is a DUMMY email sender.

In a real product you would connect this to a real SMTP server
(Gmail, Outlook, SendGrid, etc.) using Python's built-in `smtplib`.
Sending real email requires an email account + app password, which is
outside the scope of "run this on your laptop and see it work",
so instead this function simply PRINTS the email to the terminal
and saves it into a file called email_log.txt

This means: every time a ticket is created / updated / assigned,
you will see a message printed in the terminal where you ran app.py.
This is enough to demonstrate the notification feature end-to-end.

If you later want REAL emails, you only need to change the inside of
this one function — nothing else in the project needs to change.
"""

from datetime import datetime

LOG_FILE = 'email_log.txt'


def send_email(to_address: str, subject: str, body: str) -> None:
    """
    'Sends' an email by printing it and logging it to a text file.
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    message = (
        f"\n----- EMAIL ({timestamp}) -----\n"
        f"To: {to_address}\n"
        f"Subject: {subject}\n"
        f"Body: {body}\n"
        f"--------------------------------\n"
    )

    # Print to terminal so you can SEE it happen live
    print(message)

    # Also save to a log file so nothing is lost
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(message)
