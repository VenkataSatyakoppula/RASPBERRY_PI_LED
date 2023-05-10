from rest_framework import viewsets,status,generics,permissions
from .models import Book
from .serializers import ChangePasswordSerializer,SetNewPasswordSerializer,BookSerializer,BookSerializer1,UserRegisterSerializer,UserSerializer,ResetPasswordRequest
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.filters import SearchFilter
from django.utils.encoding import smart_str,force_str,smart_bytes, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.shortcuts import render
import jwt,os,subprocess
from django.conf import settings
from dotenv import load_dotenv
import subprocess
import threading
load_dotenv()

TIME_OUT = 5 #seconds
BOOK_NOT_EXIST = Response({"status":"Book Doesn't Exist"},status=status.HTTP_400_BAD_REQUEST)

class Booksview(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    filter_backends = [SearchFilter]
    search_fields = ['^name']
    def list(self, request):
        user = request.user
        allbooks = user.book_set.all()
        serailzer = BookSerializer1(allbooks,many=True)
        return Response(serailzer.data)

    def create(self, request):
        serailzer = BookSerializer(data=request.data,context={'request': request})
        if(serailzer.is_valid()):
            serailzer.save(created_by=request.user)
        else:
            return Response(serailzer.errors,status=status.HTTP_400_BAD_REQUEST)
        return Response(serailzer.data,status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, pk=None):
        user = request.user
        try:
            book = user.book_set.get(pk=pk)
            serailzer = BookSerializer1(book)
        except ObjectDoesNotExist:
            return BOOK_NOT_EXIST
        
        return Response(serailzer.data) 

    def update(self, request, pk=None):
        user = request.user
        try:
            book = user.book_set.get(pk=pk)
            serailzer = BookSerializer1(book, data=request.data,partial=True)
        except ObjectDoesNotExist:
            return BOOK_NOT_EXIST
        if(serailzer.is_valid()):
            serailzer.save()
        else:
            return Response(serailzer.errors,status=status.HTTP_400_BAD_REQUEST)
        return Response(serailzer.data,status=status.HTTP_200_OK)
    
    def destroy(self, request, pk=None):
        user = request.user
        try:
            book = user.book_set.get(pk=pk)
        except ObjectDoesNotExist:
            return BOOK_NOT_EXIST
        book.delete()
        return Response("Book Deleted Successfully")

class BooksFilter(generics.ListAPIView):
    serializer_class = BookSerializer1
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    filter_backends = [SearchFilter]
    search_fields = ['name','author','book_location']
    def get_queryset(self):
        user = self.request.user
        return user.book_set.all()
    

class UserRegistration(generics.CreateAPIView):
    model = get_user_model()
    permission_classes = [
        permissions.AllowAny 
    ]
    serializer_class = UserRegisterSerializer
    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

class GetUser(generics.RetrieveAPIView):
    queryset = get_user_model().objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    authentication_classes = [JWTAuthentication]
    serializer_class = UserSerializer
    lookup_field = 'pk'
    def get_object(self):
        user = self.request.user
        queryset = self.get_queryset().filter(id=user.id)
        
        obj = get_object_or_404(queryset, **self.kwargs)
        return obj

class UserDeleteView(generics.DestroyAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = [
            permissions.IsAuthenticated
    ]
    authentication_classes = [JWTAuthentication]
    lookup_field = 'pk'
    def get_object(self):
        user = self.request.user
        queryset = self.get_queryset().filter(id=user.id)
        obj = get_object_or_404(queryset, **self.kwargs)
        return obj


class UserUpdateView(generics.UpdateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]
    authentication_classes = [JWTAuthentication]
    lookup_field = 'pk'
    def get_object(self):
        user = self.request.user
        queryset = self.get_queryset().filter(id=user.id)
        obj = get_object_or_404(queryset, **self.kwargs)
        return obj


class RequestPasswordReset(generics.GenericAPIView):
    serializer_class = ResetPasswordRequest
    def post(self,request):
        serializer = self.serializer_class(data=request.data,context={'request': request})
        if(serializer.is_valid(raise_exception=True)):
            return Response({'success':"Email has been Sent successfully"})

class PasswordTokenCheckAPI(generics.GenericAPIView):
    permission_classes = [
        permissions.AllowAny 
    ]
    serializer_class = SetNewPasswordSerializer
    def get(self,request,uidb64,token):
        try:
            id= force_str(urlsafe_base64_decode(uidb64))
            user = get_user_model().objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(token=token,user=user):
                return render(request,'change_password.html',context={'error':'Token is Not valid,Request a new one.'})
            data = {'token':token,'uidb64':uidb64}
            return render(request,'change_password.html',context={'data':data})
        except DjangoUnicodeDecodeError as e:
            if not PasswordResetTokenGenerator().check_token(token=token,user=user):
                return render(request,'change_password.html',context={'error':'Token is Not valid,Request a new one.'})
    
    def patch(self,request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success':True,'message':'Password reset Success'})

class PasswordChange(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def patch(self,request):
        serializer = self.serializer_class(data=request.data,context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response({'success':"Password Changed Successfully"})

class VerifyEmail(generics.GenericAPIView):
    def get(self,request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token,settings.SECRET_KEY,algorithms=['HS256'])
            print(payload)
            user = get_user_model().objects.get(id=payload['user_id'])
            if(not (user.is_active)):
                user.is_active = True
                user.save()
            return render(request,'change_password.html',context={"activate":"Account has been Activated!"})
        except jwt.ExpiredSignatureError:
            return render(request,'change_password.html',context={"error":"Activation Link Expired"})
        except jwt.DecodeError as e:
            return render(request,'change_password.html',context={"error":"Invalid Token Request New one"})
        except Exception:
            return render(request,'change_password.html',context={"error":"Activation Link Expired"})


class LightOnThread(threading.Thread):
    def __init__(self,light_no):
        self.light_no = light_no
        threading.Thread.__init__(self)
    
    def run(self):
        pyscript = f'from LightControl import control;import time; control.turn_light_on({self.light_no})'
        proc = subprocess.Popen(['sudo','python','-c', pyscript], stdin=subprocess.PIPE)
        server_pass = bytes(os.getenv('SERVER_PASSWORD')+'\n',encoding='utf-8')
        proc.communicate(input=server_pass)

class LightOffThread(threading.Thread):
    def __init__(self,light_no):
        self.light_no = light_no
        threading.Thread.__init__(self)
    
    def run(self):
        pyscript = f'from LightControl import control;import time; control.turn_light_off({self.light_no})'
        proc = subprocess.Popen(['sudo','python','-c', pyscript], stdin=subprocess.PIPE)
        server_pass = bytes(os.getenv('SERVER_PASSWORD')+'\n',encoding='utf-8')
        proc.communicate(input=server_pass)
NUMBER_OF_LIGHTS = 30

pixels = neopixel.NeoPixel(board.D18, NUMBER_OF_LIGHTS, brightness=1)
@api_view(['GET']) #change to post later
@permission_classes([permissions.IsAuthenticated])
@authentication_classes([JWTAuthentication])
def pi_light_on(request,pk):
    user = request.user
    try:
        book = user.book_set.get(pk=pk)
    except ObjectDoesNotExist:
        return BOOK_NOT_EXIST
    light_no = int(book.book_location) - 1
    LightOnThread(light_no).start()
    #pixels[light_no] = [255,255,255]
    response = {"status":f"Light Turned on at {light_no+1}"}
    return Response(response)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@authentication_classes([JWTAuthentication])
def pi_light_off(request,pk):
    user = request.user
    try:
        book = user.book_set.get(pk=pk)
    except ObjectDoesNotExist:
        return BOOK_NOT_EXIST
    light_no = int(book.book_location) - 1
    LightOffThread(light_no).start()
    response = {"status":f"Light Turned off at {light_no+1}"}
    return Response(response)







