from uuid import uuid4
from django.db import models


class Client(models.Model):
    uuid = models.UUIDField(default=uuid4)
    computer_name = models.CharField(max_length=255)
    os = models.CharField(max_length=255)
    mac = models.CharField(max_length=17,)

    last_ip = models.GenericIPAddressField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return ("%s %s" % (self.computer_name, self.os)).strip()

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"


class Command(models.Model):
    uuid = models.UUIDField(default=uuid4)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)

    COMMAND_TYPE_CHOICES = (
        (0, 'command'),
        (1, 'internal'),
    )
    command_type = models.IntegerField(default=COMMAND_TYPE_CHOICES[0][0])
    command = models.TextField()

    received = models.BooleanField(default=False)

    def __str__(self):
        return "%s" % self.uuid


class CommandResult(models.Model):
    command = models.ForeignKey(Command, on_delete=models.CASCADE)
    result = models.TextField(null=True, blank=True)
    has_error = models.BooleanField(default=False)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

