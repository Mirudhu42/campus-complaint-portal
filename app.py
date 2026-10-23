import os
from datetime import datetime
from flask import Flask, render_template, session, redirect, url_for
from config import Config
from db import close_db, init_tables

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Teardown database connections
    app.teardown_appcontext(close_db)

    # Initialize tables on startup
    with app.app_context():
        try:
            init_tables()
        except Exception as e:
            app.logger.warning(f"Could not auto-initialize tables on startup: {e}")

    # Custom Jinja template filters
    @app.template_filter('format_date')
    def format_date(value, format='%d %b %Y'):
        if value is None:
            return ""
        if isinstance(value, str):
            try:
                # Handle standard ISO or MySQL datetime string formats
                cleaned = value.split('.')[0]
                dt = datetime.strptime(cleaned, '%Y-%m-%d %H:%M:%S')
                return dt.strftime(format)
            except Exception:
                try:
                    dt = datetime.strptime(value[:10], '%Y-%m-%d')
                    return dt.strftime(format)
                except Exception:
                    return value
        if hasattr(value, 'strftime'):
            return value.strftime(format)
        return str(value)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.student import student_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(admin_bp)

    # Public landing page
    @app.route('/')
    def index():
        return render_template('home.html')

    # Global context processor
    @app.context_processor
    def inject_user():
        return {
            'student_name': session.get('student_name', 'Student'),
            'student_id': session.get('student_id'),
            'admin_name': session.get('admin_name', 'Admin S'),
            'admin_id': session.get('admin_id'),
            'current_year': datetime.now().year
        }

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', error_title="Page Not Found", error_message="The requested page could not be found."), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('base.html', error_title="Access Denied", error_message="You do not have permission to access this resource."), 403

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('base.html', error_title="Server Error", error_message="An internal server error occurred."), 500

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
