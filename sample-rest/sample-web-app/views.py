from django.shortcuts import render
#from django import HttpResponse
from django.shortcuts import get_object_or_404 # when object doesn't have the object
from rest_framework.views import APIView #Normal views can be used to return the API data
from rest_framework import status   #status of the data
from .models import employee
from rest_framework.response import Response #we can get response from the given
from .serializer import employeeserializer


class employeelist(APIView):


    def get(self,request):
        employee1 = employee.objects.all()
        serializer = employeeserializer(employee1, many= True)
        return Response(serializer.data)


    def post(self):
        pass
