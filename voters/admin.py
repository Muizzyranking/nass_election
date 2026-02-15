from django.contrib import admin
from .models import Student, Department

def clear_vote(modeladmin, request, queryset):
    queryset.update(has_voted=False)
    # Also delete the vote records
    for student in queryset:
        student.vote_set.all().delete()
clear_vote.short_description = "Clear selected students' votes"

class StudentAdmin(admin.ModelAdmin):
    list_display = ('matric', 'first_name', 'last_name', 'level', 'has_voted')
    actions = [clear_vote]

admin.site.register(Student, StudentAdmin)
admin.site.register(Department)