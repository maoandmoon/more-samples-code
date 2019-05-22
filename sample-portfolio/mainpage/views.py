from rest_framework import generics
from .models import *
from .serializers import *


class RetrivePersonalInfo(generics.RetrieveAPIView):
    queryset = PersonalInfo.objects.all()
    serializer_class = PersonalInfoSerializer


class ListSkills(generics.ListAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer


class ListPartners(generics.ListAPIView):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer


class ListProjects(generics.ListAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class CreateMessage(generics.CreateAPIView):
    serializer_class = MessageSerializer
