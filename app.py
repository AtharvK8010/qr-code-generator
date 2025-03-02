from flask import Flask, render_template, request, send_file, url_for
import qrcode
import os
import sqlite3
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder="templates", static_folder="static")

UPLOAD_FOLDER = "static/uploads"
QR_FOLDER = "saved_qr_codes"  # Change to 'saved_qr_codes' folder

# Ensure upload & QR storage folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["QR_FOLDER"] = QR_FOLDER

# Initialize SQLite database
conn = sqlite3.connect("qr_codes.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS qr_codes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        file_url TEXT,
        qr_url TEXT,
        deleted INTEGER DEFAULT 0
    )
''')
conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    data = request.form.get('data')
    file = request.files.get('file')
    qr_name = request.form.get('qr_name', 'qrcode').strip()

    if not data and not file:
        return "Error: No data or file provided!", 400

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)
        data = url_for('static', filename=f'uploads/{filename}', _external=True)

    # Generate QR Code
    qr_filename = f"{qr_name}.png"
    qr_img_path = os.path.join(QR_FOLDER, qr_filename)  # Save inside 'saved_qr_codes'
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill='black', back_color='white')
    img.save(qr_img_path)  # Save QR code in 'saved_qr_codes'

    # Save to database
    cursor.execute("INSERT INTO qr_codes (name, file_url, qr_url) VALUES (?, ?, ?)", 
                   (qr_name, data, qr_img_path))
    conn.commit()

    return send_file(qr_img_path, mimetype='image/png', as_attachment=True, download_name=qr_filename)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
    return send_file(qr_img_path, mimetype='image/png', as_attachment=True, download_name='qrcode.png')

if __name__ == '__main__':
    app.run(debug=True)
