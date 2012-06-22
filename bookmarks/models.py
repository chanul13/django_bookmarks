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

class Friendship(models.Model):
    # Since this class has two FKs that point to the same class, we have
    # to specify a 'related_name' attribute to differentiate them.
    # 'friend_set' contains the friends of a user.
    # 'to_friend_set' contains the users who added this user as a friend.
    #
    # 'from_friend' is the person who initiates the friendship.
    # 'to_friend' is the recipent of from_friend's friendship.  They're
    # the person 'from_friend' is friends with.
    from_friend = models.ForeignKey(User, related_name = 'friend_set')
    to_friend = models.ForeignKey(User, related_name = 'to_friend_set')

    def __unicode__(self):
        return u'%s, %s' % (
            self.from_friend.username,
            self.to_friend.username
        )

    # Options related to this class
    class Meta:
        # No more than one to_friend/from_friend tuple can exist in the database.
        # In other words, any particular friendship can only be added to the 
        # database one time.
        unique_together = (('to_friend', 'from_friend'), )
