from django.core.management.base import BaseCommand
from kyc.models import PopulationRecord

DATA = [
    ("2926396590", "Amar Ahmed Deina"),
    ("2926396590", "Ahmed Salem"),
    ("00123456787", "Fatimata Mint Mohamed"),
]

class Command(BaseCommand):
    help = "Seed simulated population registry for testing KYC."

    def handle(self, *args, **kwargs):
        for nni, full_name in DATA:
            PopulationRecord.objects.update_or_create(
                nni=nni,
                defaults={"full_name": full_name},
            )
        self.stdout.write(self.style.SUCCESS("✅ Population registry seeded successfully!"))
