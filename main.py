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
    # default value
    dir_output_relatively = os.path.join("data", "luna16")
    dir_output = os.path.join(os.path.dirname(os.path.abspath(__file__)), dir_output_relatively)

    parser = argparse.ArgumentParser(
        usage = "To run the system [pytorch-sepconv] repeatedly.\n"
            "(1.NOTE that the argument [--dir-input] should point to [.\\subset\\*\\] of LUNA16.\n"
            "(2.You can set (the repeatedly times) by input [--step] mannually\n"
            "or input the [--dir-mhd] to set that automatically.\n"
            "NOTE that at present, we think the number of info_step should be odd number\n"
            "or it will need to insert the same two images generated in CT suquence."
            )
    parser.add_argument("--dir-input", type=str, help="dir of images to input. It should be one of the folders naming .\\subset*\\*\\ from data set LUNA16.")
    parser.add_argument("--step", type=int, default=None, help="step between the two images.(how many times have to use sepconv repeatedly)")
    parser.add_argument("--dir-mhd", type=str, default=None, help="the dir of mhd.")
    parser.add_argument("--dir-output", type=str, default=dir_output, help="dir of generated images to output. Default:{}. Output tree: .\\subset*\\..\\".format(dir_output))
    args = parser.parse_args()

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

    return path_converted

def run_command(args, seriesuid, path_image_first, path_image_second, info_step):
    if info_step == 0:
        # Actually do nothing.
        None
    elif info_step == 1:
        name_and_ext_first_image = os.path.splitext(os.path.basename(path_image_first))
        name_generated_image = name_and_ext_first_image[0] + "_" + name_and_ext_first_image[1]
        name_folder = os.path.basename(os.path.dirname(seriesuid))
        path_generated_image = os.path.join(args.dir_output, name_folder, os.path.basename(seriesuid), name_generated_image)

        # run command
        command = "python run.py --model lf --first {} --second {} --out {}".format(path_image_first, path_image_second, path_generated_image)
        result = os.system(command)

    elif info_step == 3:
        name_and_ext_first_image = os.path.splitext(os.path.basename(path_image_first))
        name_generated_image_upper = name_and_ext_first_image[0] + "_" + name_and_ext_first_image[1]
        name_generated_image_middle = name_and_ext_first_image[0] + "__" + name_and_ext_first_image[1]
        name_generated_image_downer = name_and_ext_first_image[0] + "___" + name_and_ext_first_image[1]

        name_folder = os.path.basename(os.path.dirname(seriesuid))

        path_generated_image_upper = os.path.join(args.dir_output, name_folder, os.path.basename(seriesuid), name_generated_image_upper)
        path_generated_image_middle = os.path.join(args.dir_output, name_folder, os.path.basename(seriesuid), name_generated_image_middle)
        path_generated_image_downer = os.path.join(args.dir_output, name_folder, os.path.basename(seriesuid), name_generated_image_downer)

        # run command
        # middle
        command = "python run.py --model lf --first {} --second {} --out {}".format(path_image_first, path_image_second, path_generated_image_middle)
        result = os.system(command)
        # upper
        command = "python run.py --model lf --first {} --second {} --out {}".format(path_image_first, path_generated_image_middle, path_generated_image_upper)
        result = os.system(command)
        # downer
        command = "python run.py --model lf --first {} --second {} --out {}".format(path_generated_image_middle, path_image_second, path_generated_image_downer)
        result = os.system(command)

    elif info_step == 5:
        print('--------')
        print('infor_step gets value 5')

def main(args):
    path_seriesuid = os.path.join(args.dir_input, "*")
    list_seriesuid = glob.glob(path_seriesuid) # list for all the seriesuid folders

    #make sure there being the dir of output
    os.makedirs(args.dir_output, exist_ok=True)

    num_seriesuid = len(list_seriesuid)
    count_seriesuid = 0
    for each_seriesuid in list_seriesuid:
        count_seriesuid += 1
        path_image = os.path.join(each_seriesuid, 'whole_image', '*.tiff')
        list_image = glob.glob(path_image)
        list_image = sort_humanly(list_image)
        
        # [info_step] should be different for every [seriesuid CT image]
        info_step = get_info_step(args, each_seriesuid)

        num_image = len(list_image)
        count_image = 0
        # TODO use sepconv to generate images (by [info-step])
        for index in range(len(list_image)): # all the images of a CT sequence
            path_image_first_temp = list_image[index]
            path_image_second_temp = list_image[index + 1]

            # convert to RBG and save
            pathpath_converted_first = convert_to_rgb(args, each_seriesuid, path_image_first_temp)
            pathpath_converted_second = convert_to_rgb(args, each_seriesuid, path_image_second_temp)

            # algorithm maybe change later
            run_command(args, each_seriesuid, pathpath_converted_first, pathpath_converted_second, info_step)
            print("sub finisht: {:.2%}".format(count_image / num_image))
        
        print("finished: {:.2%}".format(count_seriesuid / num_seriesuid))

if __name__ == "__main__":
    args = argument()
    main(args)

    print("sepconv complete.")
    # if AttributeError: module 'sepconv' has no attribute 'FunctionSepconv'
    # check the environment whethere is 'env-pytorch-sepconv' or not.
