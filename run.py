from dotenv import load_dotenv
load_dotenv()
from app import create_app, db
import os

app = create_app()

with app.app_context():
    db.create_all()

