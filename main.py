import argparse
import glob
import os
import re

import cv2

class InfoMHD(): # to carry the information get from mhd
    def __init__(self, offset_x, offset_y, offset_z, element_spacing_x, element_spacing_y, element_spacing_z):
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.offset_z = offset_z

        self.element_spacing_x = element_spacing_x
        self.element_spacing_y = element_spacing_y
        self.element_spacing_z = element_spacing_z

def argument():
    dir_output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "luna16")
    parser = argparse.ArgumentParser(
        usage = "To run the system [pytorch-sepconv] repeatedly.\n"
            "(1.NOTE that the argument [--dir-input] should point to [subset*] of LUNA16.\n"
            "(2.You can set (the repeatedly times) by input [--step] mannually\n"
            "or input the [--dir-mhd] to set that automatically.\n"
            "(3.[the dir of output] will be:\n"
            "{}\n"
            "NOTE that at present, we think the number of info_step should be odd number\n"
            "or it will need to insert the same two images generated in CT suquence.".format(dir_output)
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
            if mhd_row.split(' ')[0] == 'Offset':
                offset_x = float(mhd_row.split(' ')[2])
                offset_y = float(mhd_row.split(' ')[3])
                offset_z = float(mhd_row.split(' ')[4].replace('\n', ''))
            if mhd_row.split(' ')[0] == 'ElementSpacing':
                element_spacing_x = float(mhd_row.split(' ')[2])
                element_spacing_y = float(mhd_row.split(' ')[3])
                element_spacing_z = float(mhd_row.split(' ')[4].replace('\n',''))

        info_mhd = InfoMHD(
            offset_x=offset_x,
            offset_y=offset_y,
            offset_z=offset_z,
            element_spacing_x=element_spacing_x,
            element_spacing_y=element_spacing_y,
            element_spacing_z=element_spacing_z,
        )
        return info_mhd

    def get_step_from_mhd(info_mhd):
        # TODO: calculate the [info_steo] from [info_mhd]
        # maybe the logic will change later
        info_step = 0
        while True:
            condition_x = ((info_mhd.element_spacing_z / (info_step + 1)) <= info_mhd.element_spacing_x)
            condition_y = ((info_mhd.element_spacing_z / (info_step + 1)) <= info_mhd.element_spacing_y)
            if condition_x and condition_y:
                break
            info_step += 1
        return info_step

    # check the mode
    if args.step:
        info_step = args.step
    elif args.dir_mhd:
        info_mhd = get_info_mhd(args, each_seriesuid)
        info_step = get_step_from_mhd(info_mhd)
    else:
        print('please input one of ([--step] or [--dir-mhd])')
    
    # the number of info_step should be odd number
    # or it need to insert the same two image generated in CT suquence.
    if ((info_step % 2) == 0) and info_step > 0:
        info_step -= 1

    return info_step

def convert_to_rgb(args, each_seriesuid, path_image):
    image_converted = cv2.imread(path_image, flags=3)
    folder_subset = os.path.basename(args.dir_input)
    id = os.path.basename(each_seriesuid)
    name_image = os.path.basename(path_image)

    path_converted = os.path.join(args.dir_output, folder_subset, id, name_image)
    os.makedirs(os.path.dirname(path_converted), exist_ok=True)
    cv2.imwrite(path_converted, image_converted)


'''
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
def run_command(args, each_seriesuid, path_image_first_temp, path_image_second_temp, info_step):
    if info_step == 0:
        # Actually do nothing.
        None
    elif info_step == 1:
        
    elif info_step == 3:
        None

def main(args):
    path_seriesuid = os.path.join(args.dir_input, "*")
    list_seriesuid = glob.glob(path_seriesuid) # list for all the seriesuid folders

    #make sure there being the dir of output
    os.makedirs(args.dir_output, exist_ok=True)

    for each_seriesuid in list_seriesuid:
        path_image = os.path.join(each_seriesuid, 'whole_image', '*.tiff')
        list_image = glob.glob(path_image)
        list_image = sort_humanly(list_image)
        
        # [info_step] should be different for every [seriesuid CT image]
        info_step = get_info_step(args, each_seriesuid)

        # TODO use sepconv to generate images (by [info-step])
        for index in range(len(list_image)): # all the images of a CT sequence
            if (index + info_step) > (len(list_image) - 1):
                break

            path_image_first_temp = list_image[index]
            path_image_second_temp = list_image[index + info_step]

            # convert to RBG and save
            convert_to_rgb(args, each_seriesuid, path_image_first_temp)
            convert_to_rgb(args, each_seriesuid, path_image_second_temp)

            # algorithm maybe change later
            run_command(args, each_seriesuid, path_image_first_temp, path_image_second_temp, info_step)

if __name__ == "__main__":
    args = argument()
    main(args)

    print("sepconv complete.")
