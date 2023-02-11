from rest_framework import serializers
from .models import Book
from .utils import Util
from rest_framework.fields import CurrentUserDefault
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str,force_str,smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

import threading

class EmailThread(threading.Thread):
    def __init__(self,email,data):
        self.email = email
        self.data = data
        threading.Thread.__init__(self)
    
    def run(self):
        self.email.send_email(self.data)


UserModel = get_user_model()

class BookSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(write_only=True,default=serializers.CurrentUserDefault())
    class Meta:
        model = Book
        fields = '__all__'

class BookSerializer1(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'
        # depth =1

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    email = serializers.EmailField()
    first_name = serializers.CharField()
    def create(self,validated_data):
        request =  self.context.get('request')
        if(validated_data['password'] == validated_data['confirm_password']):
            user = UserModel.objects.create_user(
                first_name=validated_data['first_name'],
                last_name = validated_data['last_name'],
                email = validated_data['email'],
                username=validated_data['username'],
                password=validated_data['password'],
            )
            #user is not verifed initially
            user.is_active = False
            user.save()
            token = RefreshToken.for_user(user).access_token
            current_site = get_current_site(request=request).domain
            relativeLink = reverse("booksapi:email-verify")
            url = f'http://{current_site}{relativeLink}?token={token}'
            email_body = f'Hi, {user.first_name} \n Username: {user.get_username()} \n Use the link below to activate your Account \n {url}'
            data = {'email_body':email_body,"to_email":user.email,"email_subject":"Activate Email"}
            email = Util()
            EmailThread(email=email,data=data).start()
            return user
        else:
            raise serializers.ValidationError("Passwords do not match")
    
    def validate_email(self, value):
        lower_email = value.lower()
        if UserModel.objects.filter(email__iexact=lower_email).exists():
            raise serializers.ValidationError("Email already Exists")
        return lower_email

    class Meta:
        model = UserModel
        fields = ( "id", "first_name","last_name","email","username", "password",'confirm_password', )

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ("first_name","last_name","email","username",)
    
    def validate_email(self, value):
        lower_email = value.lower()
        if UserModel.objects.filter(email__iexact=lower_email).exists():
            raise serializers.ValidationError("Email already Exists")
        return lower_email

class ResetPasswordRequest(serializers.Serializer):
    email = serializers.EmailField(min_length=3)
    action = serializers.CharField()
    class Meta:
        fields = ['email', 'action']
    
    def validate(self, attrs):
        request =  self.context.get("request")
        email = attrs.get('email')
        action = attrs.get('action')
        check = UserModel.objects.filter(email__iexact=email.lower())
        if(check.exists()):
            user = UserModel.objects.get(email=email)
            if(user.is_active and action=='reset'):
                uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
                token = PasswordResetTokenGenerator().make_token(user)
                current_site = get_current_site(request=request).domain
                relativeLink = reverse("booksapi:password-reset",kwargs={'uidb64':uidb64,'token':token})
                url = f'http://{current_site}{relativeLink}'
                email_body = f'Hi, {user.first_name} \n Username: {user.get_username()} \n Use the Link Below to reset your Password \n {url}'
                data = {'email_body':email_body,"to_email":user.email,"email_subject":"Password Reset"}
            elif(not user.is_active and action=="verify"):
                token = RefreshToken.for_user(user).access_token
                current_site = get_current_site(request=request).domain
                relativeLink = reverse("booksapi:email-verify")
                url = f'http://{current_site}{relativeLink}?token={token}'
                email_body = f'Hi, {user.first_name} \n Username: {user.get_username()} \n Use the link below to activate your Account \n {url}'
                data = {'email_body':email_body,"to_email":user.email,"email_subject":"Activate Email"}
            elif(user.is_active and action=='verify'):
                raise serializers.ValidationError("Your Email is Already Activated!")
            else:
                raise serializers.ValidationError("Your Email is Not Activated!")
            email = Util()
            EmailThread(email=email,data=data).start()
            return "Email sent success"
        else:
            raise serializers.ValidationError("This Email is Not Registered!")
            
        
class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6,max_length=68,write_only=True)
    token = serializers.CharField(min_length=1,write_only=True)
    uidb64 = serializers.CharField(min_length=1,write_only=True)
    class Meta:
        fields = ['password','token','uidb64']

    def validate(self,attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')
            id= force_str(urlsafe_base64_decode(uidb64))
            user = UserModel.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(token=token,user=user):
                raise AuthenticationFailed({'error':'Token is Not valid,Request a new one.'},401)
            
            user.set_password(password)
            user.save()
        except Exception as e:
            raise AuthenticationFailed({'error':'Token is Not valid,Request a new one.'},401)
        return super().validate(attrs)
        
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(min_length=6,max_length=68,write_only=True)
    password = serializers.CharField(min_length=6,max_length=68,write_only=True)
    class Meta:
        fields = ['password']
    
    def validate(self, attrs):
        request =  self.context.get("request")
        old_password = attrs.get('old_password')
        password = attrs.get('password')
        if request.user.check_password(old_password):
           request.user.set_password(password)
           request.user.save()
        else:
            raise AuthenticationFailed({'error':'wrong old password.'},401)   
        return super().validate(attrs)