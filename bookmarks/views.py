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
import pdb
from datetime import datetime, timedelta
from django.db.models import Q
from django.core.paginator import Paginator, InvalidPage

ITEMS_PER_PAGE = 4


# "request" is an object that contains the contents of the 
# HTTP request as a hash, E.g. request.POST contains POST data.
def main_page(request):
    shared_bookmarks = SharedBookmark.objects.order_by(
        '-date'
    )[:10]  # Limit the list to the first 10 results.

    variables = RequestContext(request, {
        'shared_bookmarks': shared_bookmarks
    })

    return render_to_response('main_page.html', variables)


# Test page
def test_page(request):
    return render_to_response(
        'test_page.html',
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
    query_set = user.bookmark_set.order_by('-id')
    paginator = Paginator(query_set, ITEMS_PER_PAGE)

    try:
        page_number = int(request.GET['page'])  # GET should contain a 'page' variable...
    except (KeyError, ValueError):  # If it doesn't, assume we want the first page.
        page_number = 1

    try:
        page = paginator.page(page_number)  # Get the current page.
    except InvalidPage:
        raise Http404

    bookmarks = page.object_list  # Retrieve the bookmarks for the current page.

    # username, bookmarks, show_tags are the context.
    variables = RequestContext(request, {
        'bookmarks': bookmarks,
        'username': username,
        'show_tags': True,
        # If the user is viewing their own page, display the 'edit'
        # link next to each bookmark.
        'show_edit': username == request.user.username,
        'show_paginator': paginator.num_pages > 1,  # If more than one page, show paginator.
        'has_prev': page.has_previous(),            # If there's a previous page, show link to it.
        'has_next': page.has_next(),                # If there's a next page, show link to it.
        'page': page_number,                        # Index of current page
        'pages': paginator.num_pages,               # Total number of pages
        'next_page': page_number + 1,               # Index of next page
        'prev_page': page_number - 1                # Index of previous page
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

    # Boolean. True if 'ajax' in GET string.
    ajax = 'ajax' in request.GET

    if request.method == 'POST':  # If the form has been submitted...

        # Input data (via request.POST) is passed to a BookmarkSaveForm object
        # for validation.
        form = BookmarkSaveForm(request.POST)   # A form bound to the POSTed data.

        if form.is_valid():   # If form passes validation...

            bookmark = _bookmark_save(request, form)

            if ajax:  # If this is an Ajax request...
                variables = RequestContext(request, {
                    'bookmarks': [bookmark],
                    'show_edit': True,
                    'show_tags': True
                })
                return render_to_response(
                    'bookmark_list.html', variables
                )
            else:  # Otherwise, this is a normal form submission.
                return HttpResponseRedirect(
                    '/user/%s/' % request.user.username

                )
        else:  # If form didn't validate...
            if ajax:  #... and it's an Ajax request...
                return HttpResponse(u'failure')  # We'll display a JavaScript error dialog box.
            # Otherwise the form will be reloaded and display the errors for the user to correct.

    elif 'url' in request.GET:  # If 'url' in GET string...

        url = request.GET['url']
        title = ''
        tags = ''

        try:
            # Get the link and bookmark objects that correspond
            # to this URL and user.
            link = Link.objects.get(url = url)
            bookmark = Bookmark.objects.get(
                link = link,
                user = request.user
            )
            title = bookmark.title
            
            # Concatenate the names of all tags associated 
            # with given bookmark.
            tags = ' '.join(
                tag.name for tag in bookmark.tag_set.all()
            )
        except (Link.DoesNotExist, Bookmark.DoesNotExist):
            # This is a null operation.  Essentially, if we
            # can't find either the URL or its associated
            # bookmark, we'll only populate the URL field below,
            # leaving the title and tags fields blank.
            pass

        # Bind the data to the BookmarkSaveForm.
        form = BookmarkSaveForm({
            'url'  : url,
            'title': title,
            'tags' : tags
        })

    else:

        # Form was requested using GET.  Create a bookmark form.
        form = BookmarkSaveForm()

    # Pass the bookmark form to the template.
    variables = RequestContext(request, {
        'form': form
    })

    # If we get to here, there was no POST data.  Just render form and return it.
    if ajax:
        return render_to_response(
            'bookmark_save_form.html',
            variables
        )
    else:
        return render_to_response(
            'bookmark_save.html', 
            variables
        )


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


def search_page(request):

    form = SearchForm()  # Generate the search form.
    bookmarks = []       # Holds bookmarks to display in search results.
    show_results = False # If False, there was no query so don't display _anything_.
                         # If True, there was a query so either display results or
                         # or "No bookmarks found".

    if 'query' in request.GET:  # If a query was sent...
        show_results = True     # ... show search results.
        query = request.GET['query'].strip()  # Strip non-white space chars from query string.

        if query:
            keywords = query.split()
            
            q = Q()
            for keyword in keywords:
                q = q & Q(title__icontains=keyword)

            form = SearchForm({ 'query': query })  # Bind the form to the query (huh?).
            bookmarks = Bookmark.objects.filter(q)[:10]

    variables = RequestContext(request, {  # Pass everything to template for rendering.
        'form': form,
        'bookmarks': bookmarks,
        'show_results': show_results,
        'show_tags': True,
        'show_user': True
    })

    if request.GET.has_key('ajax'):
        return render_to_response('bookmark_list.html', variables)
    else:
        return render_to_response('search.html', variables)


def _bookmark_save(request, form):

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

    # Share bookmark on main page if requested.
    if form.cleaned_data['share']:
        shared, created = SharedBookmark.objects.get_or_create(
            bookmark = bookmark
        )
        if created:
            # If the shared bookmark object was created, add the current user
            # to the list of users for voted for the bookmark.
            shared.users_voted.add(request.user)
            shared.save()

    # Save bookmark to database.
    bookmark.save()

    return bookmark


@login_required
def bookmark_vote_page(request):

    if 'id' in request.GET:
        try:
            id = request.GET['id']
            shared_bookmark = SharedBookmark.objects.get(id = id)
            user_voted = shared_bookmark.users_voted.filter(username = request.user.username)
            if not user_voted:
                shared_bookmark.votes += 1
                shared_bookmark.users_voted.add(request.user)
                shared_bookmark.save()
        except SharedBookmark.DoesNotExist:
            raise Http404('Bookmark not found.')

    if 'HTTP_REFERER' in request.META:
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

    return HttpResponseRedirect('/')


def popular_page(request):
    
    today = datetime.today()
    yesterday = today - timedelta(1)
    shared_bookmarks = SharedBookmark.objects.filter(
        date__gt=yesterday
    )
    shared_bookmarks = shared_bookmarks.order_by(
        '-votes'
    )[:10]

    variables = RequestContext(request, {
        'shared_bookmarks': shared_bookmarks
    })
    return render_to_response('popular_page.html', variables)


def bookmark_page(request, bookmark_id):

    shared_bookmark = get_object_or_404(
        SharedBookmark,
        id=bookmark_id
    )

    variables = RequestContext(request, {
        'shared_bookmark': shared_bookmark
    })
    return render_to_response('bookmark_page.html', variables)

