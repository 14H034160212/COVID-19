"""Application routes."""
from functools import wraps

from flask import request, render_template, redirect, url_for, session
from flask import current_app as app

from datetime import date

from application import uow
from application.forms.forms import CommentForm, RegistrationForm, LoginForm
from application.service_layer.services import add_user, NameNotUniqueException, get_articles_by_date, \
    get_first_article, get_last_article, get_article, add_comment, get_user, UnknownUserException, authenticate_user, \
    AuthenticationException, get_articles_by_id, get_article_ids_for_tag, get_tags


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view


def make_homepage():
    return render_template(
        'home.html',
        title='COVID!!!',
        basic_urls=make_basic_urls(),
        tag_urls=make_tag_urls()
    )


def make_basic_urls():
    urls = dict()
    urls['register'] = url_for('register')
    urls['login'] = url_for('login')
    urls['logout'] = url_for('logout')
    urls['articles'] = url_for('articles_by_date')
    return urls


def make_tag_urls():
    tags = get_tags(uow)
    tag_urls = dict()
    for tag in tags:
        tag_urls[tag['name']] = url_for('articles_by_tag', tag=tag['name'])
    print(tag_urls)

    return tag_urls


@app.route('/', methods=['GET'])
def home():
    return make_homepage()


@app.route('/articles_by_date', methods=['GET'])
def articles_by_date():
    # Read query parameters.
    target_date = request.args.get('date')
    article_to_show_comments = request.args.get('view_comments_for')

    # Fetch the first and last articles in the series.
    first_article = get_first_article(uow)
    last_article = get_last_article(uow)

    if target_date is None:
        # No date query parameter, so return articles from day 1 of the series.
        target_date = first_article['date']
    else:
        # Convert target_date from string to date.
        target_date = date.fromisoformat(target_date)

    if article_to_show_comments is None:
        # No view-comments query parameter, so set to a non-existent article id.
        article_to_show_comments = -1
    else:
        # Convert article_to_show_comments from string to int.
        article_to_show_comments = int(article_to_show_comments)

    # Fetch article(s) for the target date. This call also returns the previous and next dates for articles immediately
    # before and after the target date.
    articles, previous_date, next_date = get_articles_by_date(target_date, uow)

    first_article_url = None
    last_article_url = None
    next_article_url = None
    prev_article_url = None

    if len(articles) > 0:
        # There's at least one article for the target date.
        if previous_date is not None:
            # There are articles on a previous date, so generate URLs for the 'previous' and 'first' navigation buttons.
            prev_article_url = url_for('articles_by_date', date=previous_date.isoformat())
            first_article_url = url_for('articles_by_date', date=first_article['date'].isoformat())

        # There are articles on a subsequent date, so generate URLs for the 'next' and 'last' navigation buttons.
        if next_date is not None:
            next_article_url = url_for('articles_by_date', date=next_date.isoformat())
            last_article_url = url_for('articles_by_date', date=last_article['date'].isoformat())

        # Construct urls for viewing article comments and adding comments.
        for article in articles:
            article['view_comment_url'] = url_for('articles_by_date', date=target_date, view_comments_for=article['id'])
            article['add_comment_url'] = url_for('comment_on_article', article=article['id'])

        # Generate the webpage to display the articles.
        return render_template(
            'articles.html',
            title='Articles',
            articles_title=target_date.strftime('%A %B %e %Y'),
            articles=articles,
            basic_urls=make_basic_urls(),
            tag_urls=make_tag_urls(),
            first_article_url=first_article_url,
            last_article_url=last_article_url,
            prev_article_url=prev_article_url,
            next_article_url=next_article_url,
            show_comments_for_article=article_to_show_comments
        )

    # No articles to show, so return the homepage.
    return make_homepage()


@app.route('/articles_by_tag', methods=['GET'])
def articles_by_tag():
    articles_per_page = 3

    # Read query parameters.
    tag_name = request.args.get('tag')
    cursor = request.args.get('cursor')
    article_to_show_comments = request.args.get('view_comments_for')

    if article_to_show_comments is None:
        # No view-comments query parameter, so set to a non-existent article id.
        article_to_show_comments = -1
    else:
        # Convert article_to_show_comments from string to int.
        article_to_show_comments = int(article_to_show_comments)

    if cursor is None:
        # No cursor query parameter, so initialise cursor to start at the beginning.
        cursor = 0
    else:
        # Convert cursor from string to int.
        cursor = int(cursor)

    # Retrieve article ids for articles that are tagged with tag_name.
    article_ids = get_article_ids_for_tag(tag_name, uow)

    # Retrieve the batch of articles to display on the Web page.
    articles = get_articles_by_id(article_ids[cursor:cursor + articles_per_page], uow)

    first_article_url = None
    last_article_url = None
    next_article_url = None
    prev_article_url = None

    if cursor > 0:
        # There are preceding articles, so generate URLs for the 'previous' and 'first' navigation buttons.
        prev_article_url = url_for('articles_by_tag', tag=tag_name, cursor=cursor - articles_per_page)
        first_article_url = url_for('articles_by_tag', tag=tag_name)

    if cursor + articles_per_page < len(article_ids):
        # There are further articles, so generate URLs for the 'next' and 'last' navigation buttons.
        next_article_url = url_for('articles_by_tag', tag=tag_name, cursor=cursor + articles_per_page)

        last_cursor = articles_per_page * int(len(article_ids) / articles_per_page)
        if len(article_ids) % articles_per_page == 0:
            last_cursor -= articles_per_page
        last_article_url = url_for('articles_by_tag', tag=tag_name, cursor=last_cursor)

    # Construct urls for viewing article comments and adding comments.
    for article in articles:
        article['view_comment_url'] = url_for('articles_by_tag', tag=tag_name, cursor=cursor, view_comments_for=article['id'])
        article['add_comment_url'] = url_for('comment_on_article', article=article['id'])

    # Generate the webpage to display the articles.
    return render_template(
        'articles.html',
        title='Articles',
        articles_title=tag_name,
        articles=articles,
        basic_urls=make_basic_urls(),
        tag_urls=make_tag_urls(),
        first_article_url=first_article_url,
        last_article_url=last_article_url,
        prev_article_url=prev_article_url,
        next_article_url=next_article_url,
        show_comments_for_article=article_to_show_comments
    )


@app.route('/comment', methods=['GET', 'POST'])
@login_required
def comment_on_article():
    # Obtain the username of the currently logged in user.
    username = session['username']

    # Create form. The form maintains state, e.g. when this method is called with a HTTP GET request and populates
    # the form with an article id, when subsequently called with a HTTP POST request, the article id remains in the
    # form.
    form = CommentForm()

    if form.validate_on_submit():
        # Successful POST, i.e. the comment text has passed data validation.
        # Extract the article id, representing the commented article, from the form.
        article_id = int(form.article_id.data)

        # Use the service layer to store the new comment.
        add_comment(article_id, form.comment.data, username, uow)

        # Retrieve the article in dict form.
        article = get_article(article_id, uow)

        # Cause the web browser to display the page of all articles that have the same date as the commented article,
        # and display all comments, including the new comment.
        return redirect(url_for('articles_by_date', date=article['date'], view_comments_for=article_id))

    if request.method == 'GET':
        # Request is a HTTP GET to display the form.
        # Extract the article id, representing the article to comment, from a query parameter of the GET request.
        article_id = int(request.args.get('article'))

        # Store the article id in the form.
        form.article_id.data = article_id
    else:
        # Request is a HTTP POST where form validation has failed.
        # Extract the article id of the article being commented from the form.
        article_id = form.article_id.data

    # For a GET or an unsuccessful POST, retrieve the article to comment in dict form, and return a Web page that allows
    # the user to enter a comment. The generated Web page includes a form object.
    article = get_article(article_id, uow)
    return render_template(
        'comment_on_article.html',
        title='Edit article',
        article=article,
        form=form,
        handler_url=url_for('comment_on_article'),
        basic_urls=make_basic_urls(),
        tag_urls=make_tag_urls()
    )


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    username_not_unique = None

    if form.validate_on_submit():
        # Successful POST, i.e. the username and password have passed validation checking.
        # Use the service layer to attempt to add the new user.
        try:
            add_user(form.username.data, form.password.data, uow)

            # All is well, redirect the user to the login page.
            return redirect(url_for('login'))
        except NameNotUniqueException:
            username_not_unique = 'Username is already taken - please supply another'

    # print('taking action for ', request.method)
    # for field_name, error_messages in form.errors.items():
    #    for msg in error_messages:
    #        print(field_name, msg)

    # For a GET or a failed POST request, return the Registration Web page.
    return render_template(
        'credentials.html',
        title='Register',
        form=form,
        username_error_message=username_not_unique,
        handler_url=url_for('register'),
        basic_urls=make_basic_urls(),
        tag_urls=make_tag_urls()
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    username_not_recognised = None
    password_does_not_match_username = None

    if form.validate_on_submit():
        # Successful POST, i.e. the username and password have passed validation checking.
        # Use the service layer to lookup the user.
        try:
            user = get_user(form.username.data, uow)
            if user is None:
                print('use is None is login')

            # Authenticate user.
            authenticate_user(user['username'], form.password.data, uow)

            # Initialise session and redirect the user to the home page.
            session.clear()
            session['username'] = user['username']
            return redirect(url_for('home'))

        except UnknownUserException:
            # Username not known to the system, set a suitable error message.
            username_not_recognised = 'Username not recognised - please supply another.'

        except AuthenticationException:
            # Authentication failed, set a suitable error message.
            password_does_not_match_username = 'Password does not match supplied username - please check and try again.'

    # For a GET or a failed POST, return the Login Web page.
    return render_template(
        'credentials.html',
        title='Login',
        username_error_message=username_not_recognised,
        password_error_message=password_does_not_match_username,
        form=form,
        basic_urls=make_basic_urls(),
        tag_urls=make_tag_urls()
    )


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))




