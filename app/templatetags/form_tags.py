from django import template
from app.models import *
from app.forms import *
<<<<<<< HEAD
=======
from django.contrib.auth.forms import PasswordChangeForm
>>>>>>> deployment-backup

register = template.Library()

@register.simple_tag
def get_repository_form():
    form = KotdaRepositoryResourceForm()
    return form

@register.simple_tag
def get_repository_form_instance(resource_id):
    resource = KotdaRepositoryResource.objects.get(id=resource_id)
    if resource is not None:
        form = KotdaRepositoryResourceForm(instance=resource)
        return form
    else:
        return None


@register.simple_tag
def get_user_form(user):
    form = SignUpForm(instance=user)
    return form

@register.simple_tag
def get_profile_form(user):
    form = ProfileForm(instance=user)
    return form

@register.simple_tag
def get_course_review_form():
    form = LearningResourceReviewForm()
    return form

@register.simple_tag
def get_document_form():

    folder_form = RepositoryDocumentFolderForm()
    return folder_form


@register.simple_tag
def get_department_form():
    department_form = DepartmentFolderRelationshipForm()
<<<<<<< HEAD
    return department_form
=======
    return department_form


@register.simple_tag
def get_edit_document_form(document):

    folder_form = RepositoryDocumentFolderForm(instance=document)
    return folder_form


@register.simple_tag
def get_edit_department_form(folder):
    relationship = DepartmentFolderRelationship.objects.get(folder=folder)
    department_form = DepartmentFolderRelationshipForm(instance=relationship)
    return department_form


@register.simple_tag
def get_repo_document_form():
    form = RepositoryResourceDownloadForm()
    return form


@register.simple_tag
def get_password_change_form(user):
    form = PasswordChangeForm(user)
    return form
>>>>>>> deployment-backup
