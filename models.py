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
    recepitDate = db.Column(db.DateTime, default=datetime.utcnow)
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
    recepitDate = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Grocery_TEMP_Items {self.id}>'
