# given file list, read it and contain as an associative array
# file list contains, file name , comma, file path

import os

def read_file_list(file_list):
    # read file list and contain as an associative array
    file_dict = {}
    with open(file_list, 'r') as f:
        for line in f:
            file_name, file_path = line.strip().split(',')
            file_dict[file_name] = file_path
    return file_dict

if __name__ == '__main__':
    file_list = 'mp4_files_list.txt'
    file_dict = read_file_list(file_list)
    print(file_dict["Fall while walking forward1_3"])