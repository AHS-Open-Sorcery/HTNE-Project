from flask import flash, redirect, url_for, request, session
from flask_login import current_user, login_user, LoginManager, UserMixin
from flask_dance.contrib.twitter import make_twitter_blueprint
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage, OAuthConsumerMixin
from sqlalchemy.orm.exc import NoResultFound
from flask_sqlalchemy import SQLAlchemy
import data_retrieval
import urllib

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True)

class OAuth(OAuthConsumerMixin, db.Model):
    provider_user_id = db.Column(db.String(256), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    user = db.relationship(User)

login_manager = LoginManager()
login_manager.login_view = 'twitter.login'
login_manager.blueprint_login_views = 'index'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


blueprint = make_twitter_blueprint(
    storage=SQLAlchemyStorage(OAuth, db.session, user=current_user)
)

# create/login local user on successful OAuth login
@oauth_authorized.connect_via(blueprint)
def twitter_logged_in(blueprint, token):
    if not token:
        #flash("Failed to log in.", category="error")
        return False

    resp = blueprint.session.get("account/verify_credentials.json")
    if not resp.ok:
        msg = "Failed to fetch user info."
        #flash(msg, category="error")
        return False

    info = resp.json()
    user_id = info["id_str"]

    # Find this OAuth token in the database, or create it
    query = OAuth.query.filter_by(
        provider=blueprint.name,
        provider_user_id=user_id,
    )
    try:
        oauth = query.one()
    except NoResultFound:
        oauth = OAuth(
            provider=blueprint.name,
            provider_user_id=user_id,
            token=token,
        )

    if oauth.user:
        login_user(oauth.user)
        #flash("Successfully signed in.")

    else:
        # Create a new local user account for this user
        user = User(
            name=info["screen_name"],
        )
        # Associate the new local user account with the OAuth token
        oauth.user = user
        # Save and commit our database models
        db.session.add_all([user, oauth])
        db.session.commit()
        # Log in the new local user account
        login_user(user)
        #flash("Successfully signed in.")

    # Store User Email
    if(request.cookies.get('email') is not None):
        data_retrieval.set_email(current_user.get_id(), urllib.parse.unquote(request.cookies.get('email')))

    # Disable Flask-Dance's default behavior for saving the OAuth token
    return False


# notify on OAuth provider error
@oauth_error.connect_via(blueprint)
def twitter_error(blueprint, message, response):
    msg = (
        "OAuth error from {name}! "
        "message={message} response={response}"
    ).format(
        name=blueprint.name,
        message=message,
        response=response,
    )
    #flash(msg, category="error")
   

