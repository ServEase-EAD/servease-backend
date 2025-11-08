"""
Management command to seed time slots
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from appointments.services.time_slot_manager import create_time_slots_for_date


class Command(BaseCommand):
    help = 'Seed time slots for the next N days'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to create slots for (default: 30)'
        )
        parser.add_argument(
            '--start-hour',
            type=int,
            default=9,
            help='Business hours start (default: 9 AM)'
        )
        parser.add_argument(
            '--end-hour',
            type=int,
            default=17,
            help='Business hours end (default: 5 PM)'
        )

    def handle(self, *args, **options):
        days = options['days']
        start_hour = options['start_hour']
        end_hour = options['end_hour']
        
        today = timezone.now().date()
        total_created = 0
        
        self.stdout.write(f'Creating time slots for {days} days...')
        
        for i in range(days):
            current_date = today + timedelta(days=i)
            
            # Skip weekends
            if current_date.weekday() >= 5:
                continue
            
            slots = create_time_slots_for_date(
                current_date,
                business_hours_start=start_hour,
                business_hours_end=end_hour
            )
            
            total_created += len(slots)
            
            if slots:
                self.stdout.write(
                    self.style.SUCCESS(f'Created {len(slots)} slots for {current_date}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {total_created} time slots')
        )

