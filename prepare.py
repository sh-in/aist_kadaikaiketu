import os

def get_mp4_files_and_save_to_txt(directory, output_file):
    # Get all mp4 files in the directory and save them to a txt file
    with open(output_file, 'w') as f:
        # iterate over all categories (i.e. Abnormal, BedTimeSleep)
        for category in os.listdir(directory):
            # if category is not a directory, skip it
            if not os.path.isdir(os.path.join(directory, category)):
                continue
            category_path = os.path.join(directory, category)
            # iterate over all scenes in the category
            for scene in os.listdir(category_path):
                scene_path = os.path.join(category_path, scene)
                movie_path = os.path.join(scene_path, 'movies')
                # iterate over all mp4 files in the movie directory
                for file in os.listdir(movie_path):
                    if file.endswith('.mp4'):
                        file_name = os.path.splitext(file)[0]
                        file_path = os.path.join(movie_path, file)
                        f.write(f"{file_name}, {file_path}\n")

directory = '../data/Movie/'
output_file = 'mp4_files_list.txt'
get_mp4_files_and_save_to_txt(directory, output_file)

"""
使用例
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
"""