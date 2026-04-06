from app import app, db
import os


def get_host_for_external_access():
    """Get host configuration for external device access."""
    return "0.0.0.0"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    is_prod = os.getenv("FLASK_ENV") == "production"
    host = "0.0.0.0" if is_prod else "127.0.0.1"
    debug = not is_prod

    app.run(host=host, debug=debug)

    
    # Run the application
    # For local development only:
    # app.run(host=LOCAL_HOST, debug=True)
    
    # For access from other devices on network:
    # app.run(host=EXTERNAL_HOST, debug=True)
    
    # For production (disable debug):
    # app.run(host=EXTERNAL_HOST, debug=False)