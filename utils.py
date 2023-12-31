from x2paddle import torch2paddle
import paddle
import numpy as np


def convert_rgb_to_y(img):
    if type(img) == np.ndarray:
        return 16.0 + (64.738 * img[:, :, 0] + 129.057 * img[:, :, 1] + 
            25.064 * img[:, :, 2]) / 256.0
    # elif type(img) == torch.Tensor:
    #     if len(img.shape) == 4:
    #         img = img.squeeze(0)
    #     return 16.0 + (64.738 * img[0, :, :] + 129.057 * img[1, :, :] + 25.064 * img[2, :, :]) / 256.0
    elif isinstance(img, paddle.Tensor):
        if len(img.shape) == 4:
            img = paddle.squeeze(img, axis=0)
        return 16.0 + (64.738 * img[0, :, :] + 129.057 * img[1, :, :] + 25.064 * img[2, :, :]) / 256.0
    else:
        raise Exception('Unknown Type', type(img))


def convert_rgb_to_ycbcr(img):
    if type(img) == np.ndarray:
        y = 16.0 + (64.738 * img[:, :, 0] + 129.057 * img[:, :, 1] + 25.064 *
            img[:, :, 2]) / 256.0
        cb = 128.0 + (-37.945 * img[:, :, 0] - 74.494 * img[:, :, 1] + 
            112.439 * img[:, :, 2]) / 256.0
        cr = 128.0 + (112.439 * img[:, :, 0] - 94.154 * img[:, :, 1] - 
            18.285 * img[:, :, 2]) / 256.0
        return np.array([y, cb, cr]).transpose([1, 2, 0])
    # elif type(img) == torch.Tensor:
    elif isinstance(img, paddle.Tensor):
        if len(img.shape) == 4:
            img = img.squeeze(0)
        y = 16.0 + (64.738 * img[0, :, :] + 129.057 * img[1, :, :] + 25.064 *
            img[2, :, :]) / 256.0
        cb = 128.0 + (-37.945 * img[0, :, :] - 74.494 * img[1, :, :] + 
            112.439 * img[2, :, :]) / 256.0
        cr = 128.0 + (112.439 * img[0, :, :] - 94.154 * img[1, :, :] - 
            18.285 * img[2, :, :]) / 256.0
        return torch2paddle.concat([y, cb, cr], 0).permute(1, 2, 0)
    else:
        raise Exception('Unknown Type', type(img))

def calc_psnr(img1, img2):
    return 10. * paddle.log10(1. / paddle.mean((img1 - img2) ** 2))

def convert_ycbcr_to_rgb(img):
    if type(img) == np.ndarray:
        r = 298.082 * img[:, :, 0] / 256.0 + 408.583 * img[:, :, 2
            ] / 256.0 - 222.921
        g = 298.082 * img[:, :, 0] / 256.0 - 100.291 * img[:, :, 1
            ] / 256.0 - 208.12 * img[:, :, 2] / 256.0 + 135.576
        b = 298.082 * img[:, :, 0] / 256.0 + 516.412 * img[:, :, 1
            ] / 256.0 - 276.836
        return np.array([r, g, b]).transpose([1, 2, 0])
    # elif type(img) == torch.Tensor:
    elif isinstance(img, paddle.Tensor):
        if len(img.shape) == 4:
            img = img.squeeze(0)
        r = 298.082 * img[0, :, :] / 256.0 + 408.583 * img[2, :, :
            ] / 256.0 - 222.921
        g = 298.082 * img[0, :, :] / 256.0 - 100.291 * img[1, :, :
            ] / 256.0 - 208.12 * img[2, :, :] / 256.0 + 135.576
        b = 298.082 * img[0, :, :] / 256.0 + 516.412 * img[1, :, :
            ] / 256.0 - 276.836
        return torch2paddle.concat([r, g, b], 0).permute(1, 2, 0)
    else:
        raise Exception('Unknown Type', type(img))


class AverageMeter(object):

    def __init__(self):
        self.reset()

    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count
