import os
import glob
import argparse
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
    list_image.sort()
    os.makedirs(args.dir_output, exist_ok=True)

    for index in range(0, len(list_image), 1):
        image_first = list_image[index]
        image_second = list_image[index + args.step]

        name_out = os.path.basename(list_image[index]) + "_"
        image_out = os.path.join(args.dir_output, "{}.png".format(name_out))
        command = "python run.py --model lf --first {} --second {} --out {}".format(image_first, image_second, image_out)
        result = os.system(command)
        
        if (index + args.step) > len(list_image):
            break

if __name__ == "__main__":
    args = argument()
    main(args)

    print("sepconv complete.")
