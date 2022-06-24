from eggslist.utils.user_code_generator import EmailCodeVerification


class PasswordResetCodeVerification(EmailCodeVerification):
    code_cache_key = "password_reset"
    link_endpoint = "password-reset"
    link_param_key = "reset_code"
    mail_subject = "Eggslist Password Reset"
    mail_template = "emails/password_reset.html"


class UserEmailVerification(EmailCodeVerification):
    code_cache_key = "email-verify"
    link_endpoint = "email-verify"
    link_param_key = "verification_code"
    mail_subject = "Eggslist Email Verification"
    mail_template = "emails/verify_email.html"
