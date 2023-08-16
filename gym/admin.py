from django.contrib import admin
from .models import Gym, GymReport, ReviewReport, Review

admin.site.register(Gym)
admin.site.register(Review)
admin.site.register(GymReport)
admin.site.register(ReviewReport)
