# imports
from django.contrib import admin
from .models import Species, Grid, Results

# Register database models here to access from the admin panel
admin.site.register(Species)
admin.site.register(Grid)
admin.site.register(Results)
 