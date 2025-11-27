"""
Django management command to add sample specialists to the database.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from marketplace.models import Category, SpecialistProfile
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Add sample specialists for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample specialists...')
        
        # Get or create categories
        repair_cat, _ = Category.objects.get_or_create(
            name='Ремонт и строительство',
            defaults={'slug': 'repair', 'description': 'Ремонт и строительные работы'}
        )
        
        education_cat, _ = Category.objects.get_or_create(
            name='Обучение и репетиторы',
            defaults={'slug': 'education', 'description': 'Образовательные услуги'}
        )
        
        it_cat, _ = Category.objects.get_or_create(
            name='IT и фриланс',
            defaults={'slug': 'it', 'description': 'IT услуги и разработка'}
        )
        
        beauty_cat, _ = Category.objects.get_or_create(
            name='Красота и здоровье',
            defaults={'slug': 'beauty', 'description': 'Услуги красоты'}
        )
        
        auto_cat, _ = Category.objects.get_or_create(
            name='Авторемонт',
            defaults={'slug': 'auto', 'description': 'Ремонт автомобилей'}
        )
        
        cleaning_cat, _ = Category.objects.get_or_create(
            name='Уборка и клининг',
            defaults={'slug': 'cleaning', 'description': 'Клининговые услуги'}
        )
        
        # Sample specialists data
        specialists_data = [
            # Ремонт
            {
                'username': 'alisher_master',
                'first_name': 'Alisher',
                'last_name': 'Usmanov',
                'email': 'alisher@example.com',
                'rating': Decimal('4.9'),
                'categories': [repair_cat],
                'profile': {
                    'description': 'Master with 10 years of experience. Quick arrival in Chirchiq and Yunusabad. I work quickly and efficiently. I have all the necessary professional tools. I specialize in complex wiring in new buildings and shortlisting.',
                    'years_of_experience': 10,
                    'hourly_rate': Decimal('30000'),
                    'typical_price_range_min': Decimal('50000'),
                    'typical_price_range_max': Decimal('500000'),
                    'is_verified': True,
                }
            },
            {
                'username': 'jasur_remont',
                'first_name': 'Jasur',
                'last_name': 'Rahmonov',
                'email': 'jasur@example.com',
                'rating': Decimal('4.7'),
                'categories': [repair_cat],
                'profile': {
                    'description': 'Turnkey renovation. Quality guarantee. Work experience 8 years.',
                    'years_of_experience': 8,
                    'hourly_rate': Decimal('25000'),
                    'typical_price_range_min': Decimal('100000'),
                    'typical_price_range_max': Decimal('1000000'),
                    'is_verified': True,
                }
            },
            
            # Обучение
            {
                'username': 'elena_teacher',
                'first_name': 'Elena',
                'last_name': 'Kim',
                'email': 'elena@example.com',
                'rating': Decimal('5.0'),
                'categories': [education_cat],
                'profile': {
                    'description': 'Preparation for IELTS via Zoom. Band 8.0 holder. English language teacher with 5 years of experience.',
                    'years_of_experience': 5,
                    'hourly_rate': Decimal('50000'),
                    'typical_price_range_min': Decimal('40000'),
                    'typical_price_range_max': Decimal('80000'),
                    'is_verified': True,
                }
            },
            {
                'username': 'rustam_math',
                'first_name': 'Rustam',
                'last_name': 'Azizov',
                'email': 'rustam@example.com',
                'rating': Decimal('4.8'),
                'categories': [education_cat],
                'profile': {
                    'description': 'Математика и физика для школьников и абитуриентов. Подготовка к экзаменам.',
                    'years_of_experience': 7,
                    'hourly_rate': Decimal('30000'),
                    'typical_price_range_min': Decimal('25000'),
                    'typical_price_range_max': Decimal('50000'),
                    'is_verified': True,
                }
            },
            
            # IT
            {
                'username': 'sardor_dev',
                'first_name': 'Sardor',
                'last_name': 'Toshmatov',
                'email': 'sardor@example.com',
                'rating': Decimal('4.9'),
                'categories': [it_cat],
                'profile': {
                    'description': 'Full-stack разработчик. Создание сайтов и мобильных приложений. React, Django, Flutter.',
                    'years_of_experience': 6,
                    'hourly_rate': Decimal('100000'),
                    'typical_price_range_min': Decimal('500000'),
                    'typical_price_range_max': Decimal('5000000'),
                    'is_verified': True,
                }
            },
            {
                'username': 'aziz_designer',
                'first_name': 'Aziz',
                'last_name': 'Karimov',
                'email': 'aziz@example.com',
                'rating': Decimal('4.6'),
                'categories': [it_cat],
                'profile': {
                    'description': 'UI/UX дизайнер. Дизайн сайтов и мобильных приложений. Figma, Adobe XD.',
                    'years_of_experience': 4,
                    'hourly_rate': Decimal('70000'),
                    'typical_price_range_min': Decimal('200000'),
                    'typical_price_range_max': Decimal('1000000'),
                    'is_verified': False,
                }
            },
            
            # Красота
            {
                'username': 'malika_stylist',
                'first_name': 'Malika',
                'last_name': 'Rashidova',
                'email': 'malika@example.com',
                'rating': Decimal('5.0'),
                'categories': [beauty_cat],
                'profile': {
                    'description': 'Парикмахер-стилист. Окрашивание, стрижки, укладки. Работа на дому и выезд.',
                    'years_of_experience': 8,
                    'hourly_rate': Decimal('40000'),
                    'typical_price_range_min': Decimal('50000'),
                    'typical_price_range_max': Decimal('300000'),
                    'is_verified': True,
                }
            },
            {
                'username': 'dilnoza_nails',
                'first_name': 'Dilnoza',
                'last_name': 'Yusupova',
                'email': 'dilnoza@example.com',
                'rating': Decimal('4.9'),
                'categories': [beauty_cat],
                'profile': {
                    'description': 'Мастер маникюра и педикюра. Гель-лак, наращивание, дизайн.',
                    'years_of_experience': 5,
                    'hourly_rate': Decimal('30000'),
                    'typical_price_range_min': Decimal('40000'),
                    'typical_price_range_max': Decimal('150000'),
                    'is_verified': True,
                }
            },
            
            # Авторемонт
            {
                'username': 'bobur_mechanic',
                'first_name': 'Bobur',
                'last_name': 'Mahmudov',
                'email': 'bobur@example.com',
                'rating': Decimal('4.8'),
                'categories': [auto_cat],
                'profile': {
                    'description': 'Автомеханик. Ремонт двигателей, ходовой части, электрики. Диагностика.',
                    'years_of_experience': 12,
                    'hourly_rate': Decimal('50000'),
                    'typical_price_range_min': Decimal('100000'),
                    'typical_price_range_max': Decimal('1000000'),
                    'is_verified': True,
                }
            },
            {
                'username': 'kamol_electric',
                'first_name': 'Kamol',
                'last_name': 'Saidov',
                'email': 'kamol@example.com',
                'rating': Decimal('4.7'),
                'categories': [auto_cat],
                'profile': {
                    'description': 'Автоэлектрик. Ремонт электропроводки, установка сигнализаций и мультимедиа.',
                    'years_of_experience': 9,
                    'hourly_rate': Decimal('40000'),
                    'typical_price_range_min': Decimal('50000'),
                    'typical_price_range_max': Decimal('500000'),
                    'is_verified': False,
                }
            },
            
            # Уборка
            {
                'username': 'zarina_cleaning',
                'first_name': 'Zarina',
                'last_name': 'Ismoilova',
                'email': 'zarina@example.com',
                'rating': Decimal('4.9'),
                'categories': [cleaning_cat],
                'profile': {
                    'description': 'Профессиональная уборка квартир и офисов. Генеральная уборка, поддерживающая уборка.',
                    'years_of_experience': 6,
                    'hourly_rate': Decimal('20000'),
                    'typical_price_range_min': Decimal('100000'),
                    'typical_price_range_max': Decimal('500000'),
                    'is_verified': True,
                }
            },
            {
                'username': 'nargiza_house',
                'first_name': 'Nargiza',
                'last_name': 'Ahmedova',
                'email': 'nargiza@example.com',
                'rating': Decimal('4.6'),
                'categories': [cleaning_cat],
                'profile': {
                    'description': 'Клининг после ремонта. Мойка окон, химчистка мебели.',
                    'years_of_experience': 4,
                    'hourly_rate': Decimal('25000'),
                    'typical_price_range_min': Decimal('150000'),
                    'typical_price_range_max': Decimal('600000'),
                    'is_verified': True,
                }
            },
        ]
        
        created_count = 0
        for data in specialists_data:
            # Check if user exists by username or email
            if User.objects.filter(username=data['username']).exists():
                self.stdout.write(f"  User {data['username']} already exists, skipping...")
                continue
            
            if User.objects.filter(email=data['email']).exists():
                self.stdout.write(f"  Email {data['email']} already exists, skipping...")
                continue
            
            # Create user
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                password='password123',  # Default password
                rating=data['rating'],
                is_specialist=True,
                is_client=True,
            )
            
            # Create specialist profile
            profile_data = data['profile']
            profile = SpecialistProfile.objects.create(
                user=user,
                description=profile_data['description'],
                years_of_experience=profile_data['years_of_experience'],
                hourly_rate=profile_data['hourly_rate'],
                typical_price_range_min=profile_data['typical_price_range_min'],
                typical_price_range_max=profile_data['typical_price_range_max'],
                is_verified=profile_data['is_verified'],
            )
            
            # Add categories
            profile.categories.set(data['categories'])
            
            created_count += 1
            self.stdout.write(self.style.SUCCESS(f'  ✓ Created {user.get_full_name()} ({user.username})'))
        
        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully created {created_count} specialists!'))
        self.stdout.write(f'Total specialists in database: {User.objects.filter(is_specialist=True).count()}')
