"""
Django settings for ResourceCentre project.

Based on by 'django-admin startproject' using Django 2.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import posixpath

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '45c0b6c7-1251-4458-9119-e3117a24547e'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['41.76.175.178', 'resourcecenter.konza.go.ke']

# App references
# https://docs.djangoproject.com/en/2.1/ref/settings/#std:setting-INSTALLED_APPS
INSTALLED_APPS = [
    'app',
    'languages',
    'embed_video',
    'django_summernote',
    'django_social_share',
    # Add your apps here to enable them

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# Middleware framework
# https://docs.djangoproject.com/en/2.1/topics/http/middleware/
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ResourceCentre.urls'

# Template configuration
# https://docs.djangoproject.com/en/2.1/topics/templates/
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ResourceCentre.wsgi.application'
# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
'''DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}'''

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
        'read_default_file': '/etc/mysql/my.cnf',
       },
    }
}

LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = 'repository_index'

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

#email config
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.live.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'resourcecenter@konza.go.ke'
EMAIL_HOST_PASSWORD = 'KonzaResource2021'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
#STATIC_URL = '/static/'
#STATIC_ROOT = os.path.join(BASE_DIR, 'static')
#STATICFILES_DIRS = [
#    os.path.join(BASE_DIR, 'static/app'),
#]

STATIC_URL = '/static/'
STATIC_ROOT = posixpath.join(*(BASE_DIR.split(os.path.sep) + ['static']))
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'app/static'),
    os.path.join(BASE_DIR, 'static/app'),
]


MEDIA_ROOT =  os.path.join(BASE_DIR, 'media') 
MEDIA_URL = '/media/'

AUTH_USER_MODEL = 'app.User'



#Learning resource types.
LEARNING_RESOURCE_TYPES = [
    ('Personal Development', 'Personal Development'),
    ('Professional Development', 'Professional Development'),
    ('Magazines', 'Magazines')
    ]

#Learning resource experience levels
#beginner
#intermediate
#expert
LEARNING_RESOURCE_EXPERIENCE_LEVEL = [
    ('Beginner', 'Beginner'),
    ('Intermediate', 'Intermediate'),
    ('Expert', 'Expert')
    ]

#Learning resource access level.
#public:- every user and non user can access
#protected:- only staff and enrolled users can access
#private:- only creator and admin can access
LEARNING_RESOURCE_ACCESS_LEVEL = [
    ('Public', 'Public'),
    ('Protected', 'Protected'),
    ('Private', 'Private')
    ]

#Learning resource publishing status
#draft:- saved to database but not submitted for review
#submitted:- saved to databse and submitted for review | editing is disabled at this point
#published:- saved to database and submitted for review | admin has approved for public view
#rejected:- saved to database and submitted for review | admin has rejected and is set to private view only
LEARNING_RESOURCE_PUBLISHING_STATUS = [
    ('Draft', 'Draft'),
    ('Submitted', 'Submitted'),
    ('Published', 'Published'),
    ('Rejected', 'Rejected')
    ]

#Learner enrolment status
#pending:- tutor has not approved
#Active:- tutor has approved or is open enrolment
#Blocked:- tutor has blocked enrolment
LEARNING_RESOURCE_ENROLMENT_STATUS = [
    ('Pending', 'Pending'),
    ('Active', 'Active'),
    ('Blocked', 'Blocked')
    ]


#Kotda repository
KOTDA_REPOSITORY_TYPES = [
    ('Investor journey', 'Investor journey'),
    ('Key events', 'Key events'),
    ('Project milestones', 'Project milestones'),
    ('Innovation ecosystem', 'Innovation ecosystem'),
    ('Miscellaneous', 'Miscellaneous'),
    ]


#Repository access level.
#Public information:- •	Information that is intended for public distribution and requires no specific security handling. For example, marketing, press releases, website material, posters. Etc. the material is classified as the most accessible material in the organization and no restrictions are applied to the data
#internal:- •	Information that would have minimal impact if disclosed, but where it is prudent to maintain a need-to-know approach. This category classifies information that is accessible to all staffs of staff but not external audiences. The material may include (Policies, Memos to all staff etc)
#restricted:- •	This category includes materials intended for specific groups of people within the organization. The material is only available to the people on a need-to-know basis given the work schedules and demands. Includes (Departmental reports, project documents, management reports etc)
#confidential:- •	This category of Information has a clear elevated sensitivity due to its legal, contractual, or business value and whose exposure may cost the organization financial, strategic and reputation risk.  For example, information containing sensitive personal data according to the GDPR definitions; information relating to ongoing commercial projects where disclosure could jeopardize the project; information that could identify a security vulnerability; large data sets containing personal data, trade secrets, contracts, detailed strategic documents, staff records, board papers, etc.
KOTDA_REPOSITORY_ACCESS_LEVEL = [
    ('Public', 'Public'),#C1
    ('Internal ', 'Internal'),#C2
    ('Restricted', 'Restricted'),#C3
    #('Confidential', 'Confidential')#C4
    ]



#Learning resource publishing status
#draft:- saved to database but not submitted for review
#submitted:- saved to databse and submitted for review | editing is disabled at this point
#published:- saved to database and submitted for review | admin has approved for public view
#rejected:- saved to database and submitted for review | admin has rejected and is set to private view only
KOTDA_REPOSITORY_PUBLISHING_STATUS = [
    ('Draft', 'Draft'),
    ('Submitted', 'Submitted'),
    ('Published', 'Published'),
    ('Rejected', 'Rejected')
    ]

#type of document being uploaded
UPLOAD_TYPES = [
    ('document', 'document'),
    ('video', 'video'),
    ('image', 'image'),
    #('url', 'url')
    ]

X_FRAME_OPTIONS = 'SAMEORIGIN'
