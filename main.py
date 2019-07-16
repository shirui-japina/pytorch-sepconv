import argparse
import glob
import os
import re

import cv2

def argument():
    parser = argparse.ArgumentParser(
        usage = "run the system 'pytorch-sepconv' repeatedly."
        )
    parser.add_argument("--dir-input", type=str, help="dir of images to input.")
    parser.add_argument("--dir-output", type=str, help="dir of images to output.")
    parser.add_argument("--step", type=int, help="step between the two images.")
    args = parser.parse_args()

    return args

def main(args):
    path_image = os.path.join(args.dir_input, "*")
    list_image = glob.glob(path_image)
    # list_image.sort()
    list_image_soted = sort_humanly(list_image)
    os.makedirs(args.dir_output, exist_ok=True)

    for index in range(0, len(list_image_soted), 1):
        if (index + args.step) > (len(list_image) - 1):
            break

        image_first = list_image_soted[index]
        image_second = list_image_soted[index + args.step]
        name_out_and_ext = os.path.basename(list_image_soted[index])
        name_out, ext = os.path.splitext(name_out_and_ext)
        image_out = os.path.join(args.dir_output, "{}_.png".format(name_out))

        command = "python run.py --model lf --first {} --second {} --out {}".format(image_first, image_second, image_out)
        result = os.system(command)

def tryint(s):
    try:
        return int(s)
    except ValueError:
        return s

def str2int(v_str):
    return [tryint(sub_str) for sub_str in re.split('([0-9]+)', v_str)]

def sort_humanly(v_list):
    return sorted(v_list, key=str2int)

if __name__ == "__main__":
    args = argument()
    main(args)

    print("sepconv complete.")
