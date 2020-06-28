"""Application routes."""
from flask import request, render_template, make_response, redirect, url_for
from flask import current_app as app

from application import uow
from application.service_layer.services import add_user, get_all_users, NameNotUniqueException


@app.route('/', methods=['GET'])
def user_records():
    """Create a user via query string parameters."""

    # Extract query parameters.
    username = request.args.get('user')
    email = request.args.get('email')

    if username and email:
        # Invoke the service_layer layer to attempt to add the new user.
        try:
            add_user(username, email, uow)
        except NameNotUniqueException:
            # Can't add the new user - the username is already taken.
            return make_response(f'{username} ({email}) already created!')

    # Return all users.
    redirect(url_for('user_records'))
    all_users = get_all_users(uow)

    return render_template(
        'users.jinja2',
        users=all_users,
        title="Show Users"
    )