from django.db import models


class BlogManager(models.Manager):
    def get_featured(self):
        return self.all()[:3]
