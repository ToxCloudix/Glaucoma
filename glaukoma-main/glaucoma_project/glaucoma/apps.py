from django.apps import AppConfig


class GlaucomaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'glaucoma'
    
    def ready(self):
        import glaucoma.signals
