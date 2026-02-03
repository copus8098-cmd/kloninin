from flask import Flask, render_template
from routes.image import image_bp
from routes.pdf import pdf_bp
from routes.qr import qr_bp
from routes.misc import misc_bp
from routes.rex import rix_bp
import os

app = Flask(__name__)

# مجلد الرفع
os.makedirs("uploads", exist_ok=True)

# تسجيل الـ Blueprints
app.register_blueprint(image_bp)
app.register_blueprint(pdf_bp)
app.register_blueprint(qr_bp)
app.register_blueprint(misc_bp)
app.register_blueprint(rix_bp)

# الصفحة الرئيسية
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
