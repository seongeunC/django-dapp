from django.conf import settings
from django.db import models


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='post')
    title = models.CharField(max_length=30,default='')
    ingredient = models.TextField()
    recipe_list = models.TextField()
    like = models.PositiveIntegerField(default=0)
    post_views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'Post (PK: {self.pk}, Author: {self.author.username})'

    @property
    def up_counter(self):
        self.like = self.like + 1
        self.save()

    @property
    def down_counter(self):
        self.like = self.like - 1
        self.save()

    @property
    def up_post_views(self):
        self.post_views = self.post_views + 1
        self.save()

    class Meta:
        ordering = ['-pk']


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments',on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return f'Comment (PK: {self.pk}, Author: {self.author.username})'
