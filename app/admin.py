"""
Customizations for the Django administration interface.
"""

from django.contrib import admin
from app.models import *
from django.contrib.auth.admin import UserAdmin
from django.forms import TextInput, Textarea


class UserAdminConfig(UserAdmin):
    search_fields = ('email', 'first_name', 'last_name',)
    list_filter = ('email', 'first_name', 'last_name', 'is_active', 'is_staff')
    ordering = ('-date_joined',)
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_staff')
    fieldsets = (
        (None,{'fields': ('email', 'first_name', 'last_name' )}),
        ('Permissions',{'fields': ('is_staff', 'is_active')}),
        )
    
    add_fieldsets = (
        (None,{
            'classes':('wide',),
            'fields':('email', 'first_name', 'last_name', 'password1', 'password2', 'is_active', 'is_staff'),
            }),
        )

admin.site.register(User,UserAdminConfig)

class ChoiceInline(admin.TabularInline):
    """Choice objects can be edited inline in the Poll editor."""
    model = Choice
    extra = 3

class PollAdmin(admin.ModelAdmin):
    """Definition of the Poll editor."""
    fieldsets = [
        (None, {'fields': ['text']}),
        ('Date information', {'fields': ['pub_date']}),
    ]
    inlines = [ChoiceInline]
    list_display = ('text', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['text']
    date_hierarchy = 'pub_date'

admin.site.register(Poll, PollAdmin)


class DepartmentAdmin(admin.ModelAdmin):
    fieldsets = (
        (None,{'fields': ('name', 'description', 'is_active', 'created_by' )}),
        )
    add_fieldsets = (
        (None,{
            'classes':('wide',),
            'fields':('name', 'description', 'is_active'),
            }),
        )
    list_display = ('name', 'description', 'is_active')

    search_fields = ['name', 'description']
admin.site.register(Department, DepartmentAdmin)

class ProfileAdmin(admin.ModelAdmin):
    fieldsets = (
        (None,{'fields': ('user', 'bio', 'bio_ispublic', 'department', 'role' )}),
        )
    add_fieldsets = (
        (None,{
            'classes':('wide',),
            'fields':('user', 'bio', 'department', 'role'),
            }),
        )
    list_display = ('user', 'bio', 'department', 'role')

    search_fields = ['user', 'bio', 'department','role']

admin.site.register(Profile, ProfileAdmin)

class RoleAdmin(admin.ModelAdmin):
    fieldsets = (
        (None,{'fields': ('name', 'description', 'is_active', 'created_by', 'department' )}),
        )
    search_fields = ['name', 'description']
admin.site.register(Role, RoleAdmin)

class LearningResourceAdmin(admin.ModelAdmin):
    fieldsets = (
        (None,{'fields': ('title', 'description', 'featured_image', 'badge_image', 'type', 'access_level', 'publish_status', 'is_featured' )}),
        )

    search_fields = ['title', 'description',]

admin.site.register(LearningResource, LearningResourceAdmin)


class RepositoryDocumentFolderAdmin(admin.ModelAdmin):
    fieldsets = (
        (None,{'fields': ('folder_name','description', 'access_level', 'is_static', 'is_deleted' )}),
        )
    add_fieldsets = (
        (None,{
            'classes':('wide',),
            'fields':('folder_name','description','access_level',),
            }),
        )
    list_display = ('folder_name','description','access_level',)

    search_fields = ['folder_name','description','access_level',]
admin.site.register(RepositoryDocumentFolder, RepositoryDocumentFolderAdmin)