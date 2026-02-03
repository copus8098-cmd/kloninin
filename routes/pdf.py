from flask import Blueprint, render_template, request, send_file, flash, redirect
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import os
import subprocess
from docx2pdf import convert
from docx import Document
import pdfplumber
import uuid
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm



pdf_bp = Blueprint("pdf", __name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# =========================
# Merge PDF
# =========================
@pdf_bp.route("/merge-pdf", methods=["GET", "POST"])
def merge_pdf():
    if request.method == "POST":
        files = request.files.getlist("files")
        merger = PdfMerger()
        for f in files:
            filename = f"{uuid.uuid4().hex}_{f.filename}"
            path = os.path.join(UPLOAD_FOLDER, filename)
            f.save(path)
            merger.append(path)
        out = os.path.join(UPLOAD_FOLDER, "merged.pdf")
        merger.write(out)
        merger.close()
        return send_file(out, as_attachment=True)
    return render_template("merge_pdf.html")

# =========================
# Split PDF
# =========================
@pdf_bp.route("/split-pdf", methods=["GET", "POST"])
def split_pdf():
    if request.method == "POST":
        file = request.files["file"]
        page = int(request.form["page"])
        filename = f"{uuid.uuid4().hex}_{file.filename}"
        path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(path)

        reader = PdfReader(path)
        writer = PdfWriter()
        writer.add_page(reader.pages[page-1])

        out = os.path.join(UPLOAD_FOLDER, "split.pdf")
        with open(out, "wb") as f:
            writer.write(f)

        return send_file(out, as_attachment=True)
    return render_template("split_pdf.html")

# =========================
# Compress PDF
# =========================
pdf_bp = Blueprint("pdf", __name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@pdf_bp.route("/compress-pdf", methods=["GET", "POST"])
def compress_pdf():
    if request.method == "POST":
        file = request.files.get("file")
        if not file:
            flash("No file selected!")
            return redirect(request.url)

        # حفظ الملف المرفوع
        filename = f"{uuid.uuid4().hex}_{file.filename}"
        path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(path)

        out = os.path.join(UPLOAD_FOLDER, "compressed_" + file.filename)

        # تحديد المسار الكامل للملف التنفيذي
        cpp_exe = os.path.abspath(os.path.join("cpp", "pdf_compress.exe"))

        # التحقق من وجود الملف التنفيذي
        if not os.path.isfile(cpp_exe):
            error_msg = f"C++ executable not found at {cpp_exe}. Please compile pdf_compress.cpp first."
            print(error_msg)
            return render_template("compress_pdf.html", error=error_msg)

        try:
            # استدعاء برنامج C++ لضغط PDF
            subprocess.run([cpp_exe, path, out], check=True)
        except subprocess.CalledProcessError as e:
            error_msg = f"Error while running C++ PDF compressor: {e}"
            print(error_msg)
            return render_template("compress_pdf.html", error=error_msg)

        return send_file(out, as_attachment=True)

    return render_template("compress_pdf.html")

# =========================
# Word to PDF
# =========================
@pdf_bp.route("/word-to-pdf", methods=["GET", "POST"])
def word_to_pdf():
    if request.method == "POST":
        file = request.files["file"]
        filename = f"{uuid.uuid4().hex}_{file.filename}"
        path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(path)

        out = path.replace(".docx", ".pdf")
        convert(path, out)

        return send_file(out, as_attachment=True)
    return render_template("word_to_pdf.html")

# =========================
# PDF to Word
# =========================
@pdf_bp.route("/pdf-word", methods=["GET", "POST"])
def pdf_to_word():
    if request.method == "POST":
        file = request.files["file"]
        filename = f"{uuid.uuid4().hex}_{file.filename}"
        path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(path)

        # إنشاء مستند Word جديد
        doc = Document()

        # استخراج النصوص من PDF
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    doc.add_paragraph(text)
        
        out = os.path.join(UPLOAD_FOLDER, file.filename.replace(".pdf", ".docx"))
        doc.save(out)

        return send_file(out, as_attachment=True)

    return render_template("pdf_word.html")

# =========================
# Text to PDF
# =========================
@pdf_bp.route("/text-to-pdf", methods=["GET", "POST"])
def text_to_pdf():
    if request.method == "POST":
        text = request.form.get("text", "").strip()
        font_size = int(request.form.get("font_size", 14))

        if not text:
            return render_template("text_to_pdf.html", error="No text provided")

        filename = f"text_{uuid.uuid4().hex}.pdf"
        out = os.path.join(UPLOAD_FOLDER, filename)

        c = canvas.Canvas(out, pagesize=A4)
        width, height = A4

        c.setFont("Helvetica", font_size)

        x = 2 * cm
        y = height - 2 * cm
        max_width = width - 4 * cm

        # تقسيم النص إلى أسطر
        for line in text.split("\n"):
            if y < 2 * cm:
                c.showPage()
                c.setFont("Helvetica", font_size)
                y = height - 2 * cm

            c.drawString(x, y, line)
            y -= font_size + 4

        c.save()

        return send_file(out, as_attachment=True)

    return render_template("text_to_pdf.html")
