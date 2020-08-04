import mimetypes
from threading import Thread

import torch
from flask import Flask, render_template, send_from_directory, jsonify

from ml_model import Model

model: torch.nn.Module
is_model_loaded = False


def get_model():
    global model, is_model_loaded

    model = Model()
    model.eval()

    is_model_loaded = True


thread = Thread(target=get_model, args=(), daemon=True)
thread.start()

app = Flask(__name__, template_folder='templates', static_url_path='')
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

mimetypes.add_type('application/javascript', '.js')


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/static/js/<path:path>')
def static_js(path):
    return send_from_directory('static/js', path)


@app.route('/upload', methods=['POST'])
def img_upload():
    if not is_model_loaded:
        return jsonify({})

    return jsonify({})


if __name__ == '__main__':
    app.run()
