from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin, BaseUserManager)


class UserManager(BaseUserManager):
    # Overriding User Model for email based authentication
    def create_user(self, email, password, **kwargs):
        if not email:
            raise ValueError("User must have an email.")

        email = self.normalize_email(email)
        user = self.model(email=email,  **kwargs)
        user.set_password(password)
        user.is_superuser = False
        user.is_staff = False
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    # Created a new User model where Username is now Email
    email = models.EmailField(max_length=255, unique=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email


class Profile(models.Model):
    prouser = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='static/images/users', null=True, blank=True)
    profileImageUrl = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.prouser.email


class AdminUserInfo(models.Model):
    admin_email = models.OneToOneField(User, on_delete=models.CASCADE)
    admin_firstname = models.CharField(max_length=200, blank=True, null=True)
    admin_lastname = models.CharField(max_length=200, blank=True, null=True)
    admin_phone = models.CharField(max_length=200, blank=True, null=True)
    admin_nid = models.CharField(max_length=200, blank=True, null=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.admin_email}=={self.admin_firstname}=={self.admin_lastname}=={self.date}"


class UserInfo(models.Model):
    user_email = models.OneToOneField(User, on_delete=models.CASCADE)
    user_firstname = models.CharField(max_length=200, blank=True, null=True)
    user_lastname = models.CharField(max_length=200, blank=True, null=True)
    user_nid = models.CharField(unique=True, max_length=200, blank=True, null=True)
    user_phone = models.CharField(max_length=200, blank=True, null=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_email}"