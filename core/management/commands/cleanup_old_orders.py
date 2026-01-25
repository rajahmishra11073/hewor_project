"""
Django management command to clean up files from old completed orders.

Usage:
    python manage.py cleanup_old_orders --days 30
    python manage.py cleanup_old_orders --days 7 --dry-run
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import ServiceOrder
from core.signals import delete_order_files


class Command(BaseCommand):
    help = 'Clean up files from old completed orders to reduce storage costs'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Delete files from orders completed more than X days ago (default: 30)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Find old completed orders
        old_orders = ServiceOrder.objects.filter(
            status='completed',
            completed_at__lt=cutoff_date
        ).select_related('user')
        
        total_count = old_orders.count()
        
        if total_count == 0:
            self.stdout.write(
                self.style.WARNING(
                    f'No orders found that were completed more than {days} days ago.'
                )
            )
            return
        
        self.stdout.write(f'Found {total_count} orders to process...\n')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No files will be deleted\n'))
        
        processed_count = 0
        total_files_deleted = 0
        
        for order in old_orders:
            completed_date = order.completed_at.strftime('%Y-%m-%d') if order.completed_at else 'Unknown'
            
            if dry_run:
                # Count files that would be deleted
                file_count = 0
                if order.file_upload: file_count += 1
                if order.delivery_file: file_count += 1
                if order.freelancer_roadmap: file_count += 1
                if order.payment_screenshot: file_count += 1
                if order.freelancer_payment_screenshot: file_count += 1
                file_count += order.files.count()
                file_count += order.freelancer_chats.filter(attachment__isnull=False).count()
                
                if file_count > 0:
                    self.stdout.write(
                        f'  [DRY RUN] Order #{order.id} ({order.user.username}): '
                        f'{order.title[:50]} - {file_count} files - Completed: {completed_date}'
                    )
                    total_files_deleted += file_count
            else:
                # Actually delete files
                files_deleted = delete_order_files(order)
                if files_deleted > 0:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✓ Order #{order.id} ({order.user.username}): '
                            f'{order.title[:50]} - {files_deleted} files deleted - Completed: {completed_date}'
                        )
                    )
                    total_files_deleted += files_deleted
            
            processed_count += 1
        
        # Summary
        self.stdout.write('\n' + '='*60)
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'\nDRY RUN SUMMARY:\n'
                    f'  Orders processed: {processed_count}\n'
                    f'  Files that would be deleted: {total_files_deleted}\n'
                    f'\nRun without --dry-run to actually delete files.'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nCLEANUP COMPLETED:\n'
                    f'  Orders processed: {processed_count}\n'
                    f'  Total files deleted: {total_files_deleted}\n'
                    f'  Storage space freed up significantly!'
                )
            )
