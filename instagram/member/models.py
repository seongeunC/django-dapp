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

    def follow(self, user):
        if not isinstance(user, User):
            raise ValueError('"user" argument must "User" class')

        self.follow_relations.get_or_create(to_user=user)

    def unfollow(self, user):
        if not isinstance(user, User):
            raise ValueError('"user" argument must "User" class')

        self.follow_relations.filter(to_user=user).delete()

    def is_follow(self, user):
        """해당 user를 내가 follow하고 있는지 여부"""
        return self.follow_relations.filter(to_user=user).exists()

    def is_follower(self, user):
        """해당 user가 나를 follow하고 있는지 여부"""
        return self.follower_relations.filter(from_user=user).exists()

    def is_friend(self, user):
        """서로가 follow하고 있는지"""
        return Relation.objects.filter(
            Q(from_user=self, to_user=user) & Q(to_user=self, from_user=user)).exists()

    def follow_toggle(self, user):
        relation, relation_created = self.follow_relations.get_or_create(to_user=user)
        if not relation_created:
            relation.delete()
        else:
            return relation

    @property
    def following(self):
        relations = self.follow_relations.all()
        return User.objects.filter(pk__in=relations.values('to_user'))

    @property
    def followers(self):
        relations = self.follower_relations.all()
        return User.objects.filter(pk__in=relations.values('from_user'))

    @property
    def friends(self):
        following_pk_list = self.follow_relations.values('to_user')
        followers_pk_list = self.follower_relations.filter(
            from_user__pk__in=following_pk_list).values('from_user')
        return User.objects.filter(pk__in=followers_pk_list.values('from_user'))


class Relation(models.Model):
    from_user = models.ForeignKey(User, related_name='follow_relations',on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='follower_relations',on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            ('from_user', 'to_user'),
        )

    def __str__(self):
        return f'Relation ' \
               f'from({self.from_user.username}) ' \
               f'to ({self.to_user.username})'
