# Import various classes from modules
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import Context, RequestContext
from django.template.loader import get_template
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from bookmarks.forms import *
from bookmarks.models import *

# "request" is an object that contains the contents of the 
# HTTP request as a hash, E.g. request.POST contains POST data.
def main_page(request):
    # Simpler than above. Render an HttpResponse object that
    # contains the main_pate template containing...
    return render_to_response(
        'main_page.html',
        RequestContext(request)
    )


# username contains the string in the capturing parentheses
# in urls.py file
def user_page(request, username):
    ''' 
    Call the get_object... method. Pass in the User class and 
    and the username. Use them to retrieve that user's info
    from the database and create a user object.  If the user
    isn't found, generate a 404 error page.
    '''
    user = get_object_or_404(User, username=username)
    '''
    Display bookmarks associated with the given user in 
    descending (most recent first) order by id.
    '''
    bookmarks = user.bookmark_set.order_by('-id')
    try:
        # First username is the database field. Second is 
        # the actual username input argument.
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404(u'Requested user not found')

    # Obtain list of bookmarks for the given user.
    # This is explained in the "Making queries" Django doc page.
    bookmarks = user.bookmark_set.all()

    # username, bookmarks, show_tags are the context.
    variables = RequestContext(request, {
        'username': username,
        'bookmarks': bookmarks,
        'show_tags': True
    })
    # View is finished. Render the user page.
    return render_to_response('user_page.html', variables)


def tag_page(request, tag_name):

    ''' 
    Use the tag name to create a tag object. This object
    is populated from information about the tag from the database.
    '''
    tag = get_object_or_404(Tag, name=tag_name)

    # Get all bookmarks associated with the given tag in descending order.
    bookmarks = tag.bookmarks.order_by('-id')

    # Set up variables to pass to the tag_page template.
    # bookmarks, etc. comprise the context.  Context is just
    # a dictionary of values.
    variables = RequestContext(request, {
        'bookmarks': bookmarks,
        'tag_name' : tag_name,
        'show_tags': True,
        'show_user': True
    })
    # View is done. Now populate template with the contents
    # of the dictionary, i.e, the context.  It gets passed a
    # Context instance by default, not a RequestContext.
    return render_to_response('tag_page.html', variables)


def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')


def register_page(request):
    # Has user submitted the form?
    if request.method == 'POST':
        # Yes.
        # RegistrationForm was declared in forms.py
        form = RegistrationForm(request.POST)
        # Was the submitted data valid?
        if form.is_valid():
            # Yes. Create a new user in the database.
            user = User.objects.create_user(
                username = form.cleaned_data['username'],
                password = form.cleaned_data['password1'],
                email = form.cleaned_data['email']
            )
            # If everything is OK, exit the view here and
            # redirect the user to the "success" page
            return HttpResponseRedirect('/register/success/')
    else:
        # Otherwise, generate HTML for the form...
        form = RegistrationForm()

    variables = RequestContext(request, {
        'form': form
    })
    # ... and render the form
    return render_to_response(
        'registration/register.html',
        variables
    )


@login_required
def bookmark_save_page(request):

    if request.method == 'POST':  # If the form has been submitted...

        # Input data (via request.POST) is passed to a BookmarkSaveForm object
        # for validation.
        form = BookmarkSaveForm(request.POST)   # A form bound to the POSTed data.

        if form.is_valid():   # If form passes validation...

            # Create or get link object from Bookmark model.
            # See if the link is already in the database.  If it's not
            # create one and store it in the database. Return the created
            # object and a Boolean: True if it was created, False if it was
            # already in the database.
            link, dummy = Link.objects.get_or_create(
                url = form.cleaned_data['url']
            )

            # Create or get bookmark.  We don't want to add the 
            # same bookmark twice so we use get or create.
            bookmark, created = Bookmark.objects.get_or_create(
                user = request.user,
                link = link
            )

            # Update bookmark title.
            bookmark.title = form.cleaned_data['title']

            # If the bookmark is being updated, clear old tag list.
            if not created:
                bookmark.tag_set.clear()

            # Create new tag list.
            tag_names = form.cleaned_data['tags'].split()
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name = tag_name)
                bookmark.tag_set.add(tag)

            # Save bookmark to database.
            bookmark.save()

            # Redirect user to next page.
            return HttpResponseRedirect(
                '/user/%s/' % request.user.username
            )

    else:

        # Form was requested using GET.  Create a bookmark form.
        form = BookmarkSaveForm()

    # Pass the bookmark form to the template.
    variables = RequestContext(request, {
        'form': form
    })

    return render_to_response('bookmark_save.html', variables)

def tag_cloud_page(request):

    # Maximum tag weight
    MAX_WEIGHT = 5

    # Get all tags sorted by name.
    tags = Tag.objects.order_by('name')

    # Get a starting value for min and max counts by
    # counting the number of bookmarks associated with
    # the first tag in the QuerySet.
    min_count = max_count = tags[0].bookmarks.count()

    # Adjust min and max counts:
    # Get the number of bookmarks associated with each tag.
    # If that number is less than min_count, set min_count
    # to that lower number.  Also, if it's greater than
    # max_count, set max_count to that higher number.
    for tag in tags:
        # Create a temporary attribute for the count.
        tag.count = tag.bookmarks.count()
        if tag.count < min_count:
            min_count = tag.count
        if max_count < tag.count:
            max_count = tag.count

    # Calculate the count range. Avoid dividing by zero.
    range = float(max_count - min_count)
    if range == 0.0:
        range = 1.0

    # Calculate the tag weights.
    for tag in tags:
        tag.weight = int(
            MAX_WEIGHT * (tag.count - min_count) / range
        )

    variables = RequestContext(request, {
        'tags': tags 
    })
    
    return render_to_response('tag_cloud_page.html', variables)
