import base64
import io
import os
import sys
from datetime import datetime

import numpy as np
import torch
from PIL import Image
from torchvision.transforms import Compose, Resize, ToTensor, Normalize

# FASHION IMAGE INPAINTING CONFIGURATION
# BEGIN :::
# HACK insert fashion_image_inpainting repo to root
__fashion_image_inpainting_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fashion_image_inpainting")
if os.path.exists(__fashion_image_inpainting_path):
    sys.path.insert(0, __fashion_image_inpainting_path)

from .fashion_image_inpainting.utils import unnormalize_batch
from .fashion_image_inpainting import models
# END :::::

MEAN = np.array([0.485, 0.456, 0.406])
STD = np.array([0.229, 0.224, 0.225])


def transform_image(image_bytes: bytes, mask_bytes: bytes):
    img_transforms = Compose([Resize(256), ToTensor(), Normalize(MEAN, STD)])
    mask_transforms = Compose([Resize(256), ToTensor()])
    image = Image.open(io.BytesIO(image_bytes))
    mask = Image.open(io.BytesIO(mask_bytes))

    return img_transforms(image).unsqueeze(0), mask_transforms(mask).unsqueeze(0)


def process_request(image, mask, ext, save_debug_images=False):
    _t = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    img_64_enc = image.split(',')[1]
    img_64_dec = base64.b64decode(img_64_enc)

    msk_64_enc = mask.split(',')[1]
    msk_64_dec = base64.b64decode(msk_64_enc)

    img, msk = transform_image(img_64_dec, msk_64_dec)

    if save_debug_images:
        img.save("_img-{}.png".format(_t), ext)
        msk.save("_msk-{}.png".format(_t), ext)

    img = torch.stack([img]).float()
    msk = torch.stack([msk]).float()

    return img, msk


Model: torch.nn.Module = models.Net
