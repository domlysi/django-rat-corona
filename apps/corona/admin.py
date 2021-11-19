from django.contrib import admin

from .models import *


@admin.register(Command)
class CommandAdmin(admin.ModelAdmin):
    list_display = [
        'computer_name',
        'command_str',
        'os',
        'get_command_type_display',
        'received',
        'created_on',
    ]

    def command_str(self, instance):
        return truncatechars(instance.command, 100)

    def os(self, instance):
        return instance.client.os

    def computer_name(self, instance):
        return instance.client.computer_name


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = [
        'computer_name',
        'os',
        'last_ip',
        'last_online',
        'mac',
        'created_on',
    ]
    readonly_fields = ('last_online', 'created_on')


@admin.register(CommandResult)
class CommandResultAdmin(admin.ModelAdmin):
    list_display = [
        'computer_name',
        'command_str',
        'is_success',
        'created_on',
    ]
    readonly_fields = ['result', 'computer_name', 'is_success', 'created_on']

    def computer_name(self, instance):
        return instance.command.client.computer_name

    def command_str(self, instance):
        return instance.command.command

    def is_success(self, instance):
        return not instance.has_error

    is_success.boolean = True
