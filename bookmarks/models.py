from django.db import models
from django.contrib.auth.models import User

# Link inherits from models.Model which is the base
# class for all models.
class Link(models.Model):
    url = models.URLField(unique=True)

    def __unicode__(self):
        return self.url

class Bookmark(models.Model):
    title = models.CharField(max_length=200)
    user = models.ForeignKey(User)
    link = models.ForeignKey(Link)

    def __unicode__(self):
        return u'%s, %s' % (self.user.username, self.link.url)

class Tag(models.Model):
    name = models.CharField(max_length=64, unique=True)
    bookmarks = models.ManyToManyField(Bookmark)

    def __unicode__(self):
        return self.name

class SharedBookmark(models.Model):
    # Each bookmark can only be shared one time.
    bookmark = models.ForeignKey(Bookmark, unique=True)
    # When creating a shared bookmark, automatically set date field to current date/time.
    date = models.DateTimeField(auto_now_add=True)
    # When creating a shared bookmark, initialize its votes to 1.
    votes = models.IntegerField(default=1)
    # Each user can vote for one or more shared bookmarks and each shared bookmark
    # can be voted on by one or more users.
    users_voted = models.ManyToManyField(User)

    def __unicode__(self):
        return u'%s, %s' % (self.bookmark, self.votes)
