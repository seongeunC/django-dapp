from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.db import models
from django.db.models import Q


class UserManager(BaseUserManager):
    def create_superuser(self, *args, **kwargs):
        return super().create_superuser(gender=self.model.GENDER_OTHER, *args, **kwargs)


class User(AbstractUser):
    GENDER_MALE = 'm'
    GENDER_FEMALE = 'f'
    GENDER_OTHER = 'o'
    NOMAL = 'n'
    COOK = 'c'
    CHOICES_GENDER = (
        (GENDER_MALE, '남성'),
        (GENDER_FEMALE, '여성'),
        (GENDER_OTHER, '기타'),
    )
    CHOICES_USER = (
        (NOMAL, '일반'),
        (COOK, '요리사'),
    )

    img_profile = models.ImageField(upload_to='user', blank=True)
    gender = models.CharField(max_length=1, choices=CHOICES_GENDER)
    wallet_address = models.CharField(max_length=40, default='')
    user_classification = models.CharField(max_length=1, choices=CHOICES_USER, default='n')
    like_posts = models.ManyToManyField('post.Post', blank=True, related_name='like_users')


    relations = models.ManyToManyField(
        'self',
        symmetrical=False,
        through='Relation'
    )

    objects = UserManager()

    def __str__(self):
        return self.username

 
