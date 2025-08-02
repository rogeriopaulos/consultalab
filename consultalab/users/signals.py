from allauth.account.signals import password_changed
from django.dispatch import receiver


@receiver(password_changed)
def reset_force_password_change(sender, request, user, **kwargs):
    """
    Reseta o atributo force_password_change quando o usuário altera a senha.
    """
    if user.force_password_change:
        user.force_password_change = False
        user.save(update_fields=["force_password_change"])
