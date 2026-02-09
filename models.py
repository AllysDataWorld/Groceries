from datetime import datetime
from database import db

# Database Models
class Groceries(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    storeName = db.Column(db.String(200), nullable=False)
    receiptText = db.Column(db.Text, nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    children = db.relationship('Grocery_Items', order_by='Grocery_Items.id', back_populates='groceries')

class Grocery_Items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    groceries_id = db.Column(db.Integer, db.ForeignKey('groceries.id'))
    storeName = db.Column(db.String(200), nullable=False)
    storeCategory = db.Column(db.String(200), nullable=True)
    storeItem = db.Column(db.String(200), nullable=True)
    myItem = db.Column(db.String(200), nullable=True)
    myCategory = db.Column(db.String(200), nullable=True)
    price = db.Column(db.Float, nullable=True)
    filename = db.Column(db.String(200), nullable=False)
    recepitDate = db.Column(db.DateTime, nullable=False)
    groceries = db.relationship('Groceries', back_populates='children')

class Grocery_TEMP_Items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    storeName = db.Column(db.String(200), nullable=False)
    storeCategory = db.Column(db.String(200), nullable=True)
    storeItem = db.Column(db.String(200), nullable=True)
    myItem = db.Column(db.String(200), nullable=True)
    myCategory = db.Column(db.String(200), nullable=True)
    price = db.Column(db.Float, nullable=True)
    filename = db.Column(db.String(200), nullable=False)
    recepitDate = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Grocery_TEMP_Items {self.id}>'


class Smart_Shopping(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Item identification
    myItem = db.Column(db.String(200), nullable=False, unique=False, index=True)
    myCategory = db.Column(db.String(200), nullable=False)

    # Purchase pattern data
    first_purchase_date = db.Column(db.DateTime, nullable=False)
    last_purchase_date = db.Column(db.DateTime, nullable=False)
    purchase_count = db.Column(db.Integer, nullable=False, default=0)

    # Interval statistics (in days)
    average_interval = db.Column(db.Float, nullable=True)  # Average days between purchases
    std_deviation = db.Column(db.Float, nullable=True)  # Standard deviation of intervals

    # Typical purchase data
    typical_quantity = db.Column(db.Integer, nullable=False, default=1)
    typical_price = db.Column(db.Float, nullable=False)
    preferred_store = db.Column(db.String(200), nullable=False, default='Metro')

    # Metadata
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Smart_Shopping {self.myItem}>'