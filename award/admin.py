from django.contrib import admin

from award.models import Lecturer, Nomination, Verification


@admin.register(Lecturer)
class LecturerAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'faculty', 'count_nominations', 'count_nominations_verified')
    list_filter = ('faculty', 'is_favorite')
    ordering = ('first_name', 'last_name')
    search_fields = ['first_name', 'last_name']

    @admin.display(description='Nominations total')
    def count_nominations(self, obj):
        return obj.nomination_set.count()

    @admin.display(description='Nominations verified')
    def count_nominations_verified(self, obj):
        return obj.nomination_set.filter(is_verified=True).count()


@admin.register(Nomination)
class NominationAdmin(admin.ModelAdmin):
    list_display = ('sub_email', 'lecturer', 'sub_date', 'is_verified')
    list_filter = ('is_verified',)
    date_hierarchy = 'sub_date'
    ordering = ('sub_email',)
    search_fields = ['sub_email']


@admin.register(Verification)
class VerificationAdmin(admin.ModelAdmin):
    list_select_related = True
    list_display = ('nomination', 'created', 'is_expired')
    list_filter = (
        ('nomination__lecturer', admin.RelatedOnlyFieldListFilter),
    )
    list_display_links = None
    date_hierarchy = 'created'
    ordering = ('nomination__sub_email',)
    search_fields = ['nomination__sub_email']
