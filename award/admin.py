from django.contrib import admin

from award.models import Lecturer, Nomination, Verification


@admin.register(Lecturer)
class LecturerAdmin(admin.ModelAdmin):
    pass


@admin.register(Nomination)
class NominationAdmin(admin.ModelAdmin):
    pass


@admin.register(Verification)
class VerificationAdmin(admin.ModelAdmin):
    pass
