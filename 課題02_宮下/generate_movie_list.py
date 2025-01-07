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

directory = '../Knowledge-Graph-Reasoning-Challenge/movie/'
output_file = 'mp4_files_list.txt'
get_mp4_files_and_save_to_txt(directory, output_file)