import json
import rdflib
from moviepy.editor import VideoFileClip
import os
from act_movie_mapper import construct_full_path
import pdb

class RoomImageExtractor:
    def __init__(self, mp4_file_list_path):
        self.file_dict_ = {}
        with open(mp4_file_list_path, 'r') as f:
            for line in f:
                file_name, file_path = line.strip().split(',')
                self.file_dict_[file_name] = file_path
        self.episode_prefix_ = "../Knowledge-Graph-Reasoning-Challenge/DataSet/CompleteData/Episodes/"
        self.rdf_prefix_ = "../Knowledge-Graph-Reasoning-Challenge/DataSet/CompleteData/RDF/"
        
    def extract_images(self):
        g = rdflib.Graph()
        with open(self.rdf_prefix_ + "add_places.ttl", 'r') as file:
                g.parse(file, format='turtle')
        query = """
        PREFIX : <http://kgrc4si.home.kg/virtualhome2kg/ontology/>
        PREFIX ex: <http://kgrc4si.home.kg/virtualhome2kg/instance/>
        SELECT *
        WHERE {
            ?e :place ?place .
        }
        """
        result = g.query(query)
        event_by_place = {}
        for row in result:
            place = row.place
            if place not in event_by_place.keys():
                event_by_place[place] = row.e
        for place in event_by_place.keys():
            print(f"place is {place}, event is {event_by_place[place]}")
        # pdb.set_trace()            
        for place in event_by_place.keys():
            g = rdflib.Graph()
            event = event_by_place[place]
            event_id = int(event.split("/")[-1].split("_")[-1].split("scene")[-1])
            activity_path = self.rdf_prefix_ + event.split("/")[-1].split("_", 1)[-1].capitalize() + ".ttl"
            activity = "_".join(event.split("/")[-1].split("_")[1:-1]).capitalize()
            scene = event.split("/")[-1].split("_")[-1].split("scene")[-1]
            with open(activity_path, 'r') as file:
                g.parse(file, format='turtle')

            query = """
            PREFIX : <http://kgrc4si.home.kg/virtualhome2kg/ontology/>
            PREFIX ex: <http://kgrc4si.home.kg/virtualhome2kg/instance/>
            SELECT *
            WHERE {
                ?e :eventNumber ?n .
                ?e :time ?time .
                ?time time:numericDuration ?sec
            } order by ?n limit 100"""
            
            result = g.query(query)
            count = 0
            cumulative_time = 0
            for row in result:
                if count != event_id:
                    count += 1
                    cumulative_time += float(row.sec)
                    continue
                time = cumulative_time + float(row.sec) / 2 # 中央のフレームを取得
                prefix = self.file_dict_[activity]
                video_path = os.path.join(prefix, f"scene{scene}", "movies", f"{activity.replace("_", " ")}_4.mp4")
                self.save_image_from_video(video_path, time, place.split("/")[-1])
                break
                
    def save_image_from_video(self, video_path, time, place):
        with VideoFileClip(video_path) as video:
            frame = video.get_frame(time)
            output_path = f"./images/{place}.jpg"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            video.save_frame(output_path, t=time)
            print(f"Saved image for {place} at {output_path}")

if __name__ == "__main__":
    extractor = RoomImageExtractor(mp4_file_list_path='./mp4_files_list.txt')
    extractor.extract_images()