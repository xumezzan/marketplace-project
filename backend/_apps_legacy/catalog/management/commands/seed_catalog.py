from django.core.management.base import BaseCommand
from apps.catalog.models import Category, District

class Command(BaseCommand):
    help = 'Seed initial data for Categories and Districts'

    def handle(self, *args, **options):
        # Districts
        districts = [
            'Almazar', 'Bektemir', 'Mirabad', 'Mirzo Ulugbek', 'Sergeli',
            'Uchtepa', 'Chilanzar', 'Shaykhantahur', 'Yunusabad',
            'Yakkasaroy', 'Yangihayot', 'Yashnabad'
        ]
        for d in districts:
            District.objects.get_or_create(name=d)
        
        self.stdout.write(self.style.SUCCESS(f'Seeded {len(districts)} districts.'))

        # Categories
        # Commission based
        comm_cats = ['Tutor', 'Psychologist', 'Trainer', 'Auto Instructor', 'Lawyer', 'Accountant', 'Freelancer']
        for name in comm_cats:
            Category.objects.get_or_create(
                name=name, 
                defaults={'default_tariff': Category.TariffType.COMMISSION}
            )

        # Response based
        resp_cats = ['Repair', 'Plumber', 'Electrician', 'Hairdresser', 'Cleaner', 'Courier']
        for name in resp_cats:
            Category.objects.get_or_create(
                name=name,
                defaults={'default_tariff': Category.TariffType.RESPONSE}
            )

        self.stdout.write(self.style.SUCCESS(f'Seeded {len(comm_cats) + len(resp_cats)} categories.'))
