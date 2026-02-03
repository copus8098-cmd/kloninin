import time
from flask import Blueprint, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
import os
import json
import uuid
import pandas as pd
import patoolib
import zipfile
import tempfile
import textwrap


misc_bp = Blueprint("misc", __name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

misc_bp = Blueprint("misc", __name__)
UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ===============================
# ✏️ Text → Image
# ===============================
@misc_bp.route("/text-to-image", methods=["GET", "POST"])
def text_to_image():
    if request.method == "POST":
        text = request.form.get("text", "")
        font_size = int(request.form.get("font_size", 32))
        font_color = request.form.get("text_color", "#2c3e50")
        bg_color = request.form.get("bg_color", "#ffffff")
        image_width = int(request.form.get("image_width", 800))
        image_height = int(request.form.get("image_height", 400))
        
        # تحويل HEX إلى RGB
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        text_rgb = hex_to_rgb(font_color)
        bg_rgb = hex_to_rgb(bg_color)
        
        # إنشاء الصورة
        img = Image.new("RGB", (image_width, image_height), color=bg_rgb)
        draw = ImageDraw.Draw(img)
        
        # تحميل الخط
        font_path = "static/fonts/Amiri-Regular.ttf"  # ضع مسار الخط هنا
        if os.path.exists(font_path):
            font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.load_default()
        
        # تقسيم النص ليناسب الصورة
        max_chars = int(image_width / (font_size * 0.6))
        wrapped_text = textwrap.fill(text, width=max_chars)
        
        # حساب موضع النص للرسم (محاذاة مركزية)
        y = 10
        for line in wrapped_text.split("\n"):
            bbox = draw.textbbox((0,0), line, font=font)
            line_width = bbox[2] - bbox[0]
            x = (image_width - line_width) // 2  # center
            draw.text((x, y), line, fill=text_rgb, font=font)
            y += int(font_size * 1.5)
        
        # حفظ الصورة في uploads
        filename = f"text_image_{int(time.time())}.png"
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        img.save(image_path)

        # تمرير الصورة للنصوص HTML
        return render_template("text_to_image.html", image=filename, text=text)
    
    # في حال GET، مرر image=None لتجنب الخطأ
    return render_template("text_to_image.html", image=None)


# ===============================
# 🔀 JSON → Excel
# ===============================
@misc_bp.route("/json-to-excel", methods=["GET", "POST"])
def json_to_excel():
    if request.method == "POST":

        data = None

        # JSON File Upload
        if "file" in request.files and request.files["file"].filename != "":
            file = request.files["file"]
            path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(path)

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

        # JSON Text Input
        elif request.form.get("json_text"):
            data = json.loads(request.form["json_text"])

        if data is None:
            return render_template("json_to_excel.html", error="No JSON data provided")

        # Convert to DataFrame
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            df = pd.DataFrame([data])
        else:
            return render_template("json_to_excel.html", error="Unsupported JSON format")

        out = os.path.join(UPLOAD_FOLDER, "converted.xlsx")
        df.to_excel(out, index=False)

        return send_file(out, as_attachment=True)

    return render_template("json_to_excel.html")
# =========================
# Excel -> JSON
# =========================
@misc_bp.route("/excel-to-json", methods=["GET", "POST"])
def excel_to_json():
    if request.method == "POST":
        file = request.files.get("file")
        if not file:
            return render_template("excel_to_json.html", error="No file selected")

        # حفظ الملف
        filename = f"{uuid.uuid4().hex}_{file.filename}"
        path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(path)

        # قراءة Excel وتحويله إلى JSON
        try:
            df = pd.read_excel(path)
            json_data = df.to_json(orient="records", force_ascii=False, indent=4)

            # حفظ JSON
            json_filename = filename.rsplit(".", 1)[0] + ".json"
            json_path = os.path.join(UPLOAD_FOLDER, json_filename)
            with open(json_path, "w", encoding="utf-8") as f:
                f.write(json_data)

            return render_template(
                "excel_to_json.html",
                json_file=json_filename,
                success=True
            )
        except Exception as e:
            return render_template("excel_to_json.html", error=str(e))

    return render_template("excel_to_json.html")


# =========================
# RAR -> ZIP
# =========================
@misc_bp.route("/rar-to-zip", methods=["GET", "POST"])
def rar_to_zip():
    if request.method == "POST":
        file = request.files.get("file")
        if not file:
            return render_template("rar_to_zip.html", error="No file selected")

        # حفظ الملف
        filename = f"{uuid.uuid4().hex}_{file.filename}"
        rar_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(rar_path)

        # إنشاء مجلد مؤقت لاستخراج ملفات RAR
        temp_dir = tempfile.mkdtemp()

        try:
            # فك الضغط من RAR
            patoolib.extract_archive(rar_path, outdir=temp_dir)

            # إنشاء ملف ZIP
            zip_filename = filename.rsplit(".", 1)[0] + ".zip"
            zip_path = os.path.join(UPLOAD_FOLDER, zip_filename)
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for f in files:
                        file_path = os.path.join(root, f)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname)

            return render_template("rar_to_zip.html", success=True, zip_file=zip_filename)

        except Exception as e:
            return render_template("rar_to_zip.html", error=str(e))

    return render_template("rar_to_zip.html")
