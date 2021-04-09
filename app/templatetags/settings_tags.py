from django import template
from app.models import *
from app.forms import *
from django.conf import settings

register = template.Library()

@register.simple_tag
def get_repository_types():
    repository_types = settings.KOTDA_REPOSITORY_TYPES
    return repository_types