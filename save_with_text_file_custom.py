from nodes import SaveImage
import folder_paths as comfy_paths
import os
import numpy as np
from PIL import Image
import json
from PIL.PngImagePlugin import PngInfo
from comfy.cli_args import args

class SaveWithTextCustom(SaveImage):
    FUNCTION = "func"

    @classmethod   
    def INPUT_TYPES(s):
        it = SaveImage.INPUT_TYPES()
        it['required']['text'] = ("STRING", {"default": ""})
        it['required']['save_path'] = ("STRING", {"default": ""})
        return it
    
    def func(self, images, filename_prefix, save_path, text, prompt=None, extra_pnginfo=None):
        returnable = self.save_images_with_custom_path(images, save_path, filename_prefix, prompt, extra_pnginfo)
        for result in returnable['ui']['images']:
            path = os.path.join(save_path, result['subfolder'], result['filename'])
            txt_path = os.path.splitext(path)[0] + ".txt"
            with open(txt_path, 'w') as f:
                print(text, file=f)
        return returnable
    
    def save_images_with_custom_path(self, images, save_path, filename_prefix="ComfyUI", prompt=None, extra_pnginfo=None):
        filename_prefix += self.prefix_append
        full_output_folder, filename, counter, subfolder, filename_prefix = comfy_paths.get_save_image_path(filename_prefix, save_path, images[0].shape[1], images[0].shape[0])
        results = list()
        for (batch_number, image) in enumerate(images):
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            metadata = None
            if not args.disable_metadata:
                metadata = PngInfo()
                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))
                if extra_pnginfo is not None:
                    for x in extra_pnginfo:
                        metadata.add_text(x, json.dumps(extra_pnginfo[x]))

            filename_with_batch_num = filename.replace("%batch_num%", str(batch_number))
            file = f"{filename_with_batch_num}_{counter:05}_.png"
            img.save(os.path.join(full_output_folder, file), pnginfo=metadata, compress_level=self.compress_level)
            results.append({
                "filename": file,
                "subfolder": subfolder,
                "type": self.type
            })
            counter += 1

        return { "ui": { "images": results } }
    

