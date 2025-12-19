# run.py
import os
import sys
from app import create_app
from app.config import Config

def main():
    """
    Main entry point for the Flask application
    """
    try:
        # Create Flask application instance
        app = create_app(Config)
        
        # Get port from environment or use default
        port = int(os.environ.get('PORT', 5000))
        host = os.environ.get('HOST', '0.0.0.0')
        
        # Determine if running in development or production
        debug = os.environ.get('FLASK_ENV') == 'development'
        
        print("=" * 50)
        print("🚀 Flask Backend Application")
        print("=" * 50)
        print(f"Environment: {os.environ.get('FLASK_ENV', 'production')}")
        print(f"Debug Mode: {debug}")
        print(f"Database: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')}")
        print(f"Listening on: http://{host}:{port}")
        print("=" * 50)
        
        # Run the application
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=debug
        )
        
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()