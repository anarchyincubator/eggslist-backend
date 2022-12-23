from django.db import models


class BlogManager(models.Manager):
    def get_featured(self):
        return self.all()[:3]

    def get_similar_for(self, blog):
        return self.select_related("author").filter(category=blog.category).exclude(id=blog.id)[:3]
