import logging
from flask import Flask
from flask_sqlalchemy import  SqlAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os  
import redis
from prometheus_flask_exporte import PrometheusMetrics

db = SqlAlchemy()
jwt = JWTManager()
metrics = PrometheusMetrics.for_app_factory()
redis_client = None

def create_App(config_class=None):
    app = Flask(__name__)

    if config_class:
        app.config.from_object(config_class)
    else:
        from app.config import Config
        app.config.from_object(Config)
    db.init_app(app)
    jwt.init_app(app)
    metrics.init_app(app)
    CORS(app,supports_credentials=True,origins=[app.config['FRONTEND_URL']])

    if app.config.get('REDIS_URL'):
        global redis_client
        redis_client = redis.from_url(app.config['REDIS_URL'])
    from app.auth.routes import auth_bp
    from app.fileshare.routes import fileshare_bp

    app.register_blueprint(auth_bp,url_prefix='/auth')
    app.register_blueprint(fileshare_bp,url_prefix='/files')

    @app.route('/health', methods=['GET'])
    def health():return {"status":"healthy","servise":"flask-backend"}
    @jwt.user_identity_loader
    def user_identity_lookup(user):return {'user_id':user.id,'email':user.email}
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):return jwt_data['sub']

    with app.app_context():
        db.create_all()
    def setup_logging(app):
        if not app.debug:
            handler = logging.FileHandler('app.log')
            handler.setLevel(logging.INFO)
            formatter = logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            )
            handler.setFormatter(formatter)
            app.logger.addHandler(handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('App startup')
    setup_logging(app)
    return app
  