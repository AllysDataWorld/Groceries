from utils import populate_current_food
from app import app

with app.app_context():
    populate_current_food()
