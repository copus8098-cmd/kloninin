from flask import Blueprint, render_template, request
import cv2
import os
from werkzeug.utils import secure_filename

barcode_bp = Blueprint("barcode", __name__)
UPLOAD_FOLDER = "uploads"

@barcode_bp.route("/barcode-read", methods=["GET", "POST"])
def barcode_read():
    results = []

    if request.method == "POST":
        file = request.files.get("file")
        if not file or file.filename == "":
            return render_template("barcode_read.html", error="No file selected")

        path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
        file.save(path)

        img = cv2.imread(path)
        if img is None:
            os.remove(path)
            return render_template("barcode_read.html", error="Invalid image")

        detector = cv2.QRCodeDetector()

        # محاولة قراءة (QR / Barcode محدود)
        data, bbox, _ = detector.detectAndDecode(img)

        if data:
            results.append({
                "type": "QR / Barcode",
                "data": data
            })

        os.remove(path)

        if not results:
            return render_template(
                "barcode_read.html",
                error="No barcode detected (limited OpenCV support)"
            )

    return render_template("barcode_read.html", results=results)
