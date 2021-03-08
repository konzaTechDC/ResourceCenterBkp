from django import template
from app.models import *
from app.forms import *

register = template.Library()

@register.simple_tag
def get_all_departments():
    departments = Department.objects.filter(is_active=True)
    return departments

@register.simple_tag
def check_if_repo_department_exist(repository_id, department_id):
    repo = KotdaRepositoryResource.objects.get(id=repository_id)
    department = Department.objects.get(id=department_id)

    try:
        match = RepositoryDepartment.objects.get(repository=repo,department=department)
        return match
    except:
        return None

    #get document types
@register.simple_tag
def get_document_types():
    doc_types = RepositoryDocumentFolder.objects.filter(is_deleted=False)
    return doc_types

#curate my folders
@register.simple_tag
def curate_my_directory(request, department_id=''):
    #folder list for non authenticated users
    if not request.user.is_authenticated():
        folders = RepositoryDocumentFolder.objects.filter(is_deleted=False)


@register.simple_tag
def get_resource_tags(request):
    resources_with_tags = KotdaRepositoryResource.objects.filter(tags!=None, is_deleted=False)
    return resources_with_tags

@register.simple_tag
def get_my_repositories(user):
    repo = KotdaRepositoryResource.objects.filter(created_by=user, is_deleted = False)
    return repo


@register.simple_tag
def check_course_enrolment_status(request, resource):
    try:
        enrolment = LearningResourceEnrolment.objects.get(resource=resource,learner=request.user)
        return enrolment
    except:
        return None


@register.simple_tag
def get_rating_stat(resource, rating):
    ratings = LearningResourceReview.objects.filter(resource=resource,rating=rating,is_deleted=False)
    total_ratings = LearningResourceReview.objects.filter(resource=resource,is_deleted=False)

    if ratings.count() == 0 or total_ratings.count() == 0:
        return 'Unavailable'
    rating =((ratings.count()/total_ratings.count())*100)
    return rating


@register.simple_tag
def get_average_rating(resource):
    ratings = LearningResourceReview.objects.filter(resource=resource,is_deleted=False)

    rate_count = 0
    rate_total = 0

    for rate in ratings:
        rate_count += rate.rating
        rate_total += 5

    if rate_count == 0 or rate_total == 0:
        return 'No Rating Yet'
    else:
        return (rate_count/rate_total)