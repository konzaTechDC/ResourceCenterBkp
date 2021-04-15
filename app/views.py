"""
Definition of views.
"""

import json
from os import path
from datetime import datetime
from django.contrib.auth import login
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.template import RequestContext
from django.utils import timezone
from django.views.generic import ListView, DetailView
from app.models import *
from django.forms.models import model_to_dict
from django.utils.text import slugify

from app.forms import *
from app.tokens import account_activation_token
from ResourceCentre.settings import EMAIL_HOST_USER

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Q
from itertools import chain
from django.contrib.auth.decorators import *
from django.views import View
import mimetypes
import pathlib
#from upload_validator import FileTypeValidator
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash


#index page
def home(request):
    return render(request,'staff/repository/index.html',)

#pata ip
def visitor_ip_address(request):

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


######################################################################################################
################=========Authentication Views=============############################################

#change the password
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('get_user_dashboard', user_id=request.user.id, tab='edit')
        else:
            messages.error(request, 'Please correct the error below.'+str(form.errors))
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



#registration=================############
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if form.is_valid() and profile_form.is_valid():
            user = form.save(commit=False)
            user.set_password(request.POST.get("password1"))
            user.is_active = False
            user.save()
            profile = Profile.objects.get(user=user)
            profile.department = Department.objects.get(id=request.POST.get("department"))
            profile.role = request.POST.get("role")
            
            profile.save()

            current_site = get_current_site(request)
            subject = 'Activate Your Account'
            message = render_to_string('auth/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.id)),
                'token': account_activation_token.make_token(user),
            })

            send_mail(
                'KOTDA Resource Centre email confirmation',
                message,
                EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )

            return redirect('account_activation_sent')
    else:
        form = SignUpForm()
        profile_form = ProfileForm()
    return render(
        request,
        'auth/signup.html',
        {
            'title':'Signup',
            'message':'Enter your details.',
            'year':datetime.now().year,
            'form':form,
            'profile_form':profile_form
        })
    


def account_activation_sent(request):
    return render(request, 'auth/account_activation_sent.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(id=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        login(request, user)
        return redirect('dashboard')
    else:
        return render(request, 'auth/account_activation_invalid.html')




#update user profile
def update_user_profile(request):
    if request.method == 'POST':
        if request.POST.get('user_id'):
          #  try:

                user = User.objects.get(id=request.POST.get('user_id'))
                if not user:
                    messages.add_message(request, messages.ERROR, 'An error occured. User does not exist. Contact Konza ICT Office for support')
                user_form = SignUpForm(instance=user)
                user.first_name = request.POST.get('first_name')
                user.last_name = request.POST.get('last_name')
                user.save()

                user.profile.bio = request.POST.get('bio')
                if request.POST.get('bio_ispublic') == 'on':
                    user.profile.bio_ispublic = True
                else:
                    user.profile.bio_ispublic = False
                if request.POST.get('department'):
                    user.profile.department = Department.objects.get(id=request.POST.get('department'))
                user.profile.role = request.POST.get('role')
                user.profile.save()

                messages.add_message(request, messages.SUCCESS, 'Profile updated successfully')
                return redirect('get_user_dashboard', user_id=user.id, tab=request.POST.get('tab'))
           # except:
             #   messages.add_message(request, messages.ERROR, 'An error occured. Form could not be saved. Contact Konza ICT Office for support')
              #  return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            messages.add_message(request, messages.ERROR, 'An error occured. Department could not be saved. Contact Konza ICT Office for support')

    else:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        messages.add_message(request, messages.ERROR, 'An error occured. Department could not be saved. Contact Konza ICT Office for support')



######################################################################################################


######################################################################################################
################=========Learning Portal Views=============############################################
@login_required
def create_learning_resource(request):
    if request.method == 'POST':
        form = LearningResourceForm(request.POST, request.FILES)
        requirements = request.POST.getlist('requirements[]')
        if form.is_valid():
            lresource = form.save(commit=False)
            lresource.created_by=request.user
            lresource.access_level = 'Private'
            lresource.publish_status = 'Draft'
            lresource.slug=slugify(lresource.title)
            lresource.save()

            if requirements is not None:
                for requirement in requirements:
                    req = LearningResourceRequirement()
                    req.resource = lresource
                    req.requirement = requirement
                    req.save()

            return redirect('create_learning_module',id=lresource.id)#todo: redirect to resource module
        else:
            return render(request,
                    'staff/learning/create.html',
                    {
                        'title':'Create New Learning Resource',
                        'message':'Something went wrong. Try again',
                        'year':datetime.now().year,
                        'form':form,
                    })
    else:
        form = LearningResourceForm()
        requirement_form = LearningResourceRequirementForm()
        return render(request,
                    'staff/learning/create.html',
                    {
                        'title':'Create New Learning Resource',
                        'message':'Complete the form below.',
                        'year':datetime.now().year,
                        'form':form,
                        'requirement_form':requirement_form
                    })
        
##########create learning module###########################
@login_required
def create_learning_module(request, id):
    if request.method == "POST":
        form=LearningResourceModuleForm(request.POST,request.FILES)
        reference_form = LearningModuleReferenceUrlForm(request.POST, request.FILES)
        download_form = LearningModuleDownloadForm(request.POST,request.FILES)

        resource=LearningResource.objects.get(id=id)
        if form.is_valid() and reference_form.is_valid() and download_form.is_valid() and resource is not None:
            #save module object
            l_resource_module=form.save(commit=False)
            l_resource_module.created_by=request.user
            l_resource_module.resource=resource
            l_resource_module.save()

            #save refeences#
            module_reference=reference_form.save(commit=False)
            module_reference.module=l_resource_module
            module_reference.created_by=request.user
            module_reference.save()

            #save downloads
            module_download=download_form.save(commit=False)
            module_download.module=l_resource_module
            module_download.created_by=request.user
            module_download.save()

            return redirect('dashboard')
        else:
            return render(request,
                    'staff/learning/module/create.html',
                    {
                        'title':'Create New Learning Resource',
                        'message':'Something went wrong. Try again',
                        'year':datetime.now().year,
                        'form':form,
                        'reference_form':reference_form,
                        'download_form':download_form
                    })
    else:
        form = LearningResourceModuleForm()
        reference_form = LearningModuleReferenceUrlForm()
        download_form = LearningModuleDownloadForm()

        return render(request,
                    'staff/learning/module/create.html',
                    {
                        'title':'Create New Learning Resource',
                        'message':'Complete the form below.',
                        'year':datetime.now().year,
                        'form':form,
                        'reference_form':reference_form,
                        'download_form':download_form
                    })


####===update learning module #################
@login_required
def update_learning_module(request, id):
    learning_module = LearningResourceModule.objects.get(id=id)
    references = LearningResourceModuleReferenceUrl.objects.filter(module=learning_module)
    downloads = LearningResourceModuleDownload.objects.filter(module=learning_module)

    if request.method == "POST" and learning_module is not None:
        form = LearningResourceModuleForm(request.POST, instance=learning_module)
        
        if form.is_valid():
            try:
                form.save()

                if references is not Null:
                    for reference in references:
                        reference_form = LearningModuleReferenceUrlForm(request.POST, request.FILES, instance=reference)
                        if reference_form.is_valid():
                            reference_form.save()

                if downloads is not Null:
                    for download in downloads:
                        download_form = LearningModuleDownloadForm(request.POST,request.FILES, instance=download)
                        if download_form.is_valid():
                            download_form.save()

    #TODO: return dwnload and references form objects
                return render(
                                request,
                                'staff/learning/module/update.html',
                                {
                                    'title':'Update ' +learning_resource.title,
                                    'message':'Enter your details.',
                                    'year':datetime.now().year,
                                    'form':form,
                                })
            except:
                pass
    else:
        form = LearningResourceForm(instance=learning_resource)
        return render(
                request,
                'staff/learning/update.html',
                {
                    'title':'Update ' +learning_resource.title,
                    'message':'Enter your details.',
                    'year':datetime.now().year,
                    'form':form,
                })

########################################################

########list learning module ###################
def list_learning_module(request, id):
    resource = LearningResource.objects.get(id=id)

########################################################

##############view learning module########################
def view_learning_module(request, id):
    learning_module = LearningResourceModule.objects.get(id=id)
    if learning_module is not None:
        ##Todo: update views views
        return render(
                request,
                'staff/learning/module/view.html',
                {
                    'title':learning_module.title,
                    'year':datetime.now().year,
                    'learning_module':learning_module,
                })
    else:
        return render(
                request,
                'staff/dashboard.html',
                {
                    'title':'ResourceNotFoundError',
                    'message':'Something wrong happened. Learning resource does not exits!',
                    'year':datetime.now().year,
                })

#################===remove learning module======#####################################
@login_required
def remove_learning_module(request, id):
    learning_module = LearningResourceModule.objects.get(id=id)

################====update/edit learning resource==========#############
@login_required
def post_update_learning_resource(request):


    if request.method == "POST":
        resource = LearningResource.objects.get(id=request.POST.get("resource_id")) or None
        if resource is not None:
            form = LearningResourceForm(request.POST, instance=resource)
            if form.is_valid():
                form.save()
                return render(
                    request,
                    'staff/learning/update.html',
                    {
                        'title':'Update ' +resource.title,
                        'message':'Enter your details.',
                        'year':datetime.now().year,
                        'form':form,
                        'resource':resource
                    })
    else:
        return redirect('dashboard')

    #redirects to course edit page
@login_required
def get_update_learning_resource(request,resource_id):
    resource = LearningResource.objects.get(id=resource_id)
    if resource is not None:
        form = LearningResourceForm(instance=resource)
        return render(
                request,
                'staff/learning/update.html',
                {
                    'title':'Update ' +resource.title,
                    'message':'Enter your details.',
                    'year':datetime.now().year,
                    'form':form,
                    'resource':resource
                })
    else:
        return redirect('dashboard')


    #list all published courses
def list_all_courses(request):
    learning_resources = LearningResource.objects.filter(publish_status="Published",is_deleted=False)
    #pagination
    paginator = Paginator(learning_resources, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if learning_resources is not None:
        return render(
                request,
                'staff/learning/list.html',
                {
                    'title':'Course List',
                    'year':datetime.now().year,
                    'learning_resources':learning_resources,
                    'page_obj':page_obj
                })
    else:
        return redirect('dashboard')


    #lists a content creator's uploads
def list_creator_courses(request,creator_id):
    creator = User.objects.get(id=creator_id)
    learning_resources = LearningResource.objects.filter(created_by=creator,is_deleted=False)
    #pagination
    paginator = Paginator(learning_resources, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if learning_resources is not None:
        return render(
                request,
                'staff/learning/list.html',
                {
                    'title':'Learning Resources by ' +creator.first_name,
                    'year':datetime.now().year,
                    'learning_resources':learning_resources,
                    'page_obj': page_obj
                })
    else:
        return render(
                request,
                'staff/learning/list.html',
                {
                    'title':'Error: Resource not found!',
                    'year':datetime.now().year,
                    'learning_resources':learning_resources,
                })

    #lists a content creator's published uploads
def list_creator_published_courses(request, creator_id):
    creator = User.objects.get(id=creator_id)
    learning_resources = LearningResource.objects.filter(created_by=creator,is_deleted=False,publish_status="Published")

    if learning_resources is not None:
        return render(
                request,
                'staff/learning/list.html',
                {
                    'title':'Learning Resources by ' +creator.first_name,
                    'year':datetime.now().year,
                    'learning_resources':learning_resources,
                })
    else:
        return render(
                request,
                'staff/learning/list.html',
                {
                    'title':'Error: Resource not found!',
                    'year':datetime.now().year,
                    'learning_resources':learning_resources,
                })


#lists a content creator's pending uploads
@login_required
def list_creator_pending_courses(request, creator_id):
    creator = User.objects.get(id=creator_id)
    learning_resources = LearningResource.objects.filter(created_by=creator,is_deleted=False,publish_status="Submitted")

    if learning_resources is not None:
        return render(
                request,
                'staff/learning/list.html',
                {
                    'title':'Learning Resources by ' +creator.first_name,
                    'year':datetime.now().year,
                    'learning_resources':learning_resources,
                })
    else:
        return render(
                request,
                'staff/learning/list.html',
                {
                    'title':'Error: Resource not found!',
                    'year':datetime.now().year,
                    'learning_resources':learning_resources,
                })


#lists a content creator's draft uploads
@login_required
def list_creator_draft_courses(request, creator_id):
    creator = User.objects.get(id=creator_id)
    learning_resources = LearningResource.objects.filter(created_by=creator,is_deleted=False,publish_status="Draft")

    if learning_resources is not None:
        return render(
                request,
                'staff/learning/list.html',
                {
                    'title':'Learning Resources by ' +creator.first_name,
                    'year':datetime.now().year,
                    'learning_resources':learning_resources,
                })
    else:
        return render(
                request,
                'staff/learning/list.html',
                {
                    'title':'Error: Resource not found!',
                    'year':datetime.now().year,
                    'learning_resources':learning_resources,
                })


#lists a content creator's saved courses
def list_creator_saved_courses(request, creator_id):
    pass

def view_learning_resource(request,id):
    resource = LearningResource.objects.get(id=id)
    learning_modules = LearningResourceModule.objects.filter(resource=resource)
    
    #record view
    if request.user.is_authenticated:
        view = LearningResourceView()
        view.resource = resource
        view.viewer = request.user
        view.save()

    if resource is not None:
        return render(
                request,
                'staff/learning/view.html',
                {
                    'title':resource.title,
                    'year':datetime.now().year,
                    'resource':resource,
                    'learning_modules':learning_modules,
                })
    else:
        return render(
                request,
                'staff/dashboard.html',
                {
                    'title':'ResourceNotFoundError',
                    'message':'Something wrong happened. Learning resource does not exits!',
                    'year':datetime.now().year,
                })


@login_required
def remove_learning_resource(request,id):
    learning_resource = LearningResource.objects.get(id=id)
    learning_resource.is_deleted = True

    return render(
            request,
            'staff/learning/list.html',
            {
                'title':learning_resource.title,
                'year':datetime.now().year,
                'learning_resource':learning_resource,
            })

#enrol for a course
@login_required
def enrol_course(request, resource_id):
    learning_resource = LearningResource.objects.get(id=resource_id)
    try:
        check_if_record_exists=LearningResourceEnrolment.objects.get(resource=learning_resource,learner=request.user)
        check_if_record_exists.status = True
        check_if_record_exists.save()



    except:

        enrol = LearningResourceEnrolment.objects.get(resource=learning_resource,learner=request.user)
   
        enrolment = LearningResourceEnrolment()
        enrolment.resource = learning_resource
        enrolment.learner = request.user
        enrolment.status = True
        enrolment.save() 

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def unrol_course(request, resource_id):#very suspicious name but you get it
    learning_resource = LearningResource.objects.get(id=resource_id)

    enrolment = LearningResourceEnrolment.objects.get(resource=learning_resource,learner=request.user)
    
    enrolment.status = False
    enrolment.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def mark_module_done(request, module_id):
    pass

def post_course_review(request):
    if request.method == 'POST':
        if request.POST.get('course_id'):
            resource = LearningResource.objects.get(id=request.POST.get('course_id'))
            learner = LearningResourceEnrolment.objects.get(resource=resource,learner=request.user)
            form=LearningResourceReviewForm(request.POST)
            if form.is_valid():
                l_resource = form.save(commit=False)
                l_resource.resource = resource
                l_resource.learner = learner
                l_resource.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

#search for course
def search_learning_resource(request):
    if request.method == 'POST':
        if request.POST.get('key'):
            search_tag = request.POST.get('key')
            result_list = []
            resources = LearningResource.objects.filter(
                Q(title__icontains=search_tag)
               | Q(description__icontains=search_tag)
               | Q(tags__icontains=search_tag)
               | Q(type__icontains=search_tag)
               | Q(overview__icontains=search_tag),
               is_deleted=False
               )

            #add to list
            for resource in resources:
                result_list.append(resource)


            #search in modules and add to list
            modules = LearningResourceModule.objects.filter(
                Q(title__icontains=search_tag)
               | Q(summary__icontains=search_tag)
                )
            #add to list
            for module in modules:
                if module.resource not in result_list:
                    result_list.append( module.resource)

                #search urls
            module_urls = LearningResourceModuleReferenceUrl.objects.filter(
                Q(name_of_website__icontains=search_tag)
               | Q(reference_material_url__icontains=search_tag)
                )
            #add to list
            for url in module_urls:
                if url.module.resource not in result_list:
                    result_list.append( url.module.resource)

                #search document downloads
            module_downloads = LearningResourceModuleDownload.objects.filter(
                Q(name_of_document__icontains=search_tag)
               | Q(reference_material_download__icontains=search_tag)
                )
            #add to list
            for download in module_downloads:
                if download.module.resource not in result_list:
                    result_list.append( download.module.resource)



             #pagination
            paginator = Paginator(resources, 8)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            return render(
                request,
                'staff/learning/list.html',
                {
                    'title':'Search results for ' +search_tag,
                    'year':datetime.now().year,
                    'learning_resources':result_list,
                    'page_obj':page_obj,
                })

#mark topic as finished
def module_mark_complete(request):
    if request.method == "POST":
        module = LearningResourceModule.objects.get(id=request.POST.get('module_id'))
        learner = LearningResourceEnrolment.objects.get(resource=module.resource,learner=request.user)
        #return Exception(message)
        try:
            #check if record already exists, if yes set status to inactive/active
            completion = LearningResourceModuleCompletion.objects.get(module=module,learner=learner)
            if completion.status == True:
                completion.status = False
            else:
                completion.status = True
            completion.save()

        except:
            completion = LearningResourceModuleCompletion()
            completion.learner = learner
            completion.module = module
            completion.save()


        fail = 'something wrong!'
        success = 'we are good'
        #return Exception(message)

        return HttpResponse(success)

    


def learning_resource_analytics(request,id):
    pass

######################################################################################################



######################################################################################################
################=========Repository Views=============############################################

#upload class
class BasicUploadView(View):
    def get(self, request):
        photos_list = RepositoryResourceImage.objects.all()
        return render(self.request, 'staff/repository/update.html', {'photos': photos_list})

    def post(self, request):
        
        resource = KotdaRepositoryResource.objects.get(id=request.POST.get('resource_id'))
        #if resource.upload_type == 'document':
        form = RepositoryResourceDownloadForm(self.request.POST, self.request.FILES)
        #elif resource.upload_type == 'image':
        image_form = RepositoryResourceImageForm(self.request.POST, self.request.FILES)
        #elif resource.upload_type == 'video':
        video_form = RepositoryResourceVideoUrlForm(request.POST, request.FILES)

        if resource.upload_type == 'document':
            if form.is_valid():
            
                #document_validator = FileTypeValidator(
                #    allowed_types=['application/*','text/*'],
                #    allowed_extensions=['.doc', '.docx', '.pdf', '.PDF', '.txt']
                #)

                file_upload = form.save(commit=False)
                file_upload.repository = resource
            
                file_upload.name_of_document = request.FILES.get('reference_material_download').name
                file_upload.publish_status='Draft'
                file_upload.save()
                #TODO::validation of file extensions. seems to be a futile event if the purpose is to protect from hackers

                data = {'is_valid': True, 'name': file_upload.reference_material_download.name, 'url': file_upload.reference_material_download.url}

            
            else:
                data = {'is_valid': False}
            return JsonResponse(data)


        elif resource.upload_type == 'image':
            if image_form.is_valid():
            
                

                file_upload = image_form.save(commit=False)
                file_upload.repository = resource
                file_upload.publish_status='Draft'
                file_upload.name_of_image = request.FILES.get('image').name
                file_upload.save()
                #TODO::validation of file extensions

                data = {'is_valid': True, 'name': file_upload.image.name, 'url': file_upload.image.url}

            
            else:
                data = {'is_valid': False}
            return JsonResponse(data)
        elif resource.upload_type == 'video':
            if video_form.is_valid():
            
               

                file_upload = video_form.save(commit=False)
                file_upload.repository = resource
                file_upload.publish_status='Draft'
                file_upload.name_of_video = request.FILES.get('video_file').name
                file_upload.save()
                #TODO::validation of file extensions

                data = {'is_valid': True, 'name': file_upload.video_file.name, 'url': file_upload.video_file.url}
            
            else:
                data = {'is_valid': False}
            return JsonResponse(data)


#check_repo_capacity
def check_repo_capacity(resource_id):
    resource = KotdaRepositoryResource.objects.get(id=resource_id)

    if resource.get_documents.count() <= 0:
        return JsonResponse(False)
    else:
        return JsonResponse(True)


###get the create repo page
@login_required
def get_create_repo_resource(request, upload_type=''):
    form = KotdaRepositoryResourceForm()
    resource = KotdaRepositoryResource()
    if upload_type == 'video':
        resource.upload_type = 'video'
    elif upload_type == 'image':
        resource.upload_type = 'image'
    else:
        resource.upload_type = 'document'

    resource.title = 'UNTITLED'
    resource.created_by = request.user
    #it will be set to draft by default
    resource.save()

    return redirect('get_update_repo_resource',repository_id=resource.id)
    return render(
            request,
            'staff/repository/create.html',
            {
                'title':"Create new resource",
                'year':datetime.now().year,
                'form':form,
                'resource':resource
            })


###create a repo object
@login_required
def create_repo_resource(request):
    if request.method == 'POST':
        form=KotdaRepositoryResourceForm(request.POST)
        if request.POST.get('file'):
            return HttpResponse('wayude')
        if form.is_valid():
            repo_resource = form.save(commit=False)
            repo_resource.created_by = request.user
            repo_resource.access_level = 'Restricted'
           
            repo_resource.save()

            return redirect('get_update_repo_resource', repository_id=repo_resource.id)

        
    messages.add_message(request, messages.ERROR, 'An error occured. Resource can not be created. Contact Konza ICT Office for support')        
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

#get user dahsboard
def get_user_dashboard(request, user_id, tab =''):
    user = User.objects.get(id=user_id)
    
    form = ProfileForm(instance=user)

    #check tab
    if tab == 'images':
        payload = user.get_my_images()
    elif tab == 'documents':
        payload = user.get_my_documents()
    elif tab == 'videos':
        payload = user.get_my_videos()
    elif tab == 'edit':
        payload = []
    else:
        tab = 'overview'
        payload = user.get_overview()

    if user:
        return render(
                request,
                'staff/repository/repo_dashboard.html',
                {
                    'title':user.user_name,
                    'year':datetime.now().year,
                    'user':user,
                    'tab':tab,
                    'payload':payload,
                    'form':form
                })

#to update repo page
@login_required
def get_update_repo_resource(request, repository_id, step=''):
    resource = KotdaRepositoryResource.objects.get(id=repository_id)
    if resource is not None:
        

        # dictionary for initial data with  
        # field names as keys 
        initial_dict = { 
            "title" : resource.title, 
            "description" : resource.description, 
            "tags":resource.tags, 
            #"type":resource.type
        } 

        if step == '':
            step = 'upload'
         

        form = KotdaRepositoryResourceForm(instance=resource)
        return render(
                request,
                'staff/repository/update.html',
                {
                    'title':resource.title,
                    'year':datetime.now().year,
                    'resource':resource,
                    'form':form,
                    'step':step
                })



@login_required
def post_update_repo_resource(request):
    if request.method == 'POST':
        resource = KotdaRepositoryResource.objects.get(id=request.POST.get('resource_id'))
        form = KotdaRepositoryResourceForm(request.POST, instance=resource)
        
                
        if form.is_valid() and resource is not None:
            repo = form.save(commit=False)
            repo.save()
            #raise Exception(request.POST)
            folder = RepositoryDocumentFolder.objects.get(id=request.POST.get('department_folder'))

            if folder:
                resource.department_folder = folder
            else:
                 messages.add_message(request, messages.ERROR, 'An error occured. You must select a valid department folder to add the resource')
                 return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            if request.POST.getlist('tags[]'):
                resource.tags = request.POST.getlist('tags[]')
            
            resource.save()

            #save department relationship start#
            if request.POST.getlist('department[]'):
                
                try:
                    for dept in request.POST.getlist('department[]'):
                        if 'multiselect-all' in dept:
                            pass
                        else:
                            department = Department.objects.get(id=dept)
                            match_relationship = RepositoryDepartment.objects.filter(repository=resource,department=department)
                            if not match_relationship:
                                repo_dept = RepositoryDepartment()
                                repo_dept.repository = resource
                                repo_dept.department = department
                                repo_dept.save()
                    
                       
                except:
                     #raise Exception(request.POST.getlist('department[]'))
                     messages.add_message(request, messages.ERROR, 'An error occured. Department could not be saved. Contact Konza ICT Office for support')
                #save department relationship end

            messages.add_message(request, messages.SUCCESS, 'Resource saved successfully')       
            return redirect('get_update_repo_resource', repository_id=resource.id, step='confirm')
        else:
            messages.add_message(request, messages.ERROR, 'An error occured. Resource can not be validated. Contact Konza ICT Office for support')
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def publish_resource(request, resource_id):
    resource = KotdaRepositoryResource.objects.get(id=resource_id)

    if resource.created_by == request.user:
        resource.publish_status = 'Published'
        resource.is_deleted = False
        resource.save()

        messages.add_message(request, messages.SUCCESS, 'Resource published successfully')       

        if resource.upload_type == 'document':
            doc = RepositoryResourceDownload.objects.filter(repository=resource,is_deleted=False)
            #raise Exception(doc)
            return redirect('view_document', document_id=doc[0].id)

        #if its an image redirect to view image page
        elif resource.upload_type == 'image':
            image = RepositoryResourceImage.objects.filter(repository=resource,is_deleted=False)
            return redirect('view_image', image_id=image[0].id)

        #if its an image redirect to view image page
        elif resource.upload_type == 'video':
            video = RepositoryResourceVideoUrl.objects.filter(repository=resource,is_deleted=False)
            return redirect('play_repo_video', video_id=video[0].id)

        else:
            return redirect('get_user_dashboard', user_id=request.user.id, tab='overview')

    else:
        messages.add_message(request, messages.ERROR, '(ACCESS_DENIED) An error occured. Resource can not be validated. Contact Konza ICT Office for support')
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def view_repository_media(request, resource_id):
    resource = KotdaRepositoryResource.objects.get(id=resource_id)
    if resource is not None:
        return render(
                request,
                'staff/repository/media_view.html',
                {
                    'title':resource.title,
                    'year':datetime.now().year,
                    'resource':resource,
                })

#repo index page
def repository_index(request):
    return render(
                request,
                'staff/repository/index.html',
                {
                    'title':'Repsitory index',
                    'year':datetime.now().year,

                })


#filter repo by department
def filter_repo_by_dept(request, dept_id):
        
        
        resources = []
        department = Department.objects.get(id=dept_id)
        repo_dept = RepositoryDepartment.objects.filter(department=department)
        folder_relationships = DepartmentFolderRelationship.objects.filter(department=department)
       
        #add to list depending on reuest.user
        if not request.user.is_authenticated:
            for resource in repo_dept:
                if 'Published' in resource.repository.publish_status and 'Public' in resource.repository.access_level:
                    resources.append(resource.repository)

        elif request.user.is_authenticated:
            for resource in repo_dept:
                    if 'Published' in resource.repository.publish_status:
                       if 'Public' in resource.repository.access_level:
                            resources.append(resource.repository)
                       elif 'Internal' in resource.repository.access_level:
                            resources.append(resource.repository)
                       elif 'Restricted' in resource.repository.access_level:
                           #get the relationship
                           if request.user.profile.department in resource.repository.get_host_departments():
                                resources.append(resource.repository)
        
        

         #pagination
        paginator = Paginator(resources, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        

        return render(
                request,
                'staff/repository/media_view.html',
                {
                    'title':department,
                    'year':datetime.now().year,
                    'resources':resources,
                    'department':department,
                    'page_obj': page_obj,
                    'folder_relationships':folder_relationships,
                    'perspective':'department',
                })

#get repo articles by department
def get_repo_articles_by_dept(request, dept_id):
        
        resources = []
        department = Department.objects.get(id=dept_id)
        repo_dept = RepositoryDepartment.objects.filter(department=departments)

        #add to list
        for resource in repo_dept:
            if resource.repository.publish_status == 'Published':
                resources.append(resource.repository)
        
        folder_relationships = DepartmentFolderRelationship.objects.filter(department=dept)

         #pagination
        paginator = Paginator(resources, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        

        return render(
                request,
                'staff/repository/media_view.html',
                {
                    'title':department,
                    'year':datetime.now().year,
                    'resources':resources,
                    'department':department,
                    'page_obj': page_obj,
                    'folder_relationships':folder_relationships,
                    'perspective':'department',
                })


#get repo images by type
def get_repo_images_by_dept(request, dept_id):
       
        resources = []
        department = Department.objects.get(id=dept_id)
        repo_dept = RepositoryDepartment.objects.filter(department=department)

        #add to list depending on reuest.user
        if not request.user.is_authenticated:
            for resource in repo_dept:
                if resource.repository.get_images():
                    if 'Published' in resource.repository.publish_status and 'Public' in resource.repository.access_level:
                        resources.append(resource.repository)
        elif request.user.is_authenticated:
            for resource in repo_dept:
                if resource.repository.get_images():
                    if 'Published' in resource.repository.publish_status:
                       if 'Public' in resource.repository.access_level:
                            resources.append(resource.repository)
                       elif 'Internal' in resource.repository.access_level:
                            resources.append(resource.repository)
                       elif 'Restricted' in resource.repository.access_level:
                           #get the relationship
                           if request.user.profile.department in resource.repository.get_host_departments():
                                resources.append(resource.repository)

         #pagination
        paginator = Paginator(resources, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(
                request,
                'staff/repository/media_view.html',
                {
                    'title':str(department) + ' photos',
                    'year':datetime.now().year,
                    'resources':resources,
                    'department':department,
                    'page_obj': page_obj,
                    'perspective':'department',
                })


#get repo images by type
def get_repo_videos_by_dept(request, dept_id):
       
        resources = []
        department = Department.objects.get(id=dept_id)
        repo_dept = RepositoryDepartment.objects.filter(department=department)

        #add to list depending on reuest.user
        if not request.user.is_authenticated:
            for resource in repo_dept:
                if resource.repository.get_videos():
                    if 'Published' in resource.repository.publish_status:
                        if 'Published' in resource.repository.publish_status and 'Public' in resource.repository.access_level:
                            resources.append(resource.repository)

        elif request.user.is_authenticated:#user is authenticated
            for resource in repo_dept:
                if resource.repository.get_videos():
                    if 'Published' in resource.repository.publish_status:
                       if 'Public' in resource.repository.access_level:
                            resources.append(resource.repository)
                       elif 'Internal' in resource.repository.access_level:
                            resources.append(resource.repository)
                       elif 'Restricted' in resource.repository.access_level:
                           #get the relationship
                           if request.user.profile.department in resource.repository.get_host_departments():
                                resources.append(resource.repository)




         #pagination
        paginator = Paginator(resources, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(
                request,
                'staff/repository/media_view.html',
                {
                    'title':str(department) + ' videos',
                    'year':datetime.now().year,
                    'resources':resources,
                    'department':department,
                    'perspective':'department',
                    'page_obj': page_obj,
                })

    #filter by document type
def filter_repo_by_folder(request, folder_id):
    
    #try:
        #get the folder
    folder = RepositoryDocumentFolder.objects.get(id=folder_id, is_deleted=False)
    if folder:
        #get the related folders
        folder_relationships = folder.get_folder_relationship()

        
        resources = KotdaRepositoryResource.objects.filter(department_folder=folder, publish_status='Published', is_deleted=False)
        
        #check privacy and store result in collection
        filtered_resources = []

        #raise Exception(resources)
        if request.user.is_authenticated == True:
            for resource in resources:
                if "Public" in resource.access_level  or "Internal" in resource.access_level:
                    filtered_resources.append(resource)
                elif "Restricted" in resource.access_level:
                        if  request.user.profile.department in resource.get_host_departments():
                            filtered_resources.append(resource)


        #get results for unauthorized users
        elif request.user.is_authenticated == False:
            for resource in resources:
                if "Public" in resource.access_level:
                    filtered_resources.append(resource)

        
                


        #raise Exception(filtered_resources)
            #pagination
        paginator = Paginator(filtered_resources, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(
                request,
                'staff/repository/media_view.html',
                {
                    'title':folder,
                    'year':datetime.now().year,
                    'resources':filtered_resources,
                    'perspective':'folder',
                    'current_folder':folder,
                    'folder_relationships':folder_relationships,
                    'page_obj': page_obj,
                })


    else:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    

#create new doc type
@login_required
def create_document_folder(request):
    if request.method == 'POST':
        form = RepositoryDocumentFolderForm(request.POST)
        if form.is_valid():
            
            folder = form.save(commit=False)
            folder.created_by = request.user
            folder.save()

            
            relationship = DepartmentFolderRelationship()
            relationship.folder = folder
            if request.POST.get('parent_folder_id'):#if is sub folder
                paro = RepositoryDocumentFolder.objects.get(id=request.POST.get('parent_folder_id')) or None
                relationship.parent = paro
            if request.POST.get('department'): 
                if request.user.is_superuser:#check if this was submitted by a superuser if not arudi penye ametoka
                    relationship.department = Department.objects.get(id=request.POST.get('department'))
                else:
                    messages.add_message(request, messages.ERROR, '(ACCESS_DENIED) An error occured. Resource can not be validated. Contact Konza ICT Office for support')
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            else:
                relationship.department = Department.objects.get(id=request.user.profile.department.id)
            relationship.created_by = request.user
            relationship.save()

            messages.add_message(request, messages.SUCCESS, 'Folder created successfully')
                
            


    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def update_document_folder(request):
    if request.method == 'POST':
        if request.POST.get('folder_id'):#if is sub folder
            folder = RepositoryDocumentFolder.objects.get(id=request.POST.get('folder_id')) or None
            form = RepositoryDocumentFolderForm(request.POST, instance=folder)
        if form.is_valid():
            
            folder = form.save(commit=False)
            folder.created_by = request.user
            folder.save()

            if request.POST.get('department'):
                relationship = DepartmentFolderRelationship.objects.get(folder=folder)
                relationship.folder = folder
  
                relationship.department = Department.objects.get(id=request.POST.get('department'))
                relationship.created_by = request.user
                relationship.save()

                #raise Exception(relationship)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



#search for a resource
def search_repository(request):
    if request.method == 'POST':
        #search for the tag
        search_tag = request.POST.get('q')

        repos = KotdaRepositoryResource.objects.filter(
                Q(title__icontains=search_tag)
               | Q(description__icontains=search_tag)
               | Q(tags__icontains=search_tag)
               | Q(upload_type__icontains=search_tag)
               )

        repos.exclude(is_deleted=True ,publish_status="Draft")

        #search actual resources
        docs = RepositoryResourceDownload.objects.filter(
            Q(name_of_document__icontains=search_tag)
            | Q(reference_material_download__icontains=search_tag)
            )

        docs.exclude(is_deleted=True)

        pics = RepositoryResourceImage.objects.filter(
            Q(name_of_image=search_tag)
            | Q(image__icontains=search_tag)
            )

        pics.exclude(is_deleted=True)

        videos = RepositoryResourceVideoUrl.objects.filter(
            Q(name_of_video=search_tag)
            | Q(video_file=search_tag)
            )

        videos.exclude(is_deleted=True)

        #sort the results in array
        resources = []

        for repo in repos:
            if "Published" in repo.publish_status and repo.is_deleted == False:
                #get results for unauthorized users
                if not request.user.is_authenticated:
                    if "Public" in repo.access_level:
                        resources.append(repo)
                #get results for authorized users
                else:
                    if "Public" in repo.access_level:
                        resources.append(repo)
                    if "Internal" in repo.access_level:
                        resources.append(repo)
                    if "Restricted" in repo.access_level:
                        if  request.user.profile.department in repo.get_host_departments():
                            resources.append(repo)
                    #todo: confidential check

        #sort documents
        for doc in docs:
            if "Published" in doc.repository.publish_status and doc.repository.is_deleted == False and doc.is_deleted == False:
                #get results for unauthorized users
                if not request.user.is_authenticated:
                    if "Public" in doc.repository.access_level:
                        if doc.repository not in resources:
                            resources.append(doc.repository)
                    #get results for authorized users
                else:
                    if "Public" in doc.repository.access_level:
                        if doc.repository not in resources:
                            resources.append(doc.repository)
                    if "Internal" in doc.repository.access_level:
                        if doc.repository not in resources:
                            resources.append(doc.repository)
                    if "Restricted" in doc.repository.access_level:
                        if request.user.profile.department in doc.repository.get_host_departments():
                            if doc.repository not in resources:
                                resources.append(doc.repository)
                    #todo: confidential check

        #sort pictures
        for pic in pics:
            if "Published" in pic.repository.publish_status and pic.repository.is_deleted == False and pic.is_deleted == False:

                #get results for unauthorized users
                if not request.user.is_authenticated:
                    if"Public" in pic.repository.access_level:
                        if pic.repository not in resources:
                            resources.append(pic.repository)
                    #get results for authorized users
                else:
                    if "Public" in pic.repository.access_level:
                        if pic.repository not in resources:
                            resources.append(pic.repository)
                    if "Internal" in pic.repository.access_level:
                        if pic.repository not in resources:
                            resources.append(pic.repository)
                    if "Restricted" in pic.repository.access_level:
                        if request.user.profile.department in pic.repository.get_host_departments():
                            if pic.repository not in resources:
                                resources.append(pic.repository)
                    #todo: confidential check


          #sort videos
        for video in videos:
            if video.repository.publish_status == "Published" and video.repository.is_deleted == False and video.is_deleted == False:

                #get results for unauthorized users
                if not request.user.is_authenticated:
                    if "Public" in video.repository.access_level:
                        if video.repository not in resources:
                            resources.append(video.repository)
                    #get results for unauthorized users
                else:
                    if "Internal" in video.repository.access_level:
                        if video.repository not in resources:
                            resources.append(video.repository)
                    if "Restricted" in video.repository.access_level:
                        if request.user.profile.department in video.repository.get_host_departments():
                            if video.repository not in resources:
                                resources.append(video.repository)
                    #todo: confidential check

        return get_search(request, search_tag, resources)

         #pagination
        #paginator = Paginator(resources, 5)
        #page_number = request.GET.get('page')
        #page_obj = paginator.get_page(page_number)
        #return render(
        #        request,
        #        'staff/repository/media_view.html',
        #        {
        #            'title':search_tag+' search results',
        #            'year':datetime.now().year,
        #            'resources':resources,
        #            'search_tag':search_tag,
        #            'page_obj': page_obj,
        #        })
    else:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



#search page
def get_search(request, search_tag, resources):
     #pagination
    paginator = Paginator(resources, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(
            request,
            'staff/repository/media_view.html',
            {
                'title':'"'+search_tag+'"'+' search results',
                'year':datetime.now().year,
                'resources':resources,
                'search_tag':search_tag,
                'page_obj': page_obj,
            })


#download a file and record activity
def download_file(request, document_id):
    document = RepositoryResourceDownload.objects.get(id=document_id, is_deleted=False)

    # fill these variables with real values
    fl_path = document.reference_material_download.path
    file_extension = pathlib.Path(document.reference_material_download.name).suffix
    filename = document.name_of_document+file_extension

    fl = open(fl_path, 'r')
    mime_type, _ = mimetypes.guess_type(fl_path)
    response = HttpResponse(fl, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    stat = RepositoryDocumentDownloadStat()
    stat.document = document
    stat.downloaded_by = request.user
    stat.save()

    return response




#delete an image
@login_required
def delete_repo_image(request, image_id):
    image = RepositoryResourceImage.objects.get(id = image_id)
    if image:
        if image.repository.created_by == request.user or request.user.is_superuser == True:
            image.is_deleted = True
            image.deleted_by = request.user
            image.save()

            #should I delete the repo too?
            repo = KotdaRepositoryResource.objects.get(id=image.repository.id)

            if repo.get_images().count() <= 0 and repo.get_videos().count() <= 0 and repo.get_documents().count() <= 0:
                repo.is_deleted=True
                repo.publish_status='Rejected'
                repo.deleted_by = request.user
                repo.save()

            messages.add_message(request, messages.SUCCESS, 'Image deleted successfully')       
        else:
            messages.add_message(request, messages.ERROR, 'An error occured. Image could not be deleted. Contact Konza ICT Office for support')
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


#delete document
@login_required
def delete_repo_document(request, document_id):
    document = RepositoryResourceDownload.objects.get(id = document_id)
    if document:
        if document.repository.created_by == request.user or request.user.is_superuser == True:
            document.is_deleted = True
            document.deleted_by = request.user
            document.save()

            
            #should I delete the repo too?
            repo = KotdaRepositoryResource.objects.get(id=document.repository.id)

            if repo.get_images().count() <= 0 and repo.get_videos().count() <= 0 and repo.get_documents().count() <= 0:
                repo.is_deleted=True
                repo.publish_status='Rejected'
                repo.deleted_by = request.user
                repo.save()

            messages.add_message(request, messages.SUCCESS, 'Document deleted successfully')       
        else:
            messages.add_message(request, messages.ERROR, 'An error occured. Document could not be deleted. Contact Konza ICT Office for support')
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


#delete video
@login_required
def delete_repo_video(request, video_id):
    video = RepositoryResourceVideoUrl.objects.get(id = video_id)
    if video:
        if video.repository.created_by == request.user or request.user.is_superuser == True:
            video.is_deleted = True
            video.deleted_by = request.user
            video.save()

            
            #should I delete the repo too?
            repo = KotdaRepositoryResource.objects.get(id=video.repository.id)

            if repo.get_images().count() <= 0 and repo.get_videos().count() <= 0 and repo.get_documents().count() <= 0:
                repo.is_deleted=True
                repo.publish_status='Rejected'
                repo.deleted_by = request.user
                repo.save()

            messages.add_message(request, messages.SUCCESS, 'Video deleted successfully')       
        else:
            messages.add_message(request, messages.ERROR, 'An error occured. Video could not be deleted. Contact Konza ICT Office for support')
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


#delete folder
@login_required
def delete_repo_folder(request, folder_id):
    folder = RepositoryDocumentFolder.objects.get(id=folder_id)
    if folder:
        if folder.is_static == False and folder.folder_isempty():
           # raise Exception("what the fuck")
            folder.is_deleted = True
            folder.deleted_by = request.user
            folder.save()

            messages.add_message(request, messages.SUCCESS, 'Folder deleted successfully')       

        elif folder.is_static == True:
            messages.add_message(request, messages.ERROR, 'An error occured. Folder could not be deleted. Note, default folders cannot be deleted.')
        elif folder.folder_isempty == False:
            messages.add_message(request, messages.ERROR, 'An error occured. Folder could not be deleted. Make sure the folder is empty before deleting.')
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

#play video
def play_repo_video(request, video_id):
    video = RepositoryResourceVideoUrl.objects.get(id = video_id)
    if video:

        #record click
        try:
            stat = RepositoryResourceViewStat()
            stat.repository = video.repository
            if request.user.is_authenticated:
                stat.viewer = request.user
            stat.anwani_ip = visitor_ip_address(request)
            stat.save()
        except:
            pass
        
        #security check
        if video.repository.access_level == "Public":
            return render(
                request,
                'staff/repository/video_player.html',
                {
                    'title':video.name_of_video,
                    'year':datetime.now().year,
                    'video':video,
                    
                })
        if request.user.is_authenticated:
            if "Internal" in video.repository.access_level:
                    return render(
                        request,
                        'staff/repository/video_player.html',
                        {
                            'title':video.name_of_video,
                            'year':datetime.now().year,
                            'video':video,
                    
                        })

            if "Restricted" in video.repository.access_level:
                    if request.user.profile.department in video.repository.get_host_departments():
                        return render(
                            request,
                            'staff/repository/video_player.html',
                            {
                                'title':video.name_of_video,
                                'year':datetime.now().year,
                                'video':video,
                    
                            })

        
        
    else:
        messages.add_message(request, messages.ERROR, 'An error occured. Video could not be loaded. Contact Konza ICT Office for support')
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


#view image
def view_image(request, image_id):
    image = RepositoryResourceImage.objects.get(id = image_id)
    if image:

        #record click
        try:
            stat = RepositoryResourceViewStat()
            stat.repository = image.repository
            if request.user.is_authenticated:
                stat.viewer = request.user
            stat.anwani_ip = visitor_ip_address(request)
            stat.save()
        except:
            pass

        #security check
        if 'Public' in image.repository.access_level:
            return render(
                request,
                'staff/repository/photo_view.html',
                {
                    'title':image.name_of_image,
                    'year':datetime.now().year,
                    'image':image,
                    
                })
        if 'Internal' in image.repository.access_level:
            if request.user.is_authenticated:
                return render(
                    request,
                    'staff/repository/photo_view.html',
                    {
                        'title':image.name_of_image,
                        'year':datetime.now().year,
                        'image':image,
                    
                    })
        if 'Restricted' in image.repository.access_level:
            if request.user.is_authenticated:
                if request.user.profile.department in image.repository.get_host_departments():
                    return render(
                        request,
                        'staff/repository/photo_view.html',
                        {
                            'title':image.name_of_image,
                            'year':datetime.now().year,
                            'image':image,
                    
                        })


    else:
        messages.add_message(request, messages.ERROR, 'An error occured. Image could not be loaded. Contact Konza ICT Office for support')
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))




#view document
def view_document(request, document_id):
    document = RepositoryResourceDownload.objects.get(id = document_id)
    if document:

        #record click
        try:
            stat = RepositoryResourceViewStat()
            stat.repository = document.repository
            if request.user.is_authenticated:
                stat.viewer = request.user
            stat.anwani_ip = visitor_ip_address(request)
            stat.save()
        except:
            pass

        #raise Exception(document)
        #security check
        if "Public" in document.repository.access_level:
            return render(
                request,
                'staff/repository/document_view.html',
                {
                    'title':document.name_of_document,
                    'year':datetime.now().year,
                    'document':document,
                    
                })
        if "Internal" in document.repository.access_level:
            if request.user.is_authenticated:
                return render(
                    request,
                    'staff/repository/document_view.html',
                    {
                        'title':document.name_of_document,
                        'year':datetime.now().year,
                        'document':document,
                    
                    })
        if "Restricted" in document.repository.access_level:
            if request.user.is_authenticated:
                if request.user.profile.department in document.repository.get_host_departments():
                    return render(
                            request,
                            'staff/repository/document_view.html',
                            {
                                'title':document.name_of_document,
                                'year':datetime.now().year,
                                'document':document,
                    
                            })

    else:
        messages.add_message(request, messages.ERROR, 'An error occured. Document could not be loaded. Contact Konza ICT Office for support')
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def bookmark_document(request, document_id=''):
    if request.method == "POST":
        doc = RepositoryResourceDownload.objects.get(id=request.POST.get('module_id'))
        #return Exception(message)
        try:
            #check if record already exists, if yes set status to inactive/active
            mark = RepositoryDocumentBookmark.objects.get(document=doc,marked_by=request.user)
            if mark.status == True:
                mark.status = False
                message = 'Bookmark'
            elif mark.status == False:
                mark.status = True
                message = 'Bookmarked'
            mark.anwani_ip = visitor_ip_address(request)
            mark.save()
            

        except:
            mark = RepositoryDocumentBookmark()
            mark.marked_by = request.user
            mark.document = doc
            mark.anwani_ip = visitor_ip_address(request)
            mark.save()
            message = 'Bookmarked'


        fail = 'Bookmark Fail!'
        success = message
        #return Exception(message)

        return HttpResponse(success)


@login_required
def bookmark_image(request, image_id=''):
    if request.method == "POST":
        img = RepositoryResourceImage.objects.get(id=request.POST.get('module_id'))
        #return Exception(message)
        try:
            #check if record already exists, if yes set status to inactive/active
            mark = RepositoryImageBookmark.objects.get(image=img,marked_by=request.user)
            if mark.status == True:
                mark.status = False
                message = 'Bookmark'
            elif mark.status == False:
                mark.status = True
                message = 'Bookmarked'
            mark.anwani_ip = visitor_ip_address(request)
            mark.save()
            

        except:
            mark = RepositoryImageBookmark()
            mark.marked_by = request.user
            mark.image = img
            mark.anwani_ip = visitor_ip_address(request)
            mark.save()
            message = 'Bookmarked'


        fail = 'Bookmark Fail!'
        success = message
        #return Exception(message)

        return HttpResponse(success)


@login_required
def bookmark_video(request, video_id=''):
    if request.method == "POST":
        vid = RepositoryResourceVideoUrl.objects.get(id=request.POST.get('module_id'))
        #return Exception(message)
        try:
            #check if record already exists, if yes set status to inactive/active
            mark = RepositoryVideoBookmark.objects.get(video=vid,marked_by=request.user)
            if mark.status == True:
                mark.status = False
                message = 'Bookmark'
            elif mark.status == False:
                mark.status = True
                message = 'Bookmarked'
            mark.anwani_ip = visitor_ip_address(request)
            mark.save()
            

        except:
            mark = RepositoryVideoBookmark()
            mark.marked_by = request.user
            mark.video = vid
            mark.anwani_ip = visitor_ip_address(request)
            mark.save()


        fail = 'Bookmark Fail!'
        success = message
        #return Exception(message)

        return HttpResponse(success)


@login_required
def get_my_bookmarks(request):
    bookmarks = []

    doc_marks = RepositoryDocumentBookmark.objects.filter(marked_by=request.user, status=True)
    for doc in doc_marks:
        bookmarks.append(doc.document.repository)

    image_marks = RepositoryImageBookmark.objects.filter(marked_by=request.user, status=True)
    for img in image_marks:
        bookmarks.append(img.image.repository)

    video_marks = RepositoryVideoBookmark.objects.filter(marked_by=request.user, status=True)
    for vid in video_marks:
        bookmarks.append(vid.video.repository)


    return render(
            request,
            'staff/repository/media_view.html',
            {
                'title':'Bookmarks',
                'year':datetime.now().year,
                'resources':bookmarks,
            })
 

######################################################################################################




class PollListView(ListView):
    """Renders the home page, with a list of all polls."""
    model = Poll

    def get_context_data(self, **kwargs):
        context = super(PollListView, self).get_context_data(**kwargs)
        context['title'] = 'Polls'
        context['year'] = datetime.now().year
        return context

class PollDetailView(DetailView):
    """Renders the poll details page."""
    model = Poll

    def get_context_data(self, **kwargs):
        context = super(PollDetailView, self).get_context_data(**kwargs)
        context['title'] = 'Poll'
        context['year'] = datetime.now().year
        return context

class PollResultsView(DetailView):
    """Renders the results page."""
    model = Poll

    def get_context_data(self, **kwargs):
        context = super(PollResultsView, self).get_context_data(**kwargs)
        context['title'] = 'Results'
        context['year'] = datetime.now().year
        return context

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }
    )

def vote(request, poll_id):
    """Handles voting. Validates input and updates the repository."""
    poll = get_object_or_404(Poll, pk=poll_id)
    try:
        selected_choice = poll.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'app/details.html', {
            'title': 'Poll',
            'year': datetime.now().year,
            'poll': poll,
            'error_message': "Please make a selection.",
    })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('app:results', args=(poll.id,)))

@login_required
def seed(request):
    """Seeds the database with sample polls."""
    samples_path = path.join(path.dirname(__file__), 'samples.json')
    with open(samples_path, 'r') as samples_file:
        samples_polls = json.load(samples_file)

    for sample_poll in samples_polls:
        poll = Poll()
        poll.text = sample_poll['text']
        poll.pub_date = timezone.now()
        poll.save()

        for sample_choice in sample_poll['choices']:
            choice = Choice()
            choice.poll = poll
            choice.text = sample_choice
            choice.votes = 0
            choice.save()

    return HttpResponseRedirect(reverse('app:home'))

@login_required
def seed_departments(request):
    #seeds the database with department data##
    departments_path = path.join(path.dirname(__file__), 'departments.json')
    with open(departments_path, 'r') as departments_file:
        samples_departments = json.load(departments_file)

    for sample_department in samples_departments:
        department = Department()
        department.name = sample_department['department_name']
        department.description = sample_department['department_description']
        department.created_by = request.user
        department.save()

        for sample_folder in sample_department['folder']:
            folder = RepositoryDocumentFolder()
            folder.folder_name = sample_folder['folder_name']
            folder.description = sample_folder['description']
            folder.access_level = sample_folder['access_level']
            folder.is_static = sample_folder['is_static']
            folder.created_by = request.user
            folder.save()

            relationship = DepartmentFolderRelationship()
            relationship.folder = folder
            relationship.department = department
            relationship.created_by = request.user
            relationship.save()



    return HttpResponseRedirect(reverse('app:home'))