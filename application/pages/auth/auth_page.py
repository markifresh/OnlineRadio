from flask_login import logout_user, current_user, login_user, login_required
from flask import redirect, url_for, flash, request, render_template, Blueprint, current_app
from .auth_forms import LoginForm, SignupForm
from application.db_models.user import User
from application import login_manager

auth_page = Blueprint('auth_page', __name__, template_folder='templates', static_folder='static')


@auth_page.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('welcome_page.get_started'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query(User).filter_by(email=form.email.data).first()

        if user and user.check_password(password=form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('welcome_page.get_started'))

        flash('Invalid username/password')
        return redirect(url_for('auth_page.login'))

    return render_template('login.html', form=form)


@auth_page.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    User sign-up page.

    GET requests serve sign-up page.
    POST requests validate form & user creation.
    """
    form = SignupForm()
    if form.validate_on_submit():
        existing_user = User.query(User).filter_by(email=form.email.data).first()
        if existing_user is None:
            user = User(
                name=form.name.data,
                email=form.email.data,
                website=form.website.data
            )
            user.set_password(form.password.data)
            user.session.add(user)
            user.session.commit()  # Create new user
            login_user(user)  # Log in as newly created user
            return redirect(url_for('main_bp.dashboard'))
        flash('A user already exists with that email address.')
    return render_template(
        'signup.html',
        title='Create an Account.',
        form=form,
        template='signup-page',
        body="Sign up for a user account."
    )

@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in on every page load."""
    if user_id is not None:
        return User.query.get(user_id)
    return None


@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    flash('You must be logged in to view that page.')
    return redirect(url_for('auth_page.login'))


@auth_page.route("/logout")
@login_required
def logout():
    """User log-out logic."""
    logout_user()
    return redirect(url_for('auth_page.login'))


# 'https://hackersandslackers.com/flask-login-user-authentication/'
# 'https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login'
# 'https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins'