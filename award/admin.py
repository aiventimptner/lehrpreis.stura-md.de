from django.contrib import admin

from award.models import Lecturer, Module, Nomination


@admin.register(Lecturer)
class LecturerAdmin(admin.ModelAdmin):
    pass


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    pass


@admin.register(Nomination)
class NominationAdmin(admin.ModelAdmin):
    pass
