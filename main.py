import argparse
import glob
import os
import re

import cv2

def argument():
    dir_output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "luna16")
    parser = argparse.ArgumentParser(
        usage = "To run the system [pytorch-sepconv] repeatedly.\n"
            "(1.NOTE that the argument [--dir-input] should point to [subset*] of LUNA16.\n"
            "(2.You can set (the repeatedly times) by input [--step] mannually\n"
            "or input the [--dir-mhd] to set that automatically.\n"
            "(3.[the dir of output] will be:\n"
            "{}".format(dir_output)
            )
    parser.add_argument("--dir-input", type=str, help="dir of images to input. It should be one of the folders naming 'subset*' from data set LUNA16.")
    parser.add_argument("--step", type=int, default=None, help="step between the two images.(how many times have to use sepconv repeatedly)")
    parser.add_argument("--dir-mhd", type=str, default=None, help="the dir of mhd.")

    args = parser.parse_args()
    args.dir_output = dir_output

    return args

def sort_humanly(v_list):
    # used to sort images in folder [whole_image], 
    # and not to sort folders [seriesuid] in [subset*].
    def tryint(s):
        try:
            return int(s)
        except ValueError:
            return s

    def str2int(v_str):
        return [tryint(sub_str) for sub_str in re.split('([0-9]+)', v_str)]

    return sorted(v_list, key=str2int)

def get_info_step(args, each_seriesuid):
    def get_info_mhd(args, each_seriesuid):
        name_ext_mhd = os.path.basename(each_seriesuid + '.mhd')
        path_mhd = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '3d-rnn', 'data', 'luna16', 'mhd', name_ext_mhd)
        file_mhd = open(path_mhd)
        for mhd_row in file_mhd:
            print(mhd_row)

    def get_step_from_mhd():
        None
        

    # check the mode
    if args.step:
        info_step = args.step
    elif args.dir_mhd:
        info_mhd = get_info_mhd(args, each_seriesuid)
        info_step = get_step_from_mhd(info_mhd)
    else:
        print('please input one of ([--step] or [--dir-mhd])')
    
    return info_step

def main(args):
    path_seriesuid = os.path.join(args.dir_input, "*")
    list_seriesuid = glob.glob(path_seriesuid) # list for all the seriesuid folders

    #make sure there being the dir of output
    os.makedirs(args.dir_output, exist_ok=True)

    for each_seriesuid in list_seriesuid:
        path_image = os.path.join(each_seriesuid, 'whole_image', '*.tiff')
        list_image = glob.glob(path_image)
        list_image = sort_humanly(list_image)
        
        info_step = get_info_step(args, each_seriesuid)

        for each_image in list_image: # all the images of a CT sequence
            None

'''
    for index in range(0, len(list_image), 1):
        if (index + args.step) > (len(list_image) - 1):
            break

        image_first = list_image[index]
        image_second = list_image[index + args.step]
        
        # convert to RGB
        image_first_temp = cv2.imread(image_first, flags=3)
        path_first = os.path.join(args.dir_output, os.path.basename(image_first))
        cv2.imwrite(path_first, image_first_temp)
        image_first = path_first

        image_second_temp = cv2.imread(image_second, flags=3)
        path_second = os.path.join(args.dir_output, os.path.basename(image_second))
        cv2.imwrite(path_second, image_second_temp)
        image_second = path_second

        # run command
        name_out_and_ext = os.path.basename(list_image[index])
        name_out, ext = os.path.splitext(name_out_and_ext)
        image_out = os.path.join(args.dir_output, "{}_.tiff".format(name_out))

        command = "python run.py --model lf --first {} --second {} --out {}".format(image_first, image_second, image_out)
        result = os.system(command)
        # if AttributeError: module 'sepconv' has no attribute 'FunctionSepconv'
        # check the environment whethere is 'env-pytorch-sepconv' or not.
        count_image += 1
        print("finished: {:.2%}".format(count_image / num_image))
'''

if __name__ == "__main__":
    args = argument()
    main(args)

    print("sepconv complete.")
