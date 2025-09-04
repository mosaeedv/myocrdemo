from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import PdfData
from .myengine import process_pdf_from_db
from . import db
import json

views = Blueprint('views', __name__)




@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    ocr_result = None
    if request.method == 'POST':
        if 'pdf' in request.files:
            pdf_file = request.files['pdf']
            if pdf_file.filename == '':
                flash('No selected file', category='error')
            elif not pdf_file.filename.lower().endswith('.pdf'):
                flash('File is not a PDF', category='error')
            else:
                filename = pdf_file.filename
                filesize_mb = len(pdf_file.read()) / (1024 * 1024)
                pdf_file.seek(0)  # Reset file pointer
                pdf_file.save(f"website/static/uploads/{filename}")
                new_pdf = PdfData(
                    user_id=current_user.id,
                    filename=filename,
                    filesize_mb=filesize_mb
                )
                db.session.add(new_pdf)
                db.session.commit()
                flash('PDF uploaded!', category='success')
                return redirect(url_for('views.home'))
        else:
            flash('No file part', category='error')
    return render_template("home.html", user=current_user, ocr_result=ocr_result)


@views.route('/ocr/<int:pdf_id>', methods=['POST'])
@login_required
def ocr_pdf(pdf_id):
    pdf = PdfData.query.get(pdf_id)
    if not pdf or pdf.user_id != current_user.id:
        flash('PDF not found or access denied.', category='error')
        return redirect(url_for('views.home'))
    result = process_pdf_from_db(pdf_id)
    flash('OCR completed!', category='success')
    return render_template("home.html", user=current_user, ocr_result=result)



# Note deletion route removed since Note model is no longer used
