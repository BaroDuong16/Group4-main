from django.apps import AppConfig

class CertificateConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'certificate'

    def ready(self):
        import certificate.signals 
