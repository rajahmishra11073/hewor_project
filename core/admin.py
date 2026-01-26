from django.contrib import admin
from .models import ServiceOrder, Profile, SiteSetting, ContactMessage, OrderChat, Review, CaseStudy, AgencyStat, OrderFile
from django.utils.html import format_html
from django.urls import reverse

# --- Admin Interface Customization ---
admin.site.site_header = "Hewor Administration"
admin.site.site_title = "Hewor Admin Portal"
admin.site.index_title = "Welcome to Hewor Management Dashboard"

class OrderFileInline(admin.TabularInline):
    model = OrderFile
    extra = 0
    fields = ('file', 'file_type', 'uploaded_at')
    readonly_fields = ('uploaded_at',)

# --- Service Order Admin (FIXED) ---
@admin.register(ServiceOrder)
class ServiceOrderAdmin(admin.ModelAdmin):
    # ZARURI: 'status' aur 'is_paid' yahan hona chahiye taaki niche editable mein kaam karein
    list_display = ('title', 'user', 'service_type', 'status', 'is_paid', 'open_chat', 'is_delivered')
    
    # Filters
    list_filter = ('status', 'service_type', 'is_paid', 'created_at')
    
    # Search
    search_fields = ('title', 'user__username', 'description', 'transaction_id')
    
    # Direct Edit
    list_editable = ('status', 'is_paid')
    
    list_per_page = 20

    inlines = [OrderFileInline]

    fieldsets = (
        ('Order Details', {
            'fields': ('user', 'service_type', 'title', 'description', 'file_upload', 'request_call', 'phone_number', 'status')
        }),
        ('Payment Info', {
            'fields': ('is_paid', 'transaction_id', 'payment_screenshot')
        }),
        ('Project Delivery (Admin Use Only)', {
            'fields': ('delivery_file', 'delivery_message', 'completed_at'),
            'classes': ('collapse',),
            'description': "Upload the final file here to deliver the project to the client."
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('created_at',)

    def is_delivered(self, obj):
        return bool(obj.delivery_file)
    is_delivered.boolean = True
    is_delivered.short_description = "Delivered?"

    def open_chat(self, obj):
        url = reverse('order_detail', args=[obj.pk])
        return format_html('<a class="button" href="{}" target="_blank" style="background-color: #4361ee; color: white; padding: 5px 10px; border-radius: 5px; text-decoration: none;">Open Chat 💬</a>', url)
    open_chat.short_description = "Reply to User"

    def save_model(self, request, obj, form, change):
        # Auto-update status if delivered
        if obj.delivery_file and obj.status != 'completed':
            obj.status = 'completed'
            from django.utils import timezone
            if not obj.completed_at:
                obj.completed_at = timezone.now()
        super().save_model(request, obj, form, change)

# --- Order Chat Admin ---
@admin.register(OrderChat)
class OrderChatAdmin(admin.ModelAdmin):
    list_display = ('order', 'sender', 'message_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('message', 'order__title', 'sender__username')
    
    def message_preview(self, obj):
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message
    message_preview.short_description = "Message"

# --- Site Settings Admin ---
@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Sirf 1 setting object allow karein
        if SiteSetting.objects.exists():
            return False
        return True

# --- Contact Message Admin ---
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'sent_at')
    readonly_fields = ('name', 'email', 'subject', 'message', 'sent_at')
    search_fields = ('name', 'email', 'subject')

# --- Profile Admin ---
admin.site.register(Profile)

# --- Review Admin ---
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'rating', 'review_image_preview', 'delete_action', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('name', 'review_text', 'position')
    readonly_fields = ('created_at',)

    def review_image_preview(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />', obj.profile_image.url)
        return "No Image"
    review_image_preview.short_description = "Profile Image"

    def delete_action(self, obj):
        url = reverse('admin:core_review_delete', args=[obj.pk])
        return format_html('<a class="button" href="{}" style="background-color: #e74c3c; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none; font-weight: bold;">Delete</a>', url)
    delete_action.short_description = "Delete"

# --- Case Study Admin ---
@admin.register(CaseStudy)
class CaseStudyAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'category_color', 'order')
    list_editable = ('order', 'category_color')
    list_filter = ('category',)
    search_fields = ('title', 'challenge', 'solution')

# --- Agency Stat Admin ---
@admin.register(AgencyStat)
class AgencyStatAdmin(admin.ModelAdmin):
    list_display = ('label', 'value', 'icon_color', 'order')
    list_editable = ('value', 'order', 'icon_color')

# --- Team Member Admin ---
from .models import TeamMember, BlogPost
@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'order')
    list_editable = ('order',)
    search_fields = ('name', 'role', 'quote')


# --- Blog Post Admin (Content Marketing & SEO) ---
@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_published', 'is_ai_generated', 'views', 'created_at')
    list_filter = ('is_published', 'category', 'is_ai_generated', 'created_at')
    list_editable = ('is_published',)
    search_fields = ('title', 'excerpt', 'content', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('views', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Content', {'fields': ('title', 'slug', 'excerpt', 'content', 'featured_image')}),
        ('Categorization', {'fields': ('category', 'tags')}),
        ('Publishing', {'fields': ('author', 'is_published', 'is_ai_generated')}),
        ('Stats', {'fields': ('views', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )