from django.contrib import admin


# Register your models here.
from api.models import Modality, Level, CurricularArea, PrelationOrder, Prelation, PrelationRequirement 

admin.site.register(Modality)
admin.site.register(Level)
admin.site.register(CurricularArea)
admin.site.register(PrelationOrder)
admin.site.register(Prelation)
admin.site.register(PrelationRequirement)
