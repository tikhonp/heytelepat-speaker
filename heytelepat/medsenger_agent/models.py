from django.db import models
import secrets
import random


class Contract(models.Model):
    contract_id = models.IntegerField(unique=True)
    speaker_active = models.BooleanField(default=False)

    def __str__(self):
        return "Contract id - {}".format(self.contract_id)


class Speaker(models.Model):
    code = models.IntegerField(unique=True)
    token = models.CharField(max_length=255, unique=True)
    contract = models.ForeignKey(Contract, null=True, default=None, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.pk:
            print("Creating new speaker")
            self.token = secrets.token_urlsafe(16)
            self.code = random.randint(100000, 999999)

        return super(Speaker, self).save(*args, **kwargs)


class Task(models.Model):
    speaker = models.ForeignKey(Speaker, on_delete=models.CASCADE)

    PREASURE_CHECK = 'PC'
    TASK_TYPE_CHOICES = [
        (PREASURE_CHECK, 'PC'),
    ]

    task_type = models.CharField(max_length=2, choices=TASK_TYPE_CHOICES)
    datetime = models.DateTimeField(null=True, default=None)
    is_done = models.BooleanField(default=False)
