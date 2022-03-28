from django.core.mail import EmailMessage, get_connection


def send_mail_with_attachments(
    subject, message, from_email, recipient_list,
    attach_paths, fail_silently=False,
    auth_user=None, auth_password=None, connection=None
    ):
    connection = (
        connection or
        get_connection(
            username=auth_user,
            password=auth_password,
            fail_silently=fail_silently,
        )
    )
    email = EmailMessage(subject, message, from_email, recipient_list,
                         connection=connection)

    if isinstance(attach_paths, str):
        attach_paths = [attach_paths]
    for path in attach_paths:
        email.attach_file(path)
    email.send()
