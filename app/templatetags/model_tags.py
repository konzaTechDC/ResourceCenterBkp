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
def curate_my_directory(request):
    folders = []
    #folder list for non authenticated users
    if not request.user.is_authenticated:
        relationships = DepartmentFolderRelationship.objects.filter(parent=None)
        
        for relationship in relationships:
            if relationship.folder.access_level == 'Public':
                folders.append(relationship.folder)
        return folders
    elif request.user.is_authenticated:
        #folder list for authenicated users
        relationships = DepartmentFolderRelationship.objects.filter(parent=None)

        for relationship in relationships:
            if relationship.folder.is_deleted == False:
                if relationship.folder.access_level == 'Restricted':
                    if relationship.department == request.user.profile.department:
                        folders.append(relationship.folder)
                if relationship.folder.access_level == 'Internal':
                    folders.append(relationship.folder)
                if relationship.folder.access_level == 'Public':
                    folders.append(relationship.folder)

        return folders




#curate my folders
@register.simple_tag
def curate_my_department_directory(request, department):
    folders = []
    #folder list for non authenticated users
    if not request.user.is_authenticated:
        relationships = DepartmentFolderRelationship.objects.filter(parent=None, department=department)
        
        for relationship in relationships:
            if relationship.folder.access_level == 'Public':
                folders.append(relationship.folder)
        return folders
    elif request.user.is_authenticated:
        #folder list for authenicated users
        relationships = DepartmentFolderRelationship.objects.filter(parent=None, department=department)

        for relationship in relationships:
            if relationship.folder.is_deleted == False:
                if relationship.folder.access_level == 'Restricted':
                    if relationship.department == request.user.profile.department:
                        folders.append(relationship.folder)
                if relationship.folder.access_level == 'Internal':
                    folders.append(relationship.folder)
                if relationship.folder.access_level == 'Public':
                    folders.append(relationship.folder)

        return folders


@register.simple_tag
def get_related_documents(request, document):
    documents = []

    #folder list for non authenticated users
    if not request.user.is_authenticated:
        #same repo
        others = RepositoryResourceDownload.objects.filter(id=document.id, is_deleted=False)

        for other in others:
            if other != document:
                documents.append(other)

        #TODO::same tags




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


@register.simple_tag
def get_featured_content():
    content = []

    resources = KotdaRepositoryResource.objects.filter(is_featured=True, is_deleted=False)
    documents = RepositoryResourceDownload.objects.filter(is_deleted=False)
    videos = RepositoryResourceVideoUrl.objects.filter(is_deleted=False)
    images = RepositoryResourceImage.objects.filter(is_deleted=False)

    docs = []
    pics = []
    vids = []

    for doc in documents:
        if doc.repository.is_featured:
            docs.append(doc)

    for pic in images:
        if pic.repository.is_featured and pic.repository.access_level == 'Public':
            pics.append(pic)

    for vid in videos:
        if vid.repository.is_featured:
            vids.append(vid)


    
    contents = ({
        'docs':docs,
        'pics':pics,
        'vids':vids,
        'resources':resources
        })
    
    return contents