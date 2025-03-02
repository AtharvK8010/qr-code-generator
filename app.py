from flask import Flask, render_template, request, send_file, url_for
import qrcode
import os
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder="templates", static_folder="static")

UPLOAD_FOLDER = "static/uploads"
QR_FOLDER = "saved_qr_codes"

# Ensure upload & QR storage folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["QR_FOLDER"] = QR_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    data = request.form.get('data')
    file = request.files.get('file')
    qr_name = request.form.get('qr_name', '').strip()  # Get QR name input

    if not data and not file:
        return "Error: No data or file provided!", 400

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)
        data = url_for('static', filename=f'uploads/{filename}', _external=True)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # If no name is provided, use 'generated_qr' with timestamp
    if not qr_name:
        qr_name = f"generated_qr_{int(os.time.time())}"

    qr_file_name = f"{qr_name}.png"  # Corrected variable name
    qr_path_name = os.path.join(QR_FOLDER, qr_file_name)  # Corrected variable name

    img = qr.make_image(fill='black', back_color='white')
    img.save(qr_path_name)

    return send_file(qr_path_name, mimetype='image/png', as_attachment=True, download_name=qr_file_name)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))  # Use PORT from environment variable
    app.run(debug=True, host="0.0.0.0", port=port)
