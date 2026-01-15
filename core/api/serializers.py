from django.contrib.auth.models import Group, Permission
from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from django.db.models import Count, Window, Avg, Value
from core.models import *
from .utilities import *


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = "__all__"


class ResourceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Resource
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        kwargs["partial"] = True
        super(UserSerializer, self).__init__(*args, **kwargs)

    def update(self, user, validated_data):
        super().update(user, validated_data)

        return user
    
    def get_profile(self, obj):
        profile = Profile.objects.filter(user=obj).first()
        if profile:
            return ProfileSerializer(profile).data
        return None

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "is_active",
            "created",
            "profile",
        )


class CustomRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    role = serializers.CharField(required=False, allow_blank=True)

    def get_cleaned_data(self):
        return {
            "email": self.validated_data.get("email", ""),
            "password1": self.validated_data.get("password1", ""),
            "first_name": self.validated_data.get("first_name", ""),
            "last_name": self.validated_data.get("last_name", ""),
            "role": self.validated_data.get("role", ""),
        }

    def custom_signup(self, request, user):
        user.role = self.validated_data.get("role", "")
        user.save()
        Profile.objects.create(user=user)


class UpdateUserSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        kwargs["partial"] = True
        super(UpdateUserSerializer, self).__init__(*args, **kwargs)

    def update(self, user, validated_data):
        super().update(user, validated_data)

        return user

    class Meta:
        model = User
        fields = ("username", "first_name", "groups", "is_active")


class ProfileSerializer(serializers.ModelSerializer):
    avatar = ResourceSerializer()
    completion_percentage = serializers.ReadOnlyField()
    posted_jobs_count = serializers.ReadOnlyField()
    coins_available = serializers.ReadOnlyField()

    class Meta:
        model = Profile
        fields = "__all__"


class JobPostingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    proposal_count = serializers.ReadOnlyField()
    interview_count = serializers.ReadOnlyField()
    invite_count = serializers.ReadOnlyField()
    coin_count = serializers.ReadOnlyField()
    class Meta:
        model = JobPosting
        fields = "__all__"


class JobApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = "__all__"


class JobInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobInvitation
        fields = "__all__"


class JobOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobOffer
        fields = "__all__"


class JobMilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobMilestone
        fields = "__all__"


class JobReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobReview
        fields = "__all__"


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = "__all__"


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = "__all__"


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"
