from django.core.management.base import BaseCommand

from employees.models import PublicHoliday

from datetime import datetime





class Command(BaseCommand):

    help = 'Populate Indian and Australian public holidays for 2024-2026'



    def handle(self, *args, **kwargs):

        # Clear existing holidays

        PublicHoliday.objects.all().delete()

        self.stdout.write('Cleared existing holidays')



        # Indian Holidays 2024

        indian_holidays_2024 = [

            {'name': 'Uttarayan', 'date': '2024-01-15', 'is_optional': False},

            {'name': 'Vasi Uttarayan', 'date': '2024-01-16', 'is_optional': False},

            {'name': 'Republic Day', 'date': '2024-01-26', 'is_optional': False},

            {'name': 'Dhuleti (Holi)', 'date': '2024-03-25', 'is_optional': False},

            {'name': 'Eid al-Fitr', 'date': '2024-04-10', 'is_optional': False},

            {'name': 'Eid al-Adha', 'date': '2024-06-17', 'is_optional': False},

            {'name': 'Raksha Bandhan', 'date': '2024-08-19', 'is_optional': False},

            {'name': 'Independence Day', 'date': '2024-08-15', 'is_optional': False},

            {'name': 'Janmashtami', 'date': '2024-08-26', 'is_optional': False},

            {'name': 'Ganesh Chaturthi / Samvatsari', 'date': '2024-09-07', 'is_optional': False},

            {'name': 'Dussehra', 'date': '2024-10-12', 'is_optional': False},

            {'name': 'Diwali', 'date': '2024-11-01', 'is_optional': False},

            {'name': 'Gujarati New Year', 'date': '2024-11-02', 'is_optional': False},

            {'name': 'Bhai Dooj', 'date': '2024-11-03', 'is_optional': False},

            {'name': 'Christmas', 'date': '2024-12-25', 'is_optional': False},

        ]



        # Indian Holidays 2025

        indian_holidays_2025 = [

            {'name': 'New Year', 'date': '2025-01-01', 'is_optional': False},

            {'name': 'Makar Sankranti', 'date': '2025-01-14', 'is_optional': True},

            {'name': 'Republic Day', 'date': '2025-01-26', 'is_optional': False},

            {'name': 'Maha Shivaratri', 'date': '2025-02-26', 'is_optional': True},

            {'name': 'Holi', 'date': '2025-03-14', 'is_optional': False},

            {'name': 'Good Friday', 'date': '2025-04-18', 'is_optional': True},

            {'name': 'Ram Navami', 'date': '2025-04-06', 'is_optional': True},

            {'name': 'Mahavir Jayanti', 'date': '2025-04-10', 'is_optional': True},

            {'name': 'Eid ul-Fitr', 'date': '2025-03-31', 'is_optional': False},

            {'name': 'Buddha Purnima', 'date': '2025-05-12', 'is_optional': True},

            {'name': 'Eid ul-Adha', 'date': '2025-06-07', 'is_optional': False},

            {'name': 'Muharram', 'date': '2025-07-06', 'is_optional': True},

            {'name': 'Independence Day', 'date': '2025-08-15', 'is_optional': False},

            {'name': 'Janmashtami', 'date': '2025-08-16', 'is_optional': True},

            {'name': 'Ganesh Chaturthi', 'date': '2025-08-27', 'is_optional': True},

            {'name': 'Milad un-Nabi', 'date': '2025-09-05', 'is_optional': True},

            {'name': 'Gandhi Jayanti', 'date': '2025-10-02', 'is_optional': False},

            {'name': 'Dussehra', 'date': '2025-10-02', 'is_optional': False},

            {'name': 'Diwali', 'date': '2025-10-20', 'is_optional': False},

            {'name': 'Guru Nanak Jayanti', 'date': '2025-11-05', 'is_optional': True},

            {'name': 'Christmas', 'date': '2025-12-25', 'is_optional': False},

        ]



        # Indian Holidays 2026

        indian_holidays_2026 = [

            {'name': 'New Year', 'date': '2026-01-01', 'is_optional': False},

            {'name': 'Makar Sankranti', 'date': '2026-01-14', 'is_optional': True},

            {'name': 'Republic Day', 'date': '2026-01-26', 'is_optional': False},

            {'name': 'Maha Shivaratri', 'date': '2026-03-17', 'is_optional': True},

            {'name': 'Holi', 'date': '2026-03-04', 'is_optional': False},

            {'name': 'Good Friday', 'date': '2026-04-03', 'is_optional': True},

            {'name': 'Ram Navami', 'date': '2026-03-26', 'is_optional': True},

            {'name': 'Mahavir Jayanti', 'date': '2026-03-30', 'is_optional': True},

            {'name': 'Eid ul-Fitr', 'date': '2026-03-20', 'is_optional': False},

            {'name': 'Buddha Purnima', 'date': '2026-05-01', 'is_optional': True},

            {'name': 'Eid ul-Adha', 'date': '2026-05-27', 'is_optional': False},

            {'name': 'Muharram', 'date': '2026-06-25', 'is_optional': True},

            {'name': 'Independence Day', 'date': '2026-08-15', 'is_optional': False},

            {'name': 'Janmashtami', 'date': '2026-09-04', 'is_optional': True},

            {'name': 'Ganesh Chaturthi', 'date': '2026-09-15', 'is_optional': True},

            {'name': 'Milad un-Nabi', 'date': '2026-08-25', 'is_optional': True},

            {'name': 'Gandhi Jayanti', 'date': '2026-10-02', 'is_optional': False},

            {'name': 'Dussehra', 'date': '2026-10-21', 'is_optional': False},

            {'name': 'Diwali', 'date': '2026-11-08', 'is_optional': False},

            {'name': 'Guru Nanak Jayanti', 'date': '2026-11-24', 'is_optional': True},

            {'name': 'Christmas', 'date': '2026-12-25', 'is_optional': False},

        ]



        # Australian Holidays 2025

        australian_holidays_2025 = [

            {'name': 'New Year\'s Day', 'date': '2025-01-01', 'is_optional': False},

            {'name': 'Australia Day', 'date': '2025-01-26', 'is_optional': False},

            {'name': 'Good Friday', 'date': '2025-04-18', 'is_optional': False},

            {'name': 'Easter Saturday', 'date': '2025-04-19', 'is_optional': False},

            {'name': 'Easter Monday', 'date': '2025-04-21', 'is_optional': False},

            {'name': 'Anzac Day', 'date': '2025-04-25', 'is_optional': False},

            {'name': 'Queen\'s Birthday', 'date': '2025-06-09', 'is_optional': False, 'description': 'Except WA & QLD'},

            {'name': 'Western Australia Day', 'date': '2025-06-02', 'is_optional': False, 'description': 'WA only'},

            {'name': 'Labour Day (QLD)', 'date': '2025-05-05', 'is_optional': False, 'description': 'Queensland'},

            {'name': 'Labour Day (NSW, ACT, SA)', 'date': '2025-10-06', 'is_optional': False, 'description': 'NSW, ACT, SA'},

            {'name': 'Melbourne Cup Day', 'date': '2025-11-04', 'is_optional': False, 'description': 'Victoria'},

            {'name': 'Christmas Day', 'date': '2025-12-25', 'is_optional': False},

            {'name': 'Boxing Day', 'date': '2025-12-26', 'is_optional': False},

        ]



        # Australian Holidays 2026

        australian_holidays_2026 = [

            {'name': 'New Year\'s Day', 'date': '2026-01-01', 'is_optional': False},

            {'name': 'Australia Day', 'date': '2026-01-26', 'is_optional': False},

            {'name': 'Good Friday', 'date': '2026-04-03', 'is_optional': False},

            {'name': 'Easter Saturday', 'date': '2026-04-04', 'is_optional': False},

            {'name': 'Easter Monday', 'date': '2026-04-06', 'is_optional': False},

            {'name': 'Anzac Day', 'date': '2026-04-25', 'is_optional': False},

            {'name': 'Queen\'s Birthday', 'date': '2026-06-08', 'is_optional': False, 'description': 'Except WA & QLD'},

            {'name': 'Western Australia Day', 'date': '2026-06-01', 'is_optional': False, 'description': 'WA only'},

            {'name': 'Labour Day (QLD)', 'date': '2026-05-04', 'is_optional': False, 'description': 'Queensland'},

            {'name': 'Labour Day (NSW, ACT, SA)', 'date': '2026-10-05', 'is_optional': False, 'description': 'NSW, ACT, SA'},

            {'name': 'Melbourne Cup Day', 'date': '2026-11-03', 'is_optional': False, 'description': 'Victoria'},

            {'name': 'Christmas Day', 'date': '2026-12-25', 'is_optional': False},

            {'name': 'Boxing Day', 'date': '2026-12-26', 'is_optional': False},

        ]



        # Create Indian holidays

        for holiday_data in indian_holidays_2024 + indian_holidays_2025 + indian_holidays_2026:

            date_obj = datetime.strptime(holiday_data['date'], '%Y-%m-%d').date()

            PublicHoliday.objects.create(

                name=holiday_data['name'],

                date=date_obj,

                day=date_obj.strftime('%A'),

                year=date_obj.year,

                country='IN',

                is_optional=holiday_data.get('is_optional', False),

                description=holiday_data.get('description', ''),

                is_active=True

            )



        self.stdout.write(self.style.SUCCESS(f'Created {len(indian_holidays_2025) + len(indian_holidays_2026)} Indian holidays'))



        # Create Australian holidays

        for holiday_data in australian_holidays_2025 + australian_holidays_2026:

            date_obj = datetime.strptime(holiday_data['date'], '%Y-%m-%d').date()

            PublicHoliday.objects.create(

                name=holiday_data['name'],

                date=date_obj,

                day=date_obj.strftime('%A'),

                year=date_obj.year,

                country='AU',

                is_optional=holiday_data.get('is_optional', False),

                description=holiday_data.get('description', ''),

                is_active=True

            )



        self.stdout.write(self.style.SUCCESS(f'Created {len(australian_holidays_2025) + len(australian_holidays_2026)} Australian holidays'))

        self.stdout.write(self.style.SUCCESS('Successfully populated all holidays!'))

