from datetime import datetime
import mimetypes
from threading import Thread

import torch
from flask import Flask, render_template, send_from_directory, request, jsonify
from torchvision.transforms import ToPILImage

from ml_model import Model, process_request, unnormalize_batch, MEAN, STD

model: torch.nn.Module
is_model_loaded = False

SAVE_DEBUG_IMAGES = True


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

    image = request.json['image']
    mask = request.json['mask']
    ext = request.json['ext']

    img, msk = process_request(image, mask, ext, save_debug_images=SAVE_DEBUG_IMAGES)

    out = model.forward(img, msk)
    out = msk * unnormalize_batch(img, MEAN, STD) + (1.0 - msk) * out
    out = ToPILImage()(out.squeeze().cpu())

    if SAVE_DEBUG_IMAGES:
        out.save("_out-{}.png".format(datetime.now().strftime("%Y-%m-%d-%H-%M-%S")), ext)

    # TODO DEBUG & VALIDATE prediction
    # TODO respond/send byte to client
    # out.tobytes()

    return jsonify({})


if __name__ == '__main__':
    app.run()
