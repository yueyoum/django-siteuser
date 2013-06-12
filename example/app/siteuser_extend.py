from django.db import models

class SiteUserExtend(models.Model):
    score = models.IntegerField(default=0)
    nimei = models.CharField(max_length=12)

    class Meta:
        abstract = True