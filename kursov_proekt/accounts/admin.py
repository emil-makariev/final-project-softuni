from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import CustomBaseUser, Profile


# Inline profile admin
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    extra = 0  # Remove extra empty rows

    fields = ('shipping_address_line1', 'shipping_address_line2', 'city', 'state', 'postal_code', 'country',
              'phone_number', 'profile_picture', 'size_preferences', 'newsletter_subscribed', 'receive_promotions')


# Admin for the CustomBaseUser
@admin.register(CustomBaseUser)
class CustomBaseUserAdmin(admin.ModelAdmin):
    model = CustomBaseUser

    # Fields to be shown in the list view
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')  # Removed 'date_joined'

    # Search and filters
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active')  # Make sure is_active is correctly handled here

    # Fieldsets for user creation and editing
    fieldsets = (
        (None, {
            'fields': ('username', 'email', 'first_name', 'last_name', 'password')
        }),
        (_('Permissions'), {
            'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')
        }),
        (_('Important dates'), {
            'fields': ('last_login',)  # If you need a date field, use last_login instead
        }),
    )

    # Adding the profile inline to the user edit page
    inlines = [ProfileInline]

    # Actions for batch updating of active status
    actions = ['make_active', 'make_inactive']

    def make_active(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, _("Selected users have been activated."))

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, _("Selected users have been deactivated."))

    make_active.short_description = _('Mark selected users as active')
    make_inactive.short_description = _('Mark selected users as inactive')


# Admin for Profile
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    model = Profile

    # List view display fields
    list_display = ('user', 'shipping_address_line1', 'city', 'state', 'country', 'phone_number', 'size_preferences',
                    'newsletter_subscribed', 'receive_promotions')

    # Search and filters
    search_fields = ('user__username', 'user__email', 'city', 'state', 'country')
    list_filter = ('newsletter_subscribed', 'receive_promotions', 'country')

    # Read-only fields for the profile admin (user is linked to the CustomBaseUser)
    readonly_fields = ('user',)

    # Customizing the profile form (for editing)
    fieldsets = (
        (None, {
            'fields': (
            'user', 'shipping_address_line1', 'shipping_address_line2', 'city', 'state', 'postal_code', 'country')
        }),
        (_('Contact Information'), {
            'fields': ('phone_number', 'profile_picture')
        }),
        (_('Preferences'), {
            'fields': ('size_preferences', 'newsletter_subscribed', 'receive_promotions')
        }),
    )

    # Actions for deleting profiles (if necessary)
    def delete_selected_profiles(self, request, queryset):
        profiles = queryset.all()
        for profile in profiles:
            profile.delete()
        self.message_user(request, _("Selected profiles have been deleted."))

    delete_selected_profiles.short_description = _('Delete selected profiles')

    actions = [delete_selected_profiles]
