"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import *
from django.conf import settings
from django.contrib.auth import get_user_model
from app.models import *
from django.contrib.postgres.forms import SimpleArrayField
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget
from django_summernote.fields import SummernoteTextFormField, SummernoteTextField


class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    email = forms.EmailField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'Email'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))



class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required! Enter a valid email address.')

    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2', )

    def clean_email(self):
        data = self.cleaned_data['email']
        domain = data.split('@')[1]
        domain_list = ["konza.go.ke", "kotda.go.ke"]
        if domain not in domain_list:
            raise forms.ValidationError("Please use your staff email to login")
        return data

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio', 'department', 'role', 'bio_ispublic')
        labels = {
                'bio':_('Biography'),
                'department':_('Department'),
                'role':_('Role'),
            }
        help_texts = {
            'bio': _('A short description of yourself.'),
        }
        error_messages = {
            'bio': {
                'max_length': _("This biography name is too long. Max 500 words"),
            },
        }



class LearningResourceForm(forms.ModelForm):
    class Meta:  
        model = LearningResource  
        fields = ('title', 'overview', 'description', 'featured_image', 'language', 'badge_image', 'type')
        labels = {
                'title':_('Title'),
                'description':_('Description'),
                'overview':_('Overview'),
                'language':_('Language'),
                'badge_image':_('Badge'),
                'type':_('Type'),
            }
        localized_fields = "__all__"
        widgets = {
            'description': forms.Textarea(attrs={'cols': 40, 'rows': 20}),
            'overview': forms.Textarea(attrs={'cols': 50, 'rows': 20}),
        }
        help_texts = {
            'badge_image': _('Upload graphic document that shall represent completion of course.'),
        }
        error_messages = {
            'title': {
                'max_length': _("This title is too long."),
            },
        }


#learning resource requirement forms
class LearningResourceRequirementForm(forms.Form):
    class Meta:  
        model = LearningResourceRequirement  
        fields = ('requirement',)
        labels = {
                'requirement':_('Requirement'),
                
            }
        localized_fields = "__all__"
        widgets = {
            #'description': forms.Textarea(attrs={'cols': 80, 'rows': 20}),
        }
        help_texts = {
            'requirement': _('What are the requirements for this course? e.g. internet connection, computer e.t.c'),
        }
        error_messages = {
            'requirement': {
                'max_length': _("This title is too long. use maximum of 100 characters"),
            },
        }


class LearningResourceModuleForm(forms.ModelForm):
    class Meta:
        model = LearningResourceModule
        fields = ('title','summary','video_url')
        labels = {
                'title':_('Title'),
                'summary':_('Summary'),
                'video_url':_('Youtube video url'),
            }
        localized_fields = "__all__"
        widgets = {
            'summary': forms.Textarea(attrs={'cols': 80, 'rows': 20}),
        }
        help_texts = {
            'video_url': _('Copy and paste your link from youtube'),
        }
        error_messages = {
            'title': {
                'max_length': _("This title is too long."),
            },
        }

class LearningModuleReferenceUrlForm(forms.ModelForm):
    class Meta:
        model = LearningResourceModuleReferenceUrl
        fields = ('name_of_website','reference_material_url', 'access_level')
        labels = {
                'name_of_website':_('Name of website'),
                'reference_material_url':_('Url/Link'),
                'access_level':_('Privacy level')
            }
        localized_fields = "__all__"
        help_texts = {
            'reference_material_url': _('Copy and paste a link from another website'),
        }


class LearningModuleDownloadForm(forms.ModelForm):
    class Meta:
        model = LearningResourceModuleDownload
        fields = ('name_of_document','reference_material_download', 'access_level')
        labels = {
                'name_of_document':_('Name of document'),
                'reference_material_download':_('Upload document'),
                'access_level':_('Privacy level')
            }
        localized_fields = "__all__"
        help_texts = {
            'reference_material_url': _('Copy and paste a link from another website'),
        }


class LearningResourceReviewForm(forms.ModelForm):
   
    class Meta:
        model = LearningResourceReview
        RATING_CHOICES=[('1','1'),
         ('2','2'),
         ('3','3'),
         ('4','4'),
         ('5','5')]
        fields = ('review','rating')
        labels = {
                'review':_('Review'),
                'rating':_('Rating')
            }
        widgets = {
            'review': forms.Textarea(attrs={'cols': 40, 'rows': 20, 'class':'form-control ht-140'}),
            'rating':forms.Select(choices=RATING_CHOICES)
        }
        localized_fields = "__all__"
        help_texts = {
            'review': _('Let the instructor know what you think of the course'),
        }


class KotdaRepositoryResourceForm(forms.ModelForm):
    class Meta:  
        model = KotdaRepositoryResource  
        fields = ('title', 'description', 'department_folder', 'upload_type', 'tags', 'access_level' )
        labels = {
                'title':_('Title'),
                'description':_('Short description'),
                #'type':_('Type'),
                'department_folder':_('Department Folder'),
                'upload_type':_('Type of Upload'),
                'access_level':_('Privacy'),
                'tags':_('Tags')
            }
        localized_fields = "__all__"
        widgets = {
            'description':forms.Textarea(attrs={'cols': 40, 'rows': 20, 'class':'form-control ht-140'}),
            'title': forms.TextInput(attrs={'class':"form-control"}),
            #'type': forms.Select(attrs={'class':"form-control populate", 'required':'required', 'data-plugin-selectTwo':''}),
            'department_folder': forms.Select(attrs={'class':"form-control populate", 'required':'required', 'data-plugin-selectTwo':''}),
            'upload_type': forms.Select(attrs={'class':"form-control populate", 'required':'required', 'data-plugin-selectTwo':''}),
            'access_level': forms.Select(attrs={'class':"form-control populate", 'required':'required', 'data-plugin-selectTwo':''}),
        }
        help_texts = {
            #'type': _('Upload graphic document that shall represent completion of course.'),
            'access_level': _('Private - Only visible to you. Protected - Only visible to staff members. Public - Visible to everyone'),
        }
        error_messages = {
            'description': {
                'max_length': _("This description is too long."),
            },
        }


#repo url
class RepositoryResourceReferenceUrlForm(forms.ModelForm):
    class Meta:  
        model = RepositoryResourceReferenceUrl  
        fields = ( 'name_of_website', 'reference_material_url')
        labels = {
                'name_of_website':_('Name of website'),
                'reference_material_url':_('reference material url'),
            }
        localized_fields = "__all__"
        widgets = {
           # 'description': forms.Textarea(attrs={'cols': 40, 'rows': 20}),
        }
        help_texts = {
            #'type': _('Upload graphic document that shall represent completion of course.'),
        }
        error_messages = {
            'name_of_website': {
                'max_length': _("This name is too long."),
            },
        }


#repo download
class RepositoryResourceDownloadForm(forms.ModelForm):
    class Meta:  
        model = RepositoryResourceDownload  
        fields = ( 'name_of_document', 'reference_material_download')
        labels = {
                'name_of_document':_('Name of document'),
                'reference_material_download':_('reference material download'),
            }
        localized_fields = "__all__"
        widgets = {
           # 'description': forms.Textarea(attrs={'cols': 40, 'rows': 20}),
        }
        help_texts = {
            #'type': _('Upload graphic document that shall represent completion of course.'),
        }
        error_messages = {
            'name_of_document': {
                'max_length': _("This name is too long."),
            },
        }



#repo image
class RepositoryResourceImageForm(forms.ModelForm):
    class Meta:  
        model = RepositoryResourceImage  
        fields = ( 'name_of_image', 'image')
        labels = {
                'name_of_image':_('image caption'),
                'image':_('image file'),
            }
        localized_fields = "__all__"
        widgets = {
           # 'description': forms.Textarea(attrs={'cols': 40, 'rows': 20}),
        }
        help_texts = {
            #'type': _('Upload graphic document that shall represent completion of course.'),
        }
        error_messages = {
            'name_of_image': {
                'max_length': _("This name is too long."),
            },
        }


#repo video
class RepositoryResourceVideoUrlForm(forms.ModelForm):
    class Meta:  
        model = RepositoryResourceVideoUrl  
        fields = ( 'name_of_video', 'video_file')
        labels = {
                'name_of_video':_('Name of video'),
                'video_file':_('video file'),
            }
        localized_fields = "__all__"
        widgets = {
           # 'description': forms.Textarea(attrs={'cols': 40, 'rows': 20}),
        }
        help_texts = {
            #'type': _('Upload graphic document that shall represent completion of course.'),
        }
        error_messages = {
            'name_of_video': {
                'max_length': _("This name is too long."),
            },
        }


#repo document type
class RepositoryDocumentFolderForm(forms.ModelForm):
    class Meta:  
        model = RepositoryDocumentFolder  
        fields = ( 'folder_name', 'description', 'access_level')
        labels = {
                'folder_name':_('Folder name'),
                'description':_('Description'),
                'access_level':_('Privacy Status'),
            }
        localized_fields = "__all__"
        widgets = {
            'folder_name': forms.TextInput(attrs={'class':'form-control','placeholder':'Folder name'}),
            'description': forms.Textarea(attrs={'cols': 10, 'rows': 10,'class':'form-control'}),
            'access_level':forms.Select(attrs={'class':"form-control col-md-7 "}),
        }
        help_texts = {
            'access_level': _('Private:- The folder is visible to only your department. Protected:- The folder is visible to all staff members. Public:- The folder is visible to everyone'),
        }
        error_messages = {
            'description': {
                'max_length': _("This name is too long."),
            },
        }

        #repo folder relationship
class DepartmentFolderRelationshipForm(forms.ModelForm):
    class Meta:  
        model = DepartmentFolderRelationship  
        fields = ( 'department', 'folder')
        labels = {
                'department':_('Name of department'),
                'folder':_('folder'),
            }
        localized_fields = "__all__"
        widgets = {
            'department': forms.Select(attrs={'class':"form-control col-md-7 "}),
            'folder': forms.Select(attrs={'class':"form-control col-md-7 "}),
        }
        help_texts = {
            #'type': _('Upload graphic document that shall represent completion of course.'),
        }
        error_messages = {
            'department': {
                'max_length': _("This name is too long."),
            },
        }