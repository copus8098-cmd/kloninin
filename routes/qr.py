from flask import Blueprint, render_template, request, send_file, jsonify
import qrcode, os, cv2
from utils.file_utils import save_file
from config import UPLOAD_FOLDER

qr_bp = Blueprint("qr", __name__, url_prefix="/qr")

@qr_bp.route("/qr-create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        data = request.form.get("data")

        if not data:
            return "لا توجد بيانات", 400

        img = qrcode.make(data)
        filename = f"qr_{os.urandom(6).hex()}.png"
        path = os.path.join(UPLOAD_FOLDER, filename)
        img.save(path)

        return send_file(path, as_attachment=True)

    return render_template("qr_create.html")


@qr_bp.route("/qr-read", methods=["GET", "POST"])

def scan():
    if request.method == "POST":
        if "file" not in request.files:
            return jsonify({"error": "لم يتم اختيار ملف"})

        file = request.files["file"]
        path = save_file(file, UPLOAD_FOLDER)

        img = cv2.imread(path)
        if img is None:
            return jsonify({"error": "صورة غير صالحة"})

        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(img)

        return jsonify({"data": data if data else "لا يوجد QR"})

    return render_template("qr_read.html")
@qr_bp.route("/preview", methods=["POST"])
def preview():
    data = request.json.get("data")
    if not data:
        return jsonify({"error": "No data"}), 400

    img = qrcode.make(data)
    preview_path = os.path.join(UPLOAD_FOLDER, "preview.png")
    img.save(preview_path)

    return jsonify({"url": "/uploads/preview.png"})
