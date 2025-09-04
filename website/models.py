from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func



# PDF Data Model
from datetime import datetime
class PdfData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    filename = db.Column(db.String(256), nullable=False)
    filesize_mb = db.Column(db.Float, nullable=False)
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    ocr_text = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<PdfData {self.filename} ({self.filesize_mb}MB)>"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    pdfs = db.relationship('PdfData')
