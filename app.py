import os
from datetime import datetime

from authlib.integrations.flask_client import OAuth
from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from dotenv import load_dotenv


load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
oauth = OAuth()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///portfolio.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)
    oauth.init_app(app)
    login_manager.login_view = "index"

    _configure_oauth(app)

    with app.app_context():
        db.create_all()
        seed_projects()

    register_routes(app)
    return app


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(50), nullable=False)
    provider_id = db.Column(db.String(200), unique=True, nullable=False)
    name = db.Column(db.String(200))
    avatar = db.Column(db.String(500))
    email = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User")


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    repo_url = db.Column(db.String(500), nullable=False)


def seed_projects():
    """Populate sample projects once."""
    if db.session.scalar(func.count(Project.id)) > 0:
        return
    samples = [
        Project(
            name="Miminet Packet Filters",
            description="Network animation filters for Miminet platform.",
            repo_url="https://github.com/mimi-net/miminet/pull/349",
        ),
        Project(
            name="Graphs-Graphs",
            description="Desktop app for graph analysis.",
            repo_url="https://github.com/spbu-coding-2024/graphs-graphs-team-6",
        ),
        Project(
            name="LES",
            description="Library that provides Binary search, AVL and Red-black trees for Kotlin.",
            repo_url="https://github.com/spbu-coding-2024/trees-trees-team-4",
        ),
    ]
    db.session.add_all(samples)
    db.session.commit()


def _configure_oauth(app: Flask):
    oauth.register(
        name="github",
        client_id=os.getenv("GITHUB_CLIENT_ID"),
        client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
        access_token_url="https://github.com/login/oauth/access_token",
        authorize_url="https://github.com/login/oauth/authorize",
        api_base_url="https://api.github.com/",
        client_kwargs={"scope": "read:user user:email"},
    )
    oauth.register(
        name="yandex",
        client_id=os.getenv("YANDEX_CLIENT_ID"),
        client_secret=os.getenv("YANDEX_CLIENT_SECRET"),
        access_token_url="https://oauth.yandex.ru/token",
        authorize_url="https://oauth.yandex.ru/authorize",
        api_base_url="https://login.yandex.ru/",
        client_kwargs={"scope": "login:email login:info", "force_confirm": "yes"},
    )


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def register_routes(app: Flask):
    @app.route("/")
    def index():
        projects = Project.query.all()
        comments = Comment.query.order_by(Comment.created_at.desc()).limit(10).all()
        return render_template(
            "index.html",
            projects=projects,
            comments=comments,
            yandex_id=os.getenv("YANDEX_METRIKA_ID"),
            gtm_id=os.getenv("GTM_ID"),
            title="Portfolio — Roman Kormilcyn",
        )

    @app.route("/login/<provider>")
    def login(provider):
        client = oauth.create_client(provider)
        if not client:
            return "Unknown provider", 404
        redirect_uri = url_for("auth_callback", provider=provider, _external=True)
        return client.authorize_redirect(redirect_uri)

    @app.route("/auth/<provider>/callback")
    def auth_callback(provider):
        client = oauth.create_client(provider)
        if not client:
            return "Unknown provider", 404

        token = client.authorize_access_token()
        if provider == "github":
            resp = client.get("user", token=token)
            profile = resp.json()
            provider_id = str(profile.get("id"))
            name = profile.get("name") or profile.get("login")
            avatar = profile.get("avatar_url")
            email = profile.get("email")
        elif provider == "yandex":
            resp = client.get("info", params={"format": "json"}, token=token)
            profile = resp.json()
            provider_id = profile.get("id")
            name = profile.get("real_name") or profile.get("display_name") or profile.get("login")
            avatar_id = profile.get("default_avatar_id")
            avatar = (
                f"https://avatars.yandex.net/get-yapic/{avatar_id}/islands-200"
                if avatar_id
                else None
            )
            email = profile.get("default_email")
        else:
            return "Unsupported provider", 400

        user = User.query.filter_by(provider=provider, provider_id=provider_id).first()
        if not user:
            user = User(
                provider=provider,
                provider_id=provider_id,
                name=name,
                avatar=avatar,
                email=email,
            )
            db.session.add(user)
            db.session.commit()
        else:
            user.name = name
            user.avatar = avatar
            user.email = email
            db.session.commit()

        login_user(user)
        return redirect(url_for("index"))

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("index"))

    @app.route("/comments", methods=["GET"])
    def get_comments():
        comments = Comment.query.order_by(Comment.created_at.desc()).limit(20).all()
        return jsonify(
            [
                {
                    "id": c.id,
                    "body": c.body,
                    "author": c.user.name or "Anonymous",
                    "created_at": c.created_at.isoformat(),
                    "avatar": c.user.avatar,
                }
                for c in comments
            ]
        )

    @app.route("/comments", methods=["POST"])
    @login_required
    def post_comment():
        payload = request.get_json(silent=True) or {}
        body = (payload.get("body") or "").strip()
        if not body:
            return jsonify({"error": "Comment is empty"}), 400

        comment = Comment(body=body, user=current_user)
        db.session.add(comment)
        db.session.commit()
        return jsonify(
            {
                "id": comment.id,
                "body": comment.body,
                "author": current_user.name or "Anonymous",
                "created_at": comment.created_at.isoformat(),
                "avatar": current_user.avatar,
            }
        ), 201


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
