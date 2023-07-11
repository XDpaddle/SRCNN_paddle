import argparse
import paddle
import numpy as np
import PIL.Image as pil_image
from models import SRCNN
from utils import convert_rgb_to_ycbcr
from utils import convert_ycbcr_to_rgb
from utils import calc_psnr

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--weights-file', type=str, required=True)
    parser.add_argument('--image-file', type=str, required=True)
    parser.add_argument('--scale', type=int, default=3)
    args = parser.parse_args()

    device = paddle.CUDAPlace(0)

    model = SRCNN().to(device)

    state_dict = model.state_dict()
    for n, p in paddle.load(args.weights_file).items():
        if n in state_dict.keys():
            state_dict[n].copy_(p)
        else:
            raise KeyError(n)
        
    model.eval()
    image = pil_image.open(args.image_file).convert('RGB')
    image_width = image.width // args.scale * args.scale
    image_height = image.height // args.scale * args.scale

    image = image.resize((image_width, image_height), resample=pil_image.BICUBIC)
    image = image.resize((image.width // args.scale, image.height // args.scale), resample=pil_image.BICUBIC)
    image = image.resize((image.width * args.scale, image.height * args.scale), resample=pil_image.BICUBIC)
    
    image.save(args.image_file.replace('.', '_bicubic_x{}.'.format(args.scale)))
    
    image = np.array(image).astype(np.float32)
    ycbcr = convert_rgb_to_ycbcr(image)
    y = ycbcr[..., 0]
    y /= 255.0
    y = paddle.to_tensor(y).to(device)
    y = y.unsqueeze(0).unsqueeze(0)

    with paddle.no_grad():
        preds = model(y).clip(0.0, 1.0)
    psnr = calc_psnr(y, preds)
    print('PSNR: {:.2f}'.format(psnr.numpy()[0]))
    preds = preds.mul(255.0).cpu().numpy().squeeze(0).squeeze(0)
    output = np.array([preds, ycbcr[..., 1], ycbcr[..., 2]]).transpose([1, 2, 0])
    output = np.clip(convert_ycbcr_to_rgb(output), 0.0, 255.0).astype(np.uint8)
    output = pil_image.fromarray(output)
    output.save(args.image_file.replace('.', '_srcnn_x{}.'.format(args.scale)))
