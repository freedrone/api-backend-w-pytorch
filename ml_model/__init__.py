import base64
import io
from datetime import datetime

import numpy as np
import torch
from PIL import Image
from torch.autograd import Variable
from torchvision.transforms import Compose, Resize, ToTensor, Normalize, ToPILImage

from .fashion_image_inpainting import models

MEAN = np.array([0.485, 0.456, 0.406])
STD = np.array([0.229, 0.224, 0.225])


def unnormalize_batch(batch, _mean, _std, div_factor=1.0):
    """
    Unnormalize batch
    :param batch: input tensor with shape
     (batch_size, nbr_channels, height, width)
    :param div_factor: normalizing factor before data whitening
    :return: unnormalized data, tensor with shape
     (batch_size, nbr_channels, height, width)
    """
    # normalize using dataset mean and std
    mean = batch.data.new(batch.data.size())
    std = batch.data.new(batch.data.size())
    mean[:, 0, :, :] = _mean[0]
    mean[:, 1, :, :] = _mean[1]
    mean[:, 2, :, :] = _mean[2]
    std[:, 0, :, :] = _std[0]
    std[:, 1, :, :] = _std[1]
    std[:, 2, :, :] = _std[2]
    batch = torch.div(batch, div_factor)

    batch *= Variable(std)
    batch = torch.add(batch, Variable(mean))

    return batch


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
