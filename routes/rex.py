from flask import Blueprint, render_template, request, send_file
from PIL import Image
from PIL.ExifTags import TAGS
import os
import uuid

rix_bp = Blueprint("rix", __name__, url_prefix="/rex")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# قراءة EXIF
def read_exif(image_path):
    img = Image.open(image_path)
    exif = img.getexif()
    if not exif or len(exif) == 0:
        return None
    data = {}
    for tag_id, value in exif.items():
        tag = TAGS.get(tag_id, tag_id)
        data[str(tag)] = str(value)
    return data

# حذف EXIF
def remove_exif(input_path, output_path):
    img = Image.open(input_path)
    data = list(img.getdata())
    clean = Image.new(img.mode, img.size)
    clean.putdata(data)
    clean.save(output_path)

# الصفحة الرئيسية للأداة
@rix_bp.route("/", methods=["GET", "POST"])
def exif_remover():
    exif_before = exif_after = original = cleaned = None

    if request.method == "POST":
        file = request.files.get("file")
        if file:
            name = uuid.uuid4().hex + "_" + file.filename
            path = os.path.join(UPLOAD_FOLDER, name)
            file.save(path)

            exif_before = read_exif(path)

            cleaned_path = os.path.join(UPLOAD_FOLDER, "clean_" + name)
            remove_exif(path, cleaned_path)

            exif_after = read_exif(cleaned_path)

            original = name
            cleaned = "clean_" + name

    return render_template("rix_remover_card.html",
                           exif_before=exif_before,
                           exif_after=exif_after,
                           original=original,
                           cleaned=cleaned)
