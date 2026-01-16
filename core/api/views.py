from warnings import filters
from django.conf import settings
from django.db.models import Q
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework_extensions.mixins import NestedViewSetMixin
from datetime import datetime
from core.models import *
from .serializers import *
from .utilities import get_ip_location


class ResourceViewSet(viewsets.ModelViewSet):
    serializer_class = ResourceSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.request.user.files.all()
        return queryset

    def create(self, request, *args, **kwargs):
        try:
            file_obj = request.FILES.get('file')
            category = request.POST['category']

            # # S3 upload
            # s3 = boto3.client(
            #     's3',
            #     aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            #     aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            #     region_name=getattr(settings, 'AWS_S3_REGION_NAME', None)
            # )
            # # Generate a unique filename
            # filename = f"{category}/{uuid.uuid4().hex}_{file_obj.name}"
            # s3.upload_fileobj(
            #     file_obj,
            #     settings.AWS_STORAGE_BUCKET_NAME,
            #     filename,
            #     ExtraArgs={'ACL': 'public-read'}
            # )
            # s3_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{filename}"

            # resource = Resource.objects.create(
            #     name=file_obj.name,
            #     category=category,
            #     file=s3_url,  # Save the S3 URL
            #     size=file_obj.size  # Save the file size
            # )

            resource = Resource.objects.create(
                name=file_obj.name,
                category=category,
                file="temporary_url",  # Save the S3 URL
                size="100 KB"  # Save the file size
            )

            serializer = ResourceSerializer(resource, context={'request': request})
            result = serializer.data

            return Response(result)
        except Exception as ex:
            return Response(str(ex), status=400)


class JobPostingViewSet(viewsets.ModelViewSet):
    serializer_class = JobPostingSerializer
    permission_classes = (AllowAny,)
    ordering = ['-created']

    def get_queryset(self):
        if self.action == 'list':
            filters = ~Q(status__in=['draft'])

            group = self.request.GET.get('group')
            if self.request.user and self.request.user.is_authenticated:
                if self.request.user.role == 'freelancer':
                    if group == 'saved':
                        saved_jobs = SavedJob.objects.filter(user=self.request.user)
                        job_posting_ids = saved_jobs.values_list('job_posting__id', flat=True)
                        filters &= Q(id__in=job_posting_ids)

                    if group == 'relevant':
                        user_profile = self.request.user.profile
                        skills = user_profile.skills.split(',') if user_profile.skills else []
                        relevant_q = Q()
                        for skill in skills:
                            relevant_q |= Q(skills__icontains=skill)
                        filters &= relevant_q
                    
                    if group == 'applied':
                        applied_jobs = JobApplication.objects.filter(user=self.request.user, status__in=['pending'])
                        job_posting_ids = applied_jobs.values_list('job_posting__id', flat=True)
                        filters &= Q(id__in=job_posting_ids)

                    if group == 'invited':
                        invited_jobs = JobInvitation.objects.filter(user=self.request.user, status__in=['pending'])
                        job_posting_ids = invited_jobs.values_list('job_posting__id', flat=True)
                        filters &= Q(id__in=job_posting_ids)

                    if group == 'interviewed':
                        interview_jobs = JobApplication.objects.filter(user=self.request.user, status='accepted')
                        job_posting_ids = interview_jobs.values_list('job_posting__id', flat=True)
                        filters &= Q(id__in=job_posting_ids)

                    if group == 'offered':
                        hired_jobs = JobOffer.objects.filter(user=self.request.user, status__in=['pending'])
                        job_posting_ids = hired_jobs.values_list('job_posting__id', flat=True)
                        filters &= Q(id__in=job_posting_ids)

                    if group == 'archived':
                        interview_jobs = JobApplication.objects.filter(user=self.request.user, status__in=['cancelled', 'rejected'])
                        job_posting_ids = interview_jobs.values_list('job_posting__id', flat=True)
                        filters &= Q(id__in=job_posting_ids)
                
                if self.request.user.role == 'client':
                    if group == 'all':
                        filters &= Q(user=self.request.user)
                    
                    if group == 'posted':
                        filters &= Q(user=self.request.user) & ~Q(status__in=['draft'])
                    
                    if group == 'draft':
                        filters &= Q(user=self.request.user, status='draft')

                    if group == 'interviewed':
                        interview_jobs = JobApplication.objects.filter(job_posting__user=self.request.user, status='accepted')
                        job_posting_ids = interview_jobs.values_list('job_posting__id', flat=True)
                        filters &= Q(id__in=job_posting_ids)

                    if group == 'hired':
                        hired_jobs = JobOffer.objects.filter(job_posting__user=self.request.user, status='accepted')
                        job_posting_ids = hired_jobs.values_list('job_posting__id', flat=True)
                        filters &= Q(id__in=job_posting_ids)

                    if group == 'finished':
                        finished_jobs = JobOffer.objects.filter(job_posting__user=self.request.user, status='completed')
                        job_posting_ids = finished_jobs.values_list('job_posting__id', flat=True)
                        filters &= Q(id__in=job_posting_ids)

            search = self.request.GET.get('search')
            if search:
                for word in search.split():
                    if word.strip() == "":
                        continue
                    filters &= Q(title__icontains=word) | Q(description__icontains=word)
            
            country = self.request.GET.get('country')
            if country:
                country_q = Q()
                for skill in country.split(','):
                    country_q |= Q(user__profile__country__icontains=skill)
                filters &= country_q

            timezone = self.request.GET.get('timezone')
            if timezone:
                timezone_q = Q()
                for skill in timezone.split(','):
                    timezone_q |= Q(user__profile__timezone__icontains=skill)
                filters &= timezone_q

            skills = self.request.GET.get('skills')
            if skills:
                skill_q = Q()
                for skill in skills.split(','):
                    skill_q |= Q(skills__icontains=skill)
                filters &= skill_q

            categories = self.request.GET.get('categories')
            if categories:
                category_q = Q()
                for category in categories.split(','):
                    category_q |= Q(categories__icontains=category)
                filters &= category_q

            compensation_type = self.request.GET.get('compensation_type')
            if compensation_type:
                filters &= Q(compensation_type=compensation_type)

                if compensation_type == 'hourly':
                    rate_min = self.request.GET.get('rate_min', None)
                    if rate_min:
                        filters &= Q(price__gte=rate_min)

                    rate_max = self.request.GET.get('rate_max', None)
                    if rate_max:
                        filters &= Q(price__lte=rate_max)
                else:
                    prices = self.request.GET.get('prices', None)
                    if prices:
                        price_q = Q()
                        for price in prices.split(','):
                            price_range = price.split('-')
                            price_min = price_range[0]
                            price_max = price_range[1]
                            price_q |= Q(price__gte=price_min, price__lte=price_max)

                        filters &= price_q
            
            duration = self.request.GET.get('duration')
            if duration and duration != 'any':
                filters &= Q(duration=duration)

            size = self.request.GET.get('size')
            if size and size != 'any':
                filters &= Q(size=size)
            
            proposals = self.request.GET.get('proposals')
            if proposals:
                proposal_q = Q()
                for proposal in proposals.split(','):
                    proposal_range = proposal.split('-')
                    proposal_min = proposal_range[0]
                    proposal_max = proposal_range[1]
                    proposal_q |= Q(proposal_count__gte=proposal_min, proposal_count__lte=proposal_max)

                filters &= proposal_q

            previous_jobs = self.request.GET.get('previous_jobs')
            if previous_jobs:
                previous_job_q = Q()
                for previous_job in previous_jobs.split(','):
                    previous_job_range = previous_job.split('-')
                    previous_job_min = previous_job_range[0]
                    previous_job_max = previous_job_range[1]
                    previous_job_q |= Q(user__profile__total_jobs_count__gte=previous_job_min, user__profile__total_jobs_count__lte=previous_job_max)

                filters &= previous_job_q

            rate_min = self.request.GET.get('hire_rate_min', None)
            if rate_min:
                filters &= Q(user__profile__hire_rate__gte=rate_min)

            rate_max = self.request.GET.get('hire_rate_max', None)
            if rate_max:
                filters &= Q(user__profile__hire_rate__lte=rate_max)

            queryset = JobPosting.objects.filter(filters)
        else:
            queryset = JobPosting.objects.filter(pk=self.kwargs['pk'])
        return queryset

    @action(methods=["post", "delete"], detail=True, permission_classes=[IsAuthenticated])
    def save(self, request, pk=None):
        job_posting = self.get_object()
        if request.method == "DELETE":
            SavedJob.objects.filter(user=request.user, job_posting=job_posting).delete()
            return Response({"status": "job unsaved"})
        else:
            SavedJob.objects.get_or_create(user=request.user, job_posting=job_posting)
            return Response({"status": "job saved"})

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class JobApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = JobApplicationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        if self.action == 'list':
            filters = Q(job_posting_id=self.kwargs["parent_lookup_job_posting__id"])

            group = self.request.GET.get('group')
            if group == 'all':
                pass
            
            if group == "interviewed":
                filters &= Q(status='accepted')
            
            if group == 'offered':
                filters &= Q(status='pending')
            
            if group == "archived":
                filters &= Q(status__in=['cancelled', 'rejected'])

            queryset = JobApplication.objects.filter(filters)
        else:
            queryset = JobApplication.objects.filter(pk=self.kwargs['pk'])
        return queryset

    def perform_create(self, serializer):
        job_invitation = JobInvitation.objects.filter(
            user=self.request.user,
            job_posting_id=self.kwargs["parent_lookup_job_posting__id"],
            status='pending'
        ).first()
        job_application_status = 'pending'
        if job_invitation:
            job_application_status = 'accepted'
            job_invitation.status = 'accepted'
            job_invitation.save()

        serializer.save(
            user=self.request.user,
            job_posting_id=self.kwargs["parent_lookup_job_posting__id"],
            status=job_application_status
        )

class JobInvitationViewSet(viewsets.ModelViewSet):
    serializer_class = JobInvitationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return JobInvitation.objects.filter(job_posting_id=self.kwargs["parent_lookup_job_posting__id"])


