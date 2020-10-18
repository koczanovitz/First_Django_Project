from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin)

from django.db import models
from django.db.models.constraints import UniqueConstraint
from django.urls import reverse


class UserManager(BaseUserManager):
    def create_user(self, email, firstname, lastname, password=None):
        user = self.model(
            email=self.normalize_email(email),
            firstname=firstname,
            lastname=lastname,
            is_superuser=False,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, firstname, lastname, password=None):
        user = self.model(
            email=self.normalize_email(email),
            firstname=firstname,
            lastname=lastname,
            is_superuser=True,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    USERNAME_FIELD = 'email'
    # EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = [
        # 'email',
        'firstname',
        'lastname',
    ]

    email = models.EmailField(unique=True)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)

    profile_photo = models.ImageField(upload_to="profile_photos/", blank=True)
    description = models.TextField(blank=True)
    website = models.URLField(default='', blank=True)
    following = models.ManyToManyField(
        "self", symmetrical=False, related_name="followers", blank=True)

    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    @property
    def is_staff(self):
        return self.is_superuser

    def get_short_name(self):
        return self.firstname

    def get_full_name(self):
        return f'{self.firstname} {self.lastname}'

    def __str__(self):
        return self.get_full_name()

    def get_absolute_url(self):
        return reverse("photos:user", args=[self.pk])


class Post(models.Model):
    # """Użytkownik data aopis zdjęcie"""
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    content = models.CharField(max_length=400)
    created_timestamp = models.DateTimeField(auto_now_add=True)
    last_modified_timestamp = models.DateTimeField(auto_now=True, null=True)
    image = models.ImageField(
        upload_to="posts/", width_field='image_width', height_field='image_height')
    image_width = models.PositiveIntegerField(default=0)
    image_height = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_timestamp"]

    def __str__(self):
        return f"Post by {self.user}: {self.content[:50]}..."

    def get_absolute_url(self):
        return reverse("photos:post", args={self.pk})


class Comment(models.Model):
    # autor wpis data i czas tresc
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_timestamp = models.DateTimeField(auto_now_add=True)
    last_modified_timestamp = models.DateTimeField(auto_now=True, null=True)
    content = models.CharField(max_length=200)

    class Meta:
        ordering = ["-created_timestamp"]

    def __str__(self):
        return f"Comment by {self.user}: {self.content[:50]}..."


class LikeManager(models.Manager):
    def like_only(self):
        return self.get_queryset().filter(like=True)

    def dislike_only(self):
        return self.get_queryset().filter(like=False)


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_timestamp = models.DateTimeField(auto_now_add=True)
    last_modified_timestamp = models.DateTimeField(auto_now=True, null=True)
    like = models.BooleanField(default=True)

    objects = LikeManager()

    def __str__(self):
        return f"Like {self.like} by {self.user} on {self.post}"

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["user", "post"], name="unique_like_for_user_and_post"
            )
        ]
