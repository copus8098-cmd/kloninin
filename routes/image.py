from flask import Blueprint, render_template, request, send_file
from PIL import Image
import os
import cv2
import numpy as np

image_bp = Blueprint("image", __name__)
UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ===============================
# 📷 Image → PDF
# ===============================


PAGE_SIZES = {
    "A4": (595, 842),      # points (1pt = 1/72 inch)
    "A5": (420, 595),
    "Letter": (612, 792),
}

@image_bp.route("/image-to-pdf", methods=["GET", "POST"])
def image_to_pdf():
    if request.method == "POST":
        if "file" not in request.files:
            return render_template("image_to_pdf.html", error="No file selected")

        file = request.files["file"]
        if file.filename == "":
            return render_template("image_to_pdf.html", error="No file selected")

        # حفظ الصورة
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        # فتح الصورة
        img = Image.open(path).convert("RGB")

        # ======= خيارات القص =======
        try:
            left = int(request.form.get("crop_left", 0))
            top = int(request.form.get("crop_top", 0))
            right = int(request.form.get("crop_right", img.width))
            bottom = int(request.form.get("crop_bottom", img.height))
            img = img.crop((left, top, right, bottom))
        except:
            pass  # إذا لم تُدخل القيم، لا يتم القص

        # ======= اختيار نوع الصفحة =======
        page_type = request.form.get("page_size", "A4")
        pdf_width, pdf_height = PAGE_SIZES.get(page_type, PAGE_SIZES["A4"])

        # تكبير/تصغير الصورة لتناسب الصفحة
        img = img.resize((pdf_width, pdf_height))

        # حفظ PDF
        pdf_path = path.rsplit(".", 1)[0] + ".pdf"
        img.save(pdf_path, "PDF")

        return send_file(pdf_path, as_attachment=True)

    return render_template("image_to_pdf.html")


# ===============================
# 🎨 Image Format Convert
# ===============================
@image_bp.route("/image-convert", methods=["GET", "POST"])
def image_convert():
    if request.method == "POST":
        file = request.files["file"]
        fmt = request.form.get("format", "png")

        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        img = Image.open(path)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        out = path.rsplit(".", 1)[0] + "." + fmt
        img.save(out)

        return send_file(out, as_attachment=True)

    return render_template("image_convert.html")


# ===============================
# 📐 Resize Image
# ===============================
@image_bp.route("/resize-image", methods=["GET", "POST"])
def resize_image():
    if request.method == "POST":
        file = request.files["file"]
        width = int(request.form["width"])
        height = int(request.form["height"])

        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        img = Image.open(path)
        resized = img.resize((width, height))

        out = os.path.join(UPLOAD_FOLDER, f"resized_{file.filename}")
        resized.save(out)

        return send_file(out, as_attachment=True)

    return render_template("resize_image.html")


# ===============================
# 🎭 Remove Background (Simple)
# ===============================
@image_bp.route("/remove-bg", methods=["GET", "POST"])
def remove_bg():
    if request.method == "POST":
        file = request.files["file"]
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        img = cv2.imread(path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

        result = cv2.bitwise_and(img, img, mask=mask)

        out = os.path.join(UPLOAD_FOLDER, "no_bg_" + file.filename)
        cv2.imwrite(out, result)

        return send_file(out, as_attachment=True)

    return render_template("remove_bg.html")
# ===============================
# 🖤 Convert to Grayscale
# ===============================
@image_bp.route("/grayscale", methods=["GET", "POST"])
def grayscale_image():
    if request.method == "POST":
        file = request.files["file"]
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        img = Image.open(path).convert("L")
        out = os.path.join(UPLOAD_FOLDER, "gray_" + file.filename)
        img.save(out)

        return send_file(out, as_attachment=True)

    return render_template("grayscale.html")


# ===============================
# 🔄 Rotate Image
# ===============================
@image_bp.route("/rotate-image", methods=["GET", "POST"])
def rotate_image():
    if request.method == "POST":
        file = request.files["file"]
        angle = int(request.form.get("angle", 90))

        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        img = Image.open(path)
        rotated = img.rotate(-angle, expand=True)

        out = os.path.join(UPLOAD_FOLDER, "rotated_" + file.filename)
        rotated.save(out)

        return send_file(out, as_attachment=True)

    return render_template("rotate_image.html")


# ===============================
# ✂️ Crop Image
# ===============================
@image_bp.route("/crop-image", methods=["GET", "POST"])
def crop_image():
    if request.method == "POST":
        file = request.files["file"]
        x = int(request.form["x"])
        y = int(request.form["y"])
        w = int(request.form["width"])
        h = int(request.form["height"])

        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        img = Image.open(path)
        cropped = img.crop((x, y, x + w, y + h))

        out = os.path.join(UPLOAD_FOLDER, "cropped_" + file.filename)
        cropped.save(out)

        return send_file(out, as_attachment=True)

    return render_template("crop_image.html")


# ===============================
# ✨ Sharpen Image
# ===============================
from PIL import ImageFilter

@image_bp.route("/sharpen-image", methods=["GET", "POST"])
def sharpen_image():
    if request.method == "POST":
        file = request.files["file"]
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        img = Image.open(path)
        sharp = img.filter(ImageFilter.SHARPEN)

        out = os.path.join(UPLOAD_FOLDER, "sharp_" + file.filename)
        sharp.save(out)

        return send_file(out, as_attachment=True)

    return render_template("sharpen_image.html")


# ===============================
# 📉 Compress Image
# ===============================
@image_bp.route("/compress-image", methods=["GET", "POST"])
def compress_image():
    if request.method == "POST":
        file = request.files["file"]
        quality = int(request.form.get("quality", 50))

        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        img = Image.open(path).convert("RGB")
        out = os.path.join(UPLOAD_FOLDER, "compressed_" + file.filename)

        img.save(out, optimize=True, quality=quality)

        return send_file(out, as_attachment=True)

    return render_template("compress_image.html")
