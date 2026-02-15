from django.contrib import admin
from .models import Position, Candidate, Vote, Election

class ElectionAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Prevent adding new Election objects if one already exists
        return not Election.objects.exists()

admin.site.register(Position)
admin.site.register(Candidate)
admin.site.register(Vote)
admin.site.register(Election, ElectionAdmin)