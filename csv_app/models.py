# Create your models here.
# -*- coding: utf-8 -*-

import datetime
import os

from django.db import models
from django.utils import timezone

class Document(models.Model):
    docfile = models.FileField()
    title = models.CharField(max_length=20)
    last_update = models.DateField(default=timezone.now)
    state = models.CharField(max_length=30, default = 'OK')
    slug = models.SlugField(allow_unicode=True,max_length=25, null=True)

