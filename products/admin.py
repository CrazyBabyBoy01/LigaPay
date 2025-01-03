from django.contrib import admin

# Register your models here.
from .models import (
    AccountService,
    BattlePassService,
    BoostService,
    Category,
    DonationService,
    OtherService,
    QualificationService,
    RPService,
    TrainingService,
)


admin.site.register(Category)
admin.site.register(RPService)
admin.site.register(AccountService)
admin.site.register(DonationService)
admin.site.register(BoostService)
admin.site.register(TrainingService)
admin.site.register(BattlePassService)
admin.site.register(OtherService)
admin.site.register(QualificationService)
