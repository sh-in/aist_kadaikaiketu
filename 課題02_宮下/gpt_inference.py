from pathlib import Path
import json
import pdb
import re 
from openai import OpenAI
import base64
import os
import argparse
import cv2

# room: kitchen, bedroom, bathroom, livingroom
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
def get_room(image_path ,scene):
    client = OpenAI(api_key=os.environ.get('API_KEY', None))
    # client = OpenAI(api_key=API_KEY)
    images = os.listdir(f"./images")
    images = [f"./images/{image}" for image in images if scene in image]
    base64_images = [encode_image(image_path=image) for image in images]
    room_names = [ images.split("/")[-1].split(".")[0] for images in images]
    
    base64_image_test = encode_image(image_path=image_path)
    
    room_list_text = "\n".join([f"- {room}" for room in room_names])
    query = [
    {
      "role": "system",
      "content": [
        {
          "text": f"Which of the following rooms are you in now?\n{room_list_text}",
          "type": "text"
        }
      ]
    }
    ]

    for base64_image, room_name in zip(base64_images, room_names):
        query.append(
            {
                "role": "user",
                "content": [
                    {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_image}"
                    }
                    }
                ]
            }
        )
        query.append(
            {
                "role": "assistant",
                "content": [
                    {
                    "type": "text",
                    "text": room_name
                    }
                ]
            }
        )

    query.append(
        {
            "role": "user",
            "content": [
                {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{base64_image_test}"
                }
                }
            ]
        }
    )
    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages= query,
    temperature=1.0,
    max_tokens=30,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )
    return response.choices[0].message.content

def get_action(image_path, action_list):
    client = OpenAI(api_key=os.environ.get('API_KEY', None))
    base64_image_test = encode_image(image_path=image_path)
    action_text = "\n".join(action_list)
    query = [
    {
    "role": "system",
    "content": [
        {
        "text": f"Which of the following actions does this person perform?\n{action_text}\nOnly output one action. Do not output in the sentence format.",
        "type": "text"
        }
    ]
    },
    {
        "role": "user",
        "content": [
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{base64_image_test}"
            }
            }
        ]
    },
    ]
   
    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages= query,
    temperature=1.0,
    max_tokens=30,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )
    return response.choices[0].message.content

def query_gpt(movie_full_path, action_list, time, event_id, mode):
    if mode not in ["room", "action"]:
        raise ValueError("mode must be 'room' or 'action'")
    scene = movie_full_path.split("/")[-3]
    activity = movie_full_path.split("/")[-1].split(".")[0]
    viewpoint = movie_full_path[-5]
    cache_dir = "./cache"
    image_dir = Path(cache_dir) / scene / activity / f"event{event_id}" / f"view{viewpoint}"
    answer_filename = Path(cache_dir) / scene / activity / f"event{event_id}" / f"{mode}_answer.txt"
    # 推論に使う画像の保存
    cap = cv2.VideoCapture(movie_full_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    if not image_dir.exists():
        
        image_dir.mkdir(parents=True, exist_ok=True)

        start_frame = int(time[0] * fps)
        end_frame = int(time[1] * fps)
        for i in range(start_frame, end_frame+1): # durationが0の対策で+1
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if not ret:
                break
            frame_path = image_dir / f"frame_{i:04d}.png"
            cv2.imwrite(str(frame_path), frame)
        print(f"Saved images to {image_dir} ({end_frame - start_frame} frames)")
    cap.release()

    if mode == "action":
        image_files = sorted(image_dir.glob("*.png"))
        if not image_files:
            raise FileNotFoundError("No image files found in the directory.")
        median_frame_path = image_files[len(image_files) // 2]
        if not answer_filename.exists():
            action = get_action(image_path=median_frame_path, action_list=action_list)
            with open(answer_filename, "w") as f:
                f.write(action)
        else:
            print("GPT skipped")
        with open(answer_filename, "r") as f:
            action = f.read()
        return action
    
    elif mode == "room":
        image_files = sorted(image_dir.glob("*.png"))
        if not image_files:
            raise FileNotFoundError("No image files found in the directory.")
        answer_filename_start = Path(cache_dir) / scene / activity / f"event{event_id}" / "room_answer_start.txt"
        answer_filename_end = Path(cache_dir) / scene / activity / f"event{event_id}" / "room_answer_end.txt"
        if not answer_filename_start.exists():
            start_room = get_room(image_path=image_files[0], scene=scene)
            with open(answer_filename_start, "w") as f:
                f.write(start_room)
        else:
            print("GPT skipped")
        with open(answer_filename_start, "r") as f:
            start_room = f.read()

        if not answer_filename_end.exists():
            end_room = get_room(image_path=image_files[-1], scene=scene)
            with open(answer_filename_end, "w") as f:
                f.write(end_room)
        else:
            print("GPT skipped")
        with open(answer_filename_end, "r") as f:
            end_room = f.read()
        return start_room, end_room
