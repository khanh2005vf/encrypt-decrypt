import webbrowser
import threading
from flask import Flask, request, send_file, render_template_string, flash, redirect, url_for
from Crypto.Cipher import DES
import hashlib
import struct
import os
import io


app = Flask(__name__)
app.secret_key = 'your_secret_key'

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Mã hoá & Giải mã DES</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet" />
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css" rel="stylesheet" />
    <style>
        body {
            min-height: 100vh;
            background: url("tải\ xuống.jfif") no-repeat center center fixed;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #2c3e50;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            max-width: 600px;
        }
        .card {
            background: #ffffff;
            border-radius: 15px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
            padding: 30px 40px;
        }
        h1 {
            font-weight: 700;
            text-align: center;
            margin-bottom: 30px;
            color: #34495e;
        }
        .nav-tabs .nav-link {
            color: #34495e;
            font-weight: 600;
            border: none;
            border-radius: 8px 8px 0 0;
            background: #ecf0f1;
            transition: background 0.3s, color 0.3s;
        }
        .nav-tabs .nav-link:hover {
            background: #d1dade;
            color: #2c3e50;
        }
        .nav-tabs .nav-link.active {
            background: #2980b9;
            color: #fff;
            font-weight: 700;
            box-shadow: 0 4px 15px rgba(41, 128, 185, 0.4);
        }
        label {
            font-weight: 600;
            color: #34495e;
        }
        .form-control {
            border-radius: 10px;
            border: 1.5px solid #bdc3c7;
            padding-left: 40px;
            transition: border-color 0.3s;
        }
        .form-control:focus {
            border-color: #2980b9;
            box-shadow: 0 0 8px 0 #2980b9aa;
        }
        .input-group-text {
            background: #2980b9;
            border-radius: 10px 0 0 10px;
            border: none;
            color: #fff;
        }
        .btn-primary, .btn-success {
            border-radius: 10px;
            font-weight: 700;
            padding: 10px 25px;
            box-shadow: 0 4px 15px rgba(41, 128, 185, 0.4);
            transition: background 0.3s, box-shadow 0.3s;
        }
        .btn-primary {
            background-color: #3498db;
            border: none;
        }
        .btn-primary:hover {
            background-color: #217dbb;
            box-shadow: 0 6px 20px #217dbbaa;
        }
        .btn-success {
            background-color: #e67e22;
            border: none;
            color: #fff;
        }
        .btn-success:hover {
            background-color: #c36b17;
            box-shadow: 0 6px 20px #c36b1788;
        }
        .alert {
            border-radius: 10px;
            font-weight: 600;
        }
        .spinner-border {
            width: 1.3rem;
            height: 1.3rem;
            vertical-align: middle;
            margin-left: 8px;
            display: none;
        }
    </style>
</head>
<body>
<div class="container">
    <div class="card">
        <h1>Mã hoá & Giải mã DES</h1>
        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            {% for category, message in messages %}
              <div class="alert alert-{{category}} alert-dismissible fade show" role="alert">
                {{ message }}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
              </div>
            {% endfor %}
          {% endif %}
        {% endwith %}

        <ul class="nav nav-tabs" id="tabControl" role="tablist">
            <li class="nav-item" role="presentation">
                <button class="nav-link active" id="encrypt-tab" data-bs-toggle="tab" data-bs-target="#encrypt" type="button" role="tab" aria-controls="encrypt" aria-selected="true">Mã hoá</button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="decrypt-tab" data-bs-toggle="tab" data-bs-target="#decrypt" type="button" role="tab" aria-controls="decrypt" aria-selected="false">Giải mã</button>
            </li>
        </ul>

        <div class="tab-content mt-4" id="tabContent">
            <div class="tab-pane fade show active" id="encrypt" role="tabpanel" aria-labelledby="encrypt-tab">
                <form action="/encrypt" method="POST" enctype="multipart/form-data" onsubmit="showSpinner(this)">
                    <div class="mb-3 position-relative">
                        <label for="fileEncrypt" class="form-label">Chọn file mã hoá:</label>
                        <div class="input-group">
                            <span class="input-group-text"><i class="bi bi-file-earmark-arrow-up"></i></span>
                            <input class="form-control" type="file" id="fileEncrypt" name="file" required>
                        </div>
                    </div>
                    <div class="mb-3 position-relative">
                        <label for="passwordEncrypt" class="form-label">Mật khẩu:</label>
                        <div class="input-group">
                            <span class="input-group-text"><i class="bi bi-key-fill"></i></span>
                            <input class="form-control" type="text" id="passwordEncrypt" name="password" placeholder="Tối thiểu 8 ký tự" minlength="8" required>
                        </div>
                    </div>
                    <button class="btn btn-primary" type="submit">
                        Mã hoá & Tải về
                        <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                    </button>
                </form>
            </div>

            <div class="tab-pane fade" id="decrypt" role="tabpanel" aria-labelledby="decrypt-tab">
                <form action="/decrypt" method="POST" enctype="multipart/form-data" onsubmit="showSpinner(this)">
                    <div class="mb-3 position-relative">
                        <label for="fileDecrypt" class="form-label">Chọn file giải mã:</label>
                        <div class="input-group">
                            <span class="input-group-text"><i class="bi bi-file-earmark-arrow-down"></i></span>
                            <input class="form-control" type="file" id="fileDecrypt" name="file" required>
                        </div>
                    </div>
                    <div class="mb-3 position-relative">
                        <label for="passwordDecrypt" class="form-label">Mật khẩu:</label>
                        <div class="input-group">
                            <span class="input-group-text"><i class="bi bi-key-fill"></i></span>
                            <input class="form-control" type="text" id="passwordDecrypt" name="password" placeholder="Tối thiểu 8 ký tự" minlength="8" required>
                        </div>
                    </div>
                    <button class="btn btn-success" type="submit">
                        Giải mã & Tải về
                        <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                    </button>
                </form>
            </div>
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
<script>
function showSpinner(form) {
    const btn = form.querySelector('button[type="submit"]');
    const spinner = btn.querySelector('.spinner-border');
    spinner.style.display = 'inline-block';
    btn.setAttribute('disabled', 'disabled');
}
</script>
</body>
</html>
"""

def pad(data):
    while len(data) % 8 != 0:
        data += b' '
    return data

def get_des_key(password):
    return hashlib.sha256(password.encode()).digest()[:8]

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/encrypt', methods=['POST'])
def encrypt():
    file = request.files.get('file')
    password = request.form.get('password', '')

    if not file or not password:
        flash("Thiếu file hoặc mật khẩu.", "danger")
        return redirect(url_for('index'))

    content = file.read()
    key = get_des_key(password)
    cipher = DES.new(key, DES.MODE_ECB)
    padded_data = pad(content)
    encrypted_data = cipher.encrypt(padded_data)

    pw_hash = hashlib.sha256(password.encode()).digest()
    file_info = os.path.basename(file.filename).encode()
    file_info_len = len(file_info)

    final_data = struct.pack("B", file_info_len) + file_info + pw_hash + encrypted_data
    return send_file(io.BytesIO(final_data), download_name=file.filename + ".des", as_attachment=True)

@app.route('/decrypt', methods=['POST'])
def decrypt():
    file = request.files.get('file')
    password = request.form.get('password', '')

    if not file or not password:
        flash("Thiếu file hoặc mật khẩu.", "danger")
        return redirect(url_for('index'))

    data = file.read()
    try:
        file_info_len = data[0]
        file_info = data[1:1+file_info_len]
        pw_hash_stored = data[1+file_info_len:1+file_info_len+32]
        encrypted_data = data[1+file_info_len+32:]

        if hashlib.sha256(password.encode()).digest() != pw_hash_stored:
            flash("Sai mật khẩu!", "danger")
            return redirect(url_for('index'))

        key = get_des_key(password)
        cipher = DES.new(key, DES.MODE_ECB)
        decrypted = cipher.decrypt(encrypted_data).rstrip(b' ')
        return send_file(io.BytesIO(decrypted), download_name=file_info.decode(), as_attachment=True)
    except Exception as e:
        flash("Lỗi giải mã: " + str(e), "danger")
        return redirect(url_for('index'))

def open_browser():
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == '__main__':
    threading.Timer(1.0, open_browser).start()
    app.run(debug=False)

