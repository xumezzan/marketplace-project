#!/usr/bin/env python
"""
Script to create test specialists with portfolios for the marketplace.
Run this from the backend directory: python create_test_specialists.py
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'local_config.settings')
django.setup()

from django.contrib.auth import get_user_model
from marketplace.models import Category, SpecialistProfile, Review
from decimal import Decimal
import random

User = get_user_model()

# Specialist data
SPECIALISTS = [
    {
        'username': 'ivan_electrician',
        'email': 'ivan@example.com',
        'first_name': 'Иван',
        'last_name': 'Петров',
        'category': 'Ремонт',
        'description': 'Профессиональный электрик с 10-летним опытом. Выполняю все виды электромонтажных работ.',
        'hourly_rate': 1500,
        'rating': 4.9,
    },
    {
        'username': 'maria_tutor',
        'email': 'maria@example.com',
        'first_name': 'Мария',
        'last_name': 'Иванова',
        'category': 'Обучение',
        'description': 'Репетитор по математике и физике. Подготовка к ЕГЭ и ОГЭ. Индивидуальный подход.',
        'hourly_rate': 2000,
        'rating': 5.0,
    },
    {
        'username': 'alex_plumber',
        'email': 'alex@example.com',
        'first_name': 'Александр',
        'last_name': 'Сидоров',
        'category': 'Ремонт',
        'description': 'Сантехник. Установка и ремонт сантехники, водопровода, отопления.',
        'hourly_rate': 1800,
        'rating': 4.8,
    },
    {
        'username': 'olga_beautician',
        'email': 'olga@example.com',
        'first_name': 'Ольга',
        'last_name': 'Смирнова',
        'category': 'Красота',
        'description': 'Мастер маникюра и педикюра. Гель-лак, наращивание, дизайн ногтей.',
        'hourly_rate': 1200,
        'rating': 4.9,
    },
    {
        'username': 'dmitry_programmer',
        'email': 'dmitry@example.com',
        'first_name': 'Дмитрий',
        'last_name': 'Козлов',
        'category': 'IT услуги',
        'description': 'Full-stack разработчик. Python, Django, React. Создание веб-приложений.',
        'hourly_rate': 3000,
        'rating': 4.7,
    },
    {
        'username': 'anna_designer',
        'email': 'anna@example.com',
        'first_name': 'Анна',
        'last_name': 'Волкова',
        'category': 'IT услуги',
        'description': 'UI/UX дизайнер. Создание современных интерфейсов для веб и мобильных приложений.',
        'hourly_rate': 2500,
        'rating': 4.8,
    },
    {
        'username': 'sergey_driver',
        'email': 'sergey@example.com',
        'first_name': 'Сергей',
        'last_name': 'Морозов',
        'category': 'Перевозки',
        'description': 'Грузоперевозки по городу и области. Газель, грузчики. Быстро и аккуратно.',
        'hourly_rate': 1000,
        'rating': 4.6,
    },
    {
        'username': 'elena_cleaner',
        'email': 'elena@example.com',
        'first_name': 'Елена',
        'last_name': 'Новикова',
        'category': 'Уборка',
        'description': 'Клининговые услуги. Уборка квартир, офисов, после ремонта.',
        'hourly_rate': 800,
        'rating': 4.9,
    },
]

def create_test_specialists():
    """Create test specialists with profiles."""
    
    print("Creating test specialists...")
    
    for spec_data in SPECIALISTS:
        # Check if user already exists
        if User.objects.filter(username=spec_data['username']).exists():
            print(f"  ⚠️  User {spec_data['username']} already exists, skipping...")
            continue
        
        # Create user
        user = User.objects.create_user(
            username=spec_data['username'],
            email=spec_data['email'],
            password='testpass123',
            first_name=spec_data['first_name'],
            last_name=spec_data['last_name'],
            is_specialist=True,
        )
        
        # Get or create category
        category_name = spec_data['category']
        category, _ = Category.objects.get_or_create(
            name=category_name,
            defaults={'slug': category_name.lower().replace(' ', '-')}
        )
        
        # Create specialist profile
        profile = SpecialistProfile.objects.create(
            user=user,
            description=spec_data['description'],
            hourly_rate=Decimal(spec_data['hourly_rate']),
            is_verified=True,
        )
        profile.categories.add(category)
        
        # Update user rating
        user.rating = Decimal(spec_data['rating'])
        user.save()
        
        print(f"  ✅ Created specialist: {user.username} ({category_name}) - Rating: {spec_data['rating']}")
    
    print(f"\n✅ Successfully created {len(SPECIALISTS)} test specialists!")
    print(f"📊 Total specialists in database: {User.objects.filter(is_specialist=True).count()}")

if __name__ == '__main__':
    create_test_specialists()
