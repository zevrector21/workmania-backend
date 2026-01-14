from functools import partial
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from dj_rest_auth.registration.views import RegisterView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .serializers import * 
from .permissions import CustomPermission
from core.models import User
from workmania.settings import *
from datetime import datetime


class UserViewSet(
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = UserSerializer
    filterset_fields = ('is_active',)
    ordering_fields = ('first_name')

    def get_queryset(self):
        if self.action == 'list':
            filters = Q(profile__visibility_status="public")

            search = self.request.GET.get('search')
            if search:
                for word in search.split():
                    if word.strip() == "":
                        continue
                    filters &= Q(first_name__icontains=word) | Q(last_name__icontains=word) | Q(profile__title__icontains=word)

            role = self.request.GET.get('role')
            if role:
                filters &= Q(role=role)
            
            country = self.request.GET.get('country')
            if country:
                country_q = Q()
                for skill in country.split(','):
                    country_q |= Q(profile__country__icontains=skill)
                filters &= country_q

            timezone = self.request.GET.get('timezone')
            if timezone:
                timezone_q = Q()
                for skill in timezone.split(','):
                    timezone_q |= Q(profile__timezone__icontains=skill)
                filters &= timezone_q

            skills = self.request.GET.get('skills')
            if skills:
                skill_q = Q()
                for skill in skills.split(','):
                    skill_q |= Q(profile__skills__icontains=skill)
                filters &= skill_q
            
            english_level = self.request.GET.get('english_level')
            if english_level and english_level != "any":
                filters &= Q(profile__languages__english=english_level)

            total_hours = self.request.GET.get('total_hours')
            if total_hours and total_hours != 'any':
                if total_hours == "0":
                    filters &= Q(profile__total_hours=0)
                else:
                    filters &= Q(profile__total_hours__gte=total_hours)

            total_earnings = self.request.GET.get('total_earnings')
            if total_earnings and total_earnings != 'any':
                if total_earnings == "0":
                    filters &= Q(profile__total_earnings=0)
                else:
                    filters &= Q(profile__total_earnings__gte=total_earnings)

            job_success_min = self.request.GET.get('job_success_min')
            if job_success_min:
                filters &= Q(profile__job_success__gte=job_success_min)

            job_success_max = self.request.GET.get('job_success_max')
            if job_success_max:
                filters &= Q(profile__job_success__lte=job_success_max)

            rate_min = self.request.GET.get('rate_min', None)
            if rate_min:
                filters &= Q(profile__price__gte=rate_min)

            rate_max = self.request.GET.get('rate_max', None)
            if rate_max:
                filters &= Q(profile__price__lte=rate_max)

            queryset = User.objects.filter(filters)
        else:
            queryset = User.objects.filter(pk=self.kwargs['pk'])
        return queryset

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated])
    def me(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(methods=['delete'], detail=False, permission_classes=[IsAuthenticated])
    def delete(self, request, *args, **kwargs):
        request.user.is_active = False
        request.user.save()
        # request.user.delete()

        return Response(status=200)


class CustomRegisterView(RegisterView):
    serializer_class = CustomRegisterSerializer


class ValidateCode(APIView):
    permission_classes = (AllowAny, )

    def post(self, request, format=None):
        try:
            username = request.data['username']
            code = request.data['code']
            # TODO: generate code and save
            if code == '123456':
                user = User.objects.get(username=username)
                token = Token.objects.get(user=user)
                resp = {
                    'token': token.key,
                    'id': user.id
                }
                return Response(resp)
        except Exception:
            pass

        return Response('Invalid code', status=400)


class ResetPassword(APIView):
    permission_classes = (AllowAny, )

    def post(self, request, format=None):
        try:
            uid = request.data['uid']
            password = request.data['password']
            user = User.objects.filter(id=uid).first()
            if user:
                user.set_password(password)
                user.is_reset_password = True
                user.save()
                return Response(status=201)

            else:
                return Response(status=400)
        except Exception as e:
            print("Exception: ", e)
            pass

        return Response(status=400)


class EmailVerification(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, format=None):
        return Response(status=200)
