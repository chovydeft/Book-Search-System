from exts import db

class BookModel(db.Model):
    __tablename__ = "book"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False)