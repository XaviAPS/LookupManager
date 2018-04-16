from django.db import models

# Create your models here.
# -*- coding: utf-8 -*-
from django.db import models
import datetime

class Document(models.Model):
    docfile = models.FileField()
   #name = models.CharField(max_length=15, default = 'def')
   #last_update = models.DateField(default=datetime.datetime.now())
   #state = models.CharField(max_length=30, default = 'OK')

