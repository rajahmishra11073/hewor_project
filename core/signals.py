"""
Django signals for automatic file cleanup.
Deletes all files associated with a ServiceOrder when it's marked as completed.
"""
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.conf import settings
from .models import ServiceOrder, OrderFile, FreelancerChat
import os
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=ServiceOrder)
def cleanup_completed_order_files(sender, instance, created, **kwargs):
    """
    Delete all files when order is marked as completed.
    This runs after every save, but only acts when status changes to 'completed'.
    """
    # Don't cleanup on initial creation even if status is 'completed'
    if created:
        return
    
    # Only cleanup if file cleanup is enabled in settings
    if not getattr(settings, 'FILE_CLEANUP_ON_COMPLETION', True):
        return
    
    # Only process if order is completed
    if instance.status == 'completed':
        # Check if files still exist to avoid re-deleting on subsequent saves
        has_files = (
            instance.file_upload or 
            instance.delivery_file or 
            instance.freelancer_roadmap or
            instance.files.exists() or
            instance.freelancer_chats.filter(attachment__isnull=False).exists()
        )
        
        if has_files:
            logger.info(f"Cleaning up files for completed order #{instance.id}: {instance.title}")
            delete_order_files(instance)


@receiver(pre_delete, sender=ServiceOrder)
def cleanup_order_files_on_delete(sender, instance, **kwargs):
    """
    Delete all files when the order itself is deleted.
    This ensures orphaned files are cleaned up.
    """
    logger.info(f"Cleaning up files for deleted order #{instance.id}: {instance.title}")
    delete_order_files(instance)


def delete_order_files(order):
    """
    Helper function to delete all files associated with a ServiceOrder.
    
    Args:
        order: ServiceOrder instance
    """
    deleted_count = 0
    
    # Delete main upload file
    if order.file_upload:
        try:
            order.file_upload.delete(save=False)
            order.file_upload = None  # Clear the field reference
            deleted_count += 1
            logger.debug(f"Deleted file_upload for order #{order.id}")
        except Exception as e:
            logger.error(f"Error deleting file_upload for order #{order.id}: {e}")
    
    # Delete delivery file
    if order.delivery_file:
        try:
            order.delivery_file.delete(save=False)
            order.delivery_file = None  # Clear the field reference
            deleted_count += 1
            logger.debug(f"Deleted delivery_file for order #{order.id}")
        except Exception as e:
            logger.error(f"Error deleting delivery_file for order #{order.id}: {e}")
    
    # Delete freelancer roadmap
    if order.freelancer_roadmap:
        try:
            order.freelancer_roadmap.delete(save=False)
            order.freelancer_roadmap = None  # Clear the field reference
            deleted_count += 1
            logger.debug(f"Deleted freelancer_roadmap for order #{order.id}")
        except Exception as e:
            logger.error(f"Error deleting freelancer_roadmap for order #{order.id}: {e}")
    
    # Delete payment screenshots
    if order.payment_screenshot:
        try:
            order.payment_screenshot.delete(save=False)
            order.payment_screenshot = None  # Clear the field reference
            deleted_count += 1
            logger.debug(f"Deleted payment_screenshot for order #{order.id}")
        except Exception as e:
            logger.error(f"Error deleting payment_screenshot for order #{order.id}: {e}")
    
    if order.freelancer_payment_screenshot:
        try:
            order.freelancer_payment_screenshot.delete(save=False)
            order.freelancer_payment_screenshot = None  # Clear the field reference
            deleted_count += 1
            logger.debug(f"Deleted freelancer_payment_screenshot for order #{order.id}")
        except Exception as e:
            logger.error(f"Error deleting freelancer_payment_screenshot for order #{order.id}: {e}")
    
    # Delete OrderFile entries and their files
    for order_file in order.files.all():
        try:
            order_file.file.delete(save=False)
            order_file.delete()
            deleted_count += 1
            logger.debug(f"Deleted OrderFile #{order_file.id} for order #{order.id}")
        except Exception as e:
            logger.error(f"Error deleting OrderFile #{order_file.id}: {e}")
    
    # Delete chat attachments (but keep the chat messages)
    for chat in order.freelancer_chats.all():
        if chat.attachment:
            try:
                chat.attachment.delete(save=False)
                chat.attachment = None  # Clear the field reference
                chat.save(update_fields=['attachment'])  # Save to persist the change
                deleted_count += 1
                logger.debug(f"Deleted attachment for FreelancerChat #{chat.id}")
            except Exception as e:
                logger.error(f"Error deleting chat attachment #{chat.id}: {e}")
    
    # Save order to persist field changes (file references cleared)
    if deleted_count > 0:
        try:
            order.save(update_fields=[
                'file_upload', 
                'delivery_file', 
                'freelancer_roadmap',
                'payment_screenshot',
                'freelancer_payment_screenshot'
            ])
        except Exception as e:
            logger.error(f"Error saving order #{order.id} after file deletion: {e}")
    
    logger.info(f"Successfully deleted {deleted_count} files for order #{order.id}")
    return deleted_count
