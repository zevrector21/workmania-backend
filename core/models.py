from django.contrib.auth.models import Group
from django.contrib import admin
from django.db import models
from django.db.models import Avg, Count, Max
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import (PermissionsMixin, BaseUserManager)
from core.constants import ROLES
from .mixins import UUIDPrimaryKeyMixin, CreatedModifiedMixin
from dateutil.relativedelta import relativedelta

JOB_DURATION_CHOICES = (
    ('less_than_1_week', 'less than 1 week'),
    ('less_than_1_month', 'less than 1 month'),
    ('one_to_three_months', '1-3 months'),
    ('three_to_six_months', '3-6 months'),
    ('six_plus_months', '6+ months'),
)

class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("User must have an email")
        if not password:
            raise ValueError("User must have a password")

        user = self.model(
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
        
    def create_superuser(self, email, password=None):
        if not email:
            raise ValueError("User must have an email")
        if not password:
            raise ValueError("User must have a password")
 
        user = self.model(
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save(using=self._db)
        return user


class Organization(UUIDPrimaryKeyMixin, CreatedModifiedMixin):
    name = models.CharField(max_length=250, unique=True)
    logo = models.CharField(max_length=250, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    category = models.CharField(max_length=250, default="worker", null=True)

    def __str__(self):
        return self.name
    
    def get_users(self):
        return User.objects.filter(organization=self)


class Resource(UUIDPrimaryKeyMixin, CreatedModifiedMixin):
    CATEGORIES = (
        ('profile', 'PROFILE'),
        ('image', 'IMAGE'),
        ('document', 'DOCUMENT'),
        ('video', 'VIDEO'),
        ('other', 'OTHER'),
    )

    category = models.CharField(max_length=50, choices=CATEGORIES)
    name = models.CharField(max_length=200, null=True, blank=True)
    file = models.CharField(max_length=200, null=True, blank=True)
    size = models.CharField(max_length=200, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    # file = models.FileField(upload_to=resource_path)

    def __str__(self):
        return f'{self.category} - {self.file}'


class User(AbstractBaseUser, PermissionsMixin, UUIDPrimaryKeyMixin, CreatedModifiedMixin):
    is_staff = models.BooleanField(default=False)
    email = models.EmailField('email address', unique=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    role = models.CharField(max_length=255, choices=(
        ('client', 'Client'),
        ('freelancer', 'Freelancer'),
    ), default='freelancer')
    is_active = models.BooleanField(default=True)
    organization = models.ForeignKey(Organization, on_delete=models.DO_NOTHING, null=True, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    date_joined = models.DateTimeField(auto_now_add=True)
    objects = UserManager()

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def __str__(self):
        return f"{self.email} - {self.first_name} {self.last_name}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name or ''}"


class Profile(UUIDPrimaryKeyMixin, CreatedModifiedMixin):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    slug = models.SlugField(max_length=255, null=True, blank=True)
    avatar = models.ForeignKey(Resource, on_delete=models.DO_NOTHING, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    zip_code = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    website = models.URLField(max_length=255, null=True, blank=True)
    timezone = models.CharField(max_length=255, null=True, blank=True, default='utc')

    title = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    verifications = models.JSONField(null=True, blank=True)
    languages = models.JSONField(null=True, blank=True)
    educations = models.JSONField(null=True, blank=True)
    experiences = models.JSONField(null=True, blank=True)
    certifications = models.JSONField(null=True, blank=True)
    portfolios = models.JSONField(null=True, blank=True)
    categories = models.TextField(null=True, blank=True)
    skills = models.TextField(null=True, blank=True)

    job_success = models.FloatField(null=True, blank=True, default=0)
    total_earnings = models.FloatField(null=True, blank=True, default=0)
    total_jobs = models.IntegerField(null=True, blank=True, default=0)
    total_hours = models.FloatField(null=True, blank=True, default=0)
    rating = models.FloatField(null=True, blank=True)
    completion_percentage = models.FloatField(null=True, blank=True, default=0)
    hire_rate = models.FloatField(null=True, blank=True, default=0)

    working_availability = models.CharField(max_length=255, choices=(
        ('none', 'None'),
        ('more_than_30_hours_per_week', 'More than 30 hours/week'),
        ('less_than_30_hours_per_week', 'Less than 30 hours/week'),
        ('as_needed_open_to_offers', 'As needed - open to offers'),
    ), default='none')

    visibility_status = models.CharField(max_length=255, choices=(
        ('public', 'Public'),
        ('private', 'Private'),
    ), default='public')

    availability_status = models.CharField(max_length=255, choices=(
        ('available', 'Available'),
        ('not_available', 'Not Available'),
    ), default='available')

    def __str__(self):
        return f"{self.user.email} - {self.user.first_name} {self.user.last_name}"
    
    @property
    def coins_available(self):
        return 240
    
    @property
    def posted_jobs_count(self):
        return JobPosting.objects.filter(user=self.user).count()

    def calculate_profile_completion(self):
        score = 0

        if self.avatar:
            score += 10
        if self.title:
            score += 10
        if self.description:
            score += 10
        if self.skills:
            score += 15
        if self.categories:
            score += 10
        if self.country and self.city:
            score += 5
        if self.price and self.price > 0:
            score += 5
        if self.working_availability != 'none':
            score += 5
        if self.portfolios and len(self.portfolios) > 0:
            score += 10
        if self.educations and len(self.educations) > 0:
            score += 10
        if self.experiences and len(self.experiences) > 0:
            score += 10

        return min(score, 100)

    def save(self, *args, **kwargs):
        self.completion_percentage = self.calculate_profile_completion()
        super().save(*args, **kwargs)


class JobPosting(UUIDPrimaryKeyMixin, CreatedModifiedMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    skills = models.TextField(null=True, blank=True)
    categories = models.TextField(null=True, blank=True)
    compensation_type = models.CharField(max_length=255, choices=(
        ('fixed_price', 'Fixed price'),
        ('hourly', 'Hourly'),
    ), default='fixed_price', null=True, blank=True)
    working_type = models.CharField(max_length=255, choices=(
        ('part_time', 'Part Time'),
        ('full_time', 'Full Time'),
    ), default='part_time', null=True, blank=True)
    size = models.CharField(max_length=255, choices=(
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
    ), default='small', null=True, blank=True)
    duration = models.CharField(max_length=255,
        choices=JOB_DURATION_CHOICES,
        default="less_than_1_month",
        null=True, blank=True
    )
    experience_level = models.CharField(max_length=255, choices=(
        ('entry_level', 'Entry Level'),
        ('mid_level', 'Intermediate Level'),
        ('expert_level', 'Expert Level'),
    ), default="entry_level", null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    languages = models.JSONField(null=True, blank=True)
    developers_needed = models.IntegerField(null=True, blank=True, default=1)
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=255, choices=(
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('interviewing', 'Interviewing'),
        ('offered', 'Offered'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ), default='draft', null=True, blank=True)    

    def __str__(self):
        return f"{self.title} - {self.user.first_name} {self.user.last_name}"
    
    @property
    def proposal_count(self):
        return JobApplication.objects.filter(job_posting=self, status__in=['pending', 'accepted', 'rejected']).count()

    @property
    def interview_count(self):
        return JobApplication.objects.filter(job_posting=self, status='accepted').count()

    @property
    def invite_count(self):
        return JobInvitation.objects.filter(job_posting=self).count()

    @property
    def coin_count(self):
        return 2


class JobApplication(UUIDPrimaryKeyMixin, CreatedModifiedMixin):
    job_posting = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='job_applications')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cover_letter = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    duration = models.CharField(max_length=255, choices=JOB_DURATION_CHOICES, null=True, blank=True)
    status = models.CharField(max_length=255, choices=(
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled')),
        default='pending'
    )
    attachments = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.job_posting.title} - {self.user}"


class JobInvitation(UUIDPrimaryKeyMixin, CreatedModifiedMixin):
    job_posting = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='job_invitations')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=255, choices=(
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('cancelled', 'Cancelled')),
        default='pending'
    )

    def __str__(self):
        return f"{self.job_posting.title} - {self.user}"


class JobOffer(UUIDPrimaryKeyMixin, CreatedModifiedMixin):
    job_posting = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='job_offers')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=255, choices=(
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')),
        default='pending'
    )

    def __str__(self):
        return f"{self.job_posting.title} - {self.user}"


class JobMilestone(UUIDPrimaryKeyMixin, CreatedModifiedMixin):
    job_offer = models.ForeignKey(JobOffer, on_delete=models.CASCADE, related_name='job_milestones')
    slug = models.SlugField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=255, choices=(
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled')),
        default='draft'
    )
    due_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.job_offer.title} - {self.title}"


class JobReview(UUIDPrimaryKeyMixin, CreatedModifiedMixin):
    job_offer = models.ForeignKey(JobOffer, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.FloatField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)


class Notification(UUIDPrimaryKeyMixin, CreatedModifiedMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=255, choices=(
        ('read', 'Read'),
        ('unread', 'Unread')),
        default='unread'
    )


class Plan(UUIDPrimaryKeyMixin, CreatedModifiedMixin):
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)
    duration_type = models.CharField(max_length=255, choices=(
        ('months', 'Months'),
        ('years', 'Years')),
        default='months'
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Subscription(UUIDPrimaryKeyMixin, CreatedModifiedMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=255, choices=(
        ('active', 'Active'),
        ('inactive', 'Inactive')),
        default='active'
    )

    def __str__(self):
        return f"{self.user.email} - {self.plan.name}"


class Message(UUIDPrimaryKeyMixin, CreatedModifiedMixin):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipient')
    description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=255, choices=(
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled')),
        default='pending'
    )

    def __str__(self):
        return f"{self.sender.email} - {self.recipient.email}"

class SavedJob(UUIDPrimaryKeyMixin, CreatedModifiedMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_jobs')
    job_posting = models.ForeignKey(JobPosting, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} - {self.job_posting}"
