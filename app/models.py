"""
Definition of models.
"""

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.conf import settings
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from languages.fields import LanguageField
from embed_video.fields import EmbedVideoField
import pathlib


class CustomAccountManager(BaseUserManager):
    #create superuser function
    def create_superuser(self, email, first_name, last_name, password, **other_fields):
        other_fields.setdefault('is_staff',True)
        other_fields.setdefault('is_active',True)
        other_fields.setdefault('is_superuser',True)

        if other_fields.get('is_staff') is not True:
            raise ValueError('Superuser must be set to is_staff=True')
    
        return self.create_user(email, first_name, last_name, password, **other_fields)

    #default create user function
    def create_user(self, email, first_name, last_name, password, **other_fields):
        if not email:
            raise ValueError(_('You must provide an email address'))
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, password=password, **other_fields)
        user.set_password(password)
        user.save()
        return user

    

class User(AbstractBaseUser, PermissionsMixin):
    

    email = models.EmailField(_('email address'), unique=True)
    user_name = models.CharField(max_length=150)
    password = models.CharField(_('password'), max_length=128)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True,null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    
    objects = CustomAccountManager()

    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name','last_name']

    def __str__(self):
        return self.email

    def get_my_created_learning_resources(self):
        resources = LearningResource.objects.filter(created_by=self)
        return resources

    def get_my_documents(self):
        resources = KotdaRepositoryResource.objects.filter(created_by=self, is_deleted=False)
        documents = []

        for resource in resources:
            for document in resource.get_documents():
                documents.append(document)

        return documents

    def get_my_images(self):
        resources = KotdaRepositoryResource.objects.filter(created_by=self, is_deleted=False)
        images = []

        for resource in resources:
            for image in resource.get_images():
                images.append(image)

        return images

    def get_overview(self):
        resources = KotdaRepositoryResource.objects.filter(created_by=self, is_deleted=False)
        
        return resources

    #videos uploaded by user
    def get_my_videos(self):
        resources = KotdaRepositoryResource.objects.filter(created_by=self, is_deleted=False)
        videos = []

        for resource in resources:
            for video in resource.get_videos():
                videos.append(video)

        return videos


    
class Department(models.Model):
    name = models.CharField(_('name'),max_length=100,blank=False,null=False)
    description = models.TextField(_('description'),max_length=500,null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="created by", null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_host_resources(self):
        resources = RepositoryDepartment.objects.filter(department=self)
        return resources

    def get_folder_relationships(self):
        relationships = DepartmentFolderRelationship.objects.filter(department=self)
        return relationships



class Role(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    name = models.CharField(_('name'),max_length=100,blank=False,null=False)
    description = models.TextField(_('description'),max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="created by", null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(_('bio'),max_length=500, blank=True)
    bio_ispublic = models.BooleanField(default=False)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="department", null=True)
    role = models.CharField(blank=True, max_length=50, verbose_name="role", null=True)
    country = models.CharField(max_length=30, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    email_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.user.user_name


    @receiver(post_save, sender=User)
    def update_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)
        instance.profile.save()






class Poll(models.Model):
    """A poll object for use in the application views and repository."""
    text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def total_votes(self):
        """Calculates the total number of votes for this poll."""
        return self.choice_set.aggregate(Sum('votes'))['votes__sum']

    def __unicode__(self):
        """Returns a string representation of a poll."""
        return self.text

class Choice(models.Model):
    """A poll choice object for use in the application views and repository."""
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def votes_percentage(self):
        """Calculates the percentage of votes for this choice."""
        total=self.poll.total_votes()
        return self.votes / float(total) * 100 if total > 0 else 0

    def __unicode__(self):
        """Returns a string representation of a choice."""
        return self.text


###################################################################################
#### ========== Learning Resource Related Models===================##############################

class LearningResource(models.Model):

    def user_directory_path(instance, filename):
        # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
        return 'user_{0}/{1}'.format(instance.user.id, filename)

    title = models.CharField(_('title'), max_length=50)
    description = models.TextField(_('description'), max_length=500, blank=True)
    overview = models.TextField(_('overview'),null=True, max_length=5000, blank=True)
    featured_image = models.ImageField(upload_to='uploads/photos/%Y/%m/',null=True)# file will be saved to MEDIA_ROOT/uploads/2020/11/
    #banner_image = models.ImageField(upload_to='banner_image',null=True)
    badge_image = models.ImageField(upload_to='badge_image',null=True)
    tags = models.CharField(_('tags'), max_length=5000,null=True,blank=True)
    type = models.CharField(max_length=50, choices=settings.LEARNING_RESOURCE_TYPES)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="created by")
    access_level = models.CharField(max_length=50, choices=settings.LEARNING_RESOURCE_ACCESS_LEVEL, null=False, default="Private")
    experience_level = models.CharField(max_length=50, choices=settings.LEARNING_RESOURCE_EXPERIENCE_LEVEL, null=False, default="Beginner")
    duration = models.CharField(_('Duration'),max_length=100,null=True, blank=True)
    language = LanguageField(_('language'),null=True,blank=True)
    publish_status = models.CharField(max_length=50, choices=settings.LEARNING_RESOURCE_PUBLISHING_STATUS,null=False, default="Draft")
    is_featured = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)#todo: setup checks and controls to prevent from view while true
    slug = models.SlugField(max_length=200,null=False,unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_modules(self):
        modules = LearningResourceModule.objects.filter(resource=self)
        return modules
    
    def get_requirements(self):
        requirements = LearningResourceRequirement.objects.filter(resource=self)
        return requirements

    def get_published_resources(self):
        resources = LearningResource.objects.filter(publish_status="Published",is_deleted=False)
        return resources

    def get_reviews(self):
        reviews = LearningResourceReview.objects.filter(resource=self)
        return reviews

    def get_enrolments(self):
        enrolments = LearningResourceEnrolment.objects.filter(resource=self, status=True)
        return enrolments

    def get_views(self):
        views = LearningResourceView.objects.filter(resource=self)
        return views

    #course requirements
class LearningResourceRequirement(models.Model):
    resource = models.ForeignKey(LearningResource, on_delete=models.CASCADE)
    requirement = models.CharField(_('requirement'), max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.requirement
   
    #course topics
class LearningResourceModule(models.Model):
    resource = models.ForeignKey(LearningResource, on_delete=models.CASCADE)
    title = models.CharField(_('title'), max_length=50)
    summary = models.TextField(_('summary'), max_length=500, blank=True)
    video_url = EmbedVideoField( verbose_name="video url", null=True, blank=True)
    duration = models.CharField(_('Duration'),max_length=100,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="created by")
    access_level = models.CharField(max_length=50, choices=settings.LEARNING_RESOURCE_ACCESS_LEVEL, null=False, default="Private")
    publish_status = models.CharField(max_length=50, choices=settings.LEARNING_RESOURCE_PUBLISHING_STATUS,null=False, default="Draft")

    def __str__(self):
        return self.title

    def get_module_reference_urls(self):
        reference_urls = LearningResourceModuleReferenceUrl.objects.filter(module=self)
        return reference_urls

    def get_module_reference_downloads(self):
        reference_downloads = LearningResourceModuleDownload.objects.filter(module=self)
        return reference_downloads

class LearningResourceModuleReferenceUrl(models.Model):
    module = models.ForeignKey(LearningResourceModule, on_delete=models.CASCADE)
    name_of_website = models.CharField(_('name of website'), max_length=50)
    reference_material_url = models.URLField(max_length = 250, verbose_name="reference material url")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="created by")
    access_level = models.CharField(max_length=50, choices=settings.LEARNING_RESOURCE_ACCESS_LEVEL, null=False, default="Public")

    def __str__(self):
        return self.name_of_website

class LearningResourceModuleDownload(models.Model):
    module = models.ForeignKey(LearningResourceModule, on_delete=models.CASCADE)
    name_of_document = models.CharField(_('name of document'), max_length=50)
    reference_material_download = models.FileField(upload_to='LRMdownloads/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="created by")
    access_level = models.CharField(max_length=50, choices=settings.LEARNING_RESOURCE_ACCESS_LEVEL, null=False, default="Public")

    def __str__(self):
        return self.name_of_document

class LearningResourceEnrolment(models.Model):
    resource = models.ForeignKey(LearningResource, on_delete=models.CASCADE)
    learner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(_('status'),null=False,blank=False,default=True)

    def __str__(self):
        return self.learner

class LearningResourceView(models.Model):
    resource = models.ForeignKey(LearningResource, on_delete=models.CASCADE)
    viewer = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)#NOTE::might be risky leaving this as null
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.viewer

class LearningResourceModuleView(models.Model):
    module = models.ForeignKey(LearningResourceModule, on_delete=models.CASCADE)
    viewer = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.viewer

class LearningResourceModuleCompletion(models.Model):
    module = models.ForeignKey(LearningResourceModule, on_delete=models.CASCADE)
    learner = models.ForeignKey(LearningResourceEnrolment, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(_('status'),null=False,blank=False,default=True)

    def __str__(self):
        return self.learner

class LearningResourceReview(models.Model):
    resource = models.ForeignKey(LearningResource, on_delete=models.CASCADE)
    learner = models.ForeignKey(LearningResourceEnrolment, on_delete=models.CASCADE)
    rating = models.IntegerField(_('rating'),null=True,blank=True,default=1)
    review = models.TextField(_('review'), max_length=5000, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.review

##################################################################################



###################################################################################
#### ========== KOTDA Repository Related Models===================##############################

#repo documents | another name could be folder
class RepositoryDocumentFolder(models.Model):
    folder_name = models.CharField(_('folder name'), max_length=50, default="New Folder")
    description = models.TextField(_('description'), max_length=50000,null=True, blank=True)
    access_level = models.CharField(max_length=50, choices=settings.KOTDA_REPOSITORY_ACCESS_LEVEL, null=False, default="Protected")
    is_static = models.BooleanField(default=False)#means the folder details should not be modified i.e. undeletable
    
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="created by", null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.folder_name


    def get_folder_relationships(self):
        relationships = DepartmentFolderRelationship.objects.filter(folder=self)
        return relationships



#document type relationships
class DepartmentFolderRelationship(models.Model):
    folder = models.ForeignKey(RepositoryDocumentFolder, on_delete=models.CASCADE, verbose_name="folder", related_name="folder")
    #todo: parent and child
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, null=True,blank=True, on_delete=models.CASCADE,related_name="user")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("folder", "department")

    

class KotdaRepositoryResource(models.Model):
    title = models.CharField(_('title'), max_length=50)
    description = models.TextField(_('description'), max_length=50000,null=True, blank=True)
    tags = models.CharField(_('tags'), max_length=5000,null=True,blank=True)
    #type = models.CharField(max_length=50, choices=settings.KOTDA_REPOSITORY_TYPES,null=True,blank=True)
    department_folder = models.ForeignKey(RepositoryDocumentFolder, on_delete=models.CASCADE, verbose_name="doc type",blank=True, null=True)
    upload_type = models.CharField(max_length=50, choices=settings.UPLOAD_TYPES, null=False, blank=True, default="document")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="created by")
    access_level = models.CharField(max_length=50, choices=settings.KOTDA_REPOSITORY_ACCESS_LEVEL, null=True, blank=True, default="Private")
    publish_status = models.CharField(max_length=50, choices=settings.KOTDA_REPOSITORY_PUBLISHING_STATUS,null=False, default="Draft")
    is_featured = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def tags_as_list(self):
        if self.tags is not None:
            tags = [str(x.strip('[]')) for x in self.tags.split(',') if x]
            return tags
        else:
            return None

    def get_my_repositories():
        try:
            repo = KotdaRepositoryResource.objects.filter(created_by=request.user)
        except:
            return None

    def get_urls(self):
        urls = RepositoryResourceReferenceUrl.objects.filter(repository=self,is_deleted=False)
        return urls

    def get_images(self):
        images = RepositoryResourceImage.objects.filter(repository=self,is_deleted=False)
        return images

    def get_videos(self):
        videos = RepositoryResourceVideoUrl.objects.filter(repository=self,is_deleted=False)
        return videos

    def get_documents(self):
        documents = RepositoryResourceDownload.objects.filter(repository=self,is_deleted=False)
        return documents




#relationship between repository and departments
class RepositoryDepartment(models.Model):
    repository = models.ForeignKey(KotdaRepositoryResource, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.department

class RepositoryResourceReferenceUrl(models.Model):
    repository = models.ForeignKey(KotdaRepositoryResource, on_delete=models.CASCADE)
    name_of_website = models.CharField(_('name of website'), max_length=50)
    reference_material_url = models.URLField(max_length = 250, verbose_name="reference material url")
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    access_level = models.CharField(max_length=50, choices=settings.KOTDA_REPOSITORY_ACCESS_LEVEL, null=False, default="Public")

    def __str__(self):
        return self.name_of_website

class RepositoryResourceVideoUrl(models.Model):
    repository = models.ForeignKey(KotdaRepositoryResource, on_delete=models.CASCADE)
    name_of_video = models.CharField(_('title of video'), max_length=50)
    video_file = models.FileField(upload_to='repoVideo/', verbose_name="video url")
    thumbnail = models.ImageField(upload_to='repoImages/',null=True,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    access_level = models.CharField(max_length=50, choices=settings.KOTDA_REPOSITORY_ACCESS_LEVEL, null=False, default="Public")

    def __str__(self):
        return self.name_of_video

    def get_default_thumbnail(self):
        thumb_url = 'assets/img/video_thumb.png'
        return thumb_url

    def get_extension(self):
        file_extension = pathlib.Path(self.video_file.name).suffix

        return file_extension

    #you can call the DOCUMENTS model
class RepositoryResourceDownload(models.Model):
    repository = models.ForeignKey(KotdaRepositoryResource, on_delete=models.CASCADE)
    name_of_document = models.CharField(_('name of document'), max_length=50)
    reference_material_download = models.FileField(upload_to='repoDownloads/')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    access_level = models.CharField(max_length=50, choices=settings.KOTDA_REPOSITORY_ACCESS_LEVEL, null=False, default="Public")

    def __str__(self):
        return self.name_of_document

    def get_extension(self):
        file_extension = pathlib.Path(self.reference_material_download.name).suffix

        return file_extension

#document download stats
class RepositoryDocumentDownloadStat(models.Model):
    document = models.ForeignKey(RepositoryResourceDownload, on_delete=models.CASCADE)
    downloaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.document

class RepositoryResourceImage(models.Model):
    repository = models.ForeignKey(KotdaRepositoryResource, on_delete=models.CASCADE)
    name_of_image = models.CharField(_('name of document'), max_length=50)
    image = models.ImageField(upload_to='repoImages/')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    access_level = models.CharField(max_length=50, choices=settings.KOTDA_REPOSITORY_ACCESS_LEVEL, null=False, default="Public")

    def __str__(self):
        return self.name_of_image

    def get_extension(self):
        file_extension = pathlib.Path(self.image.name).suffix

        return file_extension

class RepositorySearch(models.Model):
    key = models.CharField(_('tag'), null=False, max_length=100)
    searched_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.key

class RepositoryResourceView(models.Model):
    repository = models.ForeignKey(KotdaRepositoryResource, on_delete=models.CASCADE)
    viewer = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.viewer

##################################################################################



###################################################################################
#### ========== KOTDA Policy Related Models===================##############################
class Policy(models.Model):
    title = models.CharField(_('title'), null=False, max_length=100)
    summary = models.TextField(_('summary'), max_length=500, blank=False)
    body = models.TextField(_('body'), max_length=5000, blank=False)
    document_for_download = models.FileField(upload_to='repoDownloads/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="created by")
    access_level = models.CharField(max_length=50, choices=settings.KOTDA_REPOSITORY_ACCESS_LEVEL, null=False, default="Private")
    publish_status = models.CharField(max_length=50, choices=settings.KOTDA_REPOSITORY_PUBLISHING_STATUS,null=False, default="Draft")


##################################################################################