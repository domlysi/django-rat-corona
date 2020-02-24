from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Command)
admin.site.register(Client)
admin.site.register(CommandResult)