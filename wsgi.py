"""
MediMitra WSGI Entry Point
For production WSGI servers like Gunicorn on Render.
"""

from app import create_app

app = create_app()
application = app

if __name__ == "__main__":
    app.run()
