import datetime
from django.db import models
from django.utils import timezone

def get_upload_to(instance, filename):
    return 'logs/%d/%s' % (instance.profile, filename)


class Document(models.Model):
    docfile = models.FileField()
    title = models.CharField(max_length=20)
    last_update = models.DateField(default=timezone.now)
    state = models.CharField(max_length=30, default = 'OK')
    slug = models.SlugField(allow_unicode=True,max_length=25, null=False)

    def __str__(self):
        return "%s" % (self.title)


class Log(models.Model):
    user = models.CharField(max_length=25, default='unknown')
    datetime = models.CharField(max_length=50)
    document = models.FileField()
    filename = models.CharField(max_length=20)
    action = models.CharField(max_length=20, default='None')
    slug = models.CharField(max_length=20, default='None')


