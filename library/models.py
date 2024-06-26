"""library management model"""
from unittest.util import _MAX_LENGTH
from django.db import models
from django.contrib.auth.models import User
# Used to generate urls by reversing the URL patterns
from django.urls import reverse
from django.db.models.signals import post_save
from django.db.models.signals import pre_save, pre_delete, post_delete
from django.contrib.auth.models import PermissionsMixin
from django.utils.timezone import now
import uuid
import random
# relation containg all genre of books

from datetime import date, timedelta, datetime
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
# from package_libman import example
# from example_package_x21174041 import example


class MyAccountManager(BaseUserManager):
    """manage myaccount"""
    def create_user(self, email, name, username,enrollment_no, password=None):
        """create user"""
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            name=name,
            enrollment_no = enrollment_no,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_superuser(self, email, name, username, password, enrollment_no):
        """create superuser"""
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            username=username,
            name=name,
            enrollment_no = enrollment_no,

        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class Account(AbstractBaseUser, PermissionsMixin):
    """account details"""
    id = models.UUIDField(primary_key=True, unique=True,
                          default=uuid.uuid4, editable=False)
    # phoneNumber = models.CharField(max_length=13)
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    name = models.CharField(max_length=60, unique=False)
    username = models.CharField(max_length=30, unique=True)
    enrollment_no = models.CharField(max_length=12,
        unique=True)
    date_joined = models.DateTimeField(
        verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    pic = models.ImageField(blank=True, upload_to='students')
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'username','enrollment_no']

    objects = MyAccountManager()

    def __str__(self):
        return f'{self.name}'

    def has_perm(self, perm, obj=None):
        """For checking permissions. to keep it simple all admin have ALL permissons/"""
        return self.is_admin

    def has_module_perms(self, app_label):
        """Does this user have permission to view this app? (ALWAYS YES FOR SIMPLICITY)"""
        return True
        
    @property
    def borrowed(self):
        """query borrowed"""
        query = self.borrower_set.all().values_list('book__title', flat=True)
        return list(query)

class Genre(models.Model):
    """__str__ method is used to override default string returnd by an object"""
    name = models.CharField(
        max_length=200, help_text="Enter a book genre (e.g. Science Fiction, French Poetry etc.)")

    def __str__(self):
        return self.name

class Language(models.Model):
    """relation containing language of books"""
    name = models.CharField(max_length=200,
                            help_text="Enter the book's natural language (e.g. English, French, Japanese etc.)")

    def __str__(self):
        return self.name

class Book(models.Model):
    """create book"""
    id = models.UUIDField(primary_key=True, unique=True,
                          default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    summary = models.TextField(
        max_length=1000, help_text="Enter a brief description of the book")
    isbn = models.CharField('ISBN', max_length=13,
                            help_text='13 Character https://www.isbn-international.org/content/what-isbn')
    genre = models.ManyToManyField(
        Genre, help_text="Select a genre for this book")
    language = models.ForeignKey(
        'Language', on_delete=models.SET_NULL, null=True)
    total_copies = models.IntegerField()
    pic = models.ImageField(blank=True, null=True, upload_to='books')
    available_copies = models.IntegerField(name='available_copies')
    timesIssued = models.IntegerField(default=0)

    # __str__ method is used to override default string returnd by an object
    def __str__(self):
        return self.title

    
    @property
    def borrowers(self):
        query = self.borrower_set.all().values_list('student__id', flat=True)
        return query

class Borrower(models.Model):
    """create borrower"""
    id = models.UUIDField(primary_key=True, unique=True,
                          default=uuid.uuid4, editable=False)
    student = models.ForeignKey('Account', on_delete=models.CASCADE)
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    issue_date = models.DateField(
        null=True, blank=True, help_text='YYYY-MM-DD', default=date.today)
    return_date = models.DateField(
        null=True, blank=True, help_text='YYYY-MM-DD')

    def __str__(self):
        return self.student.name.title()+" borrowed "+self.book.title.title()

    # def fine(self):
    #     returnDate = self.return_date
    #     today = date.today()
    #     # return example.calcFine(returnDate,today)
    #     return example.calcFine(returnDate, today);
    

# def calcFine(returnDate, today):
#     fine = 0
#     if returnDate <= today:
#         fine += 5 * (today - returnDate).days
#         return fine


# def borrower_pre_delete(sender, instance, *args, **kwargs):
#     try:
#         instance.book.available_copies += 1
#         instance.book.save()
#     except:
#         raise ValueError('Error while updating')

# pre_delete.connect(borrower_pre_delete, sender=Borrower)
