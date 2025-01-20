from pathlib import Path
import json
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
    
def get_room(project_path: Path,image_path: Path,scene: str, activity: str):
    # client = OpenAI(api_key=os.environ.get('API_KEY', None))
    client = OpenAI(api_key=API_KEY)
    base64_image_1 = encode_image(image_path= project_path / Path(f"methods/prompt_images/{scene}/kitchen.png"))
    base64_image_2 = encode_image(image_path= project_path / Path(f"methods/prompt_images/{scene}/bedroom.png"))
    base64_image_3 = encode_image(image_path= project_path / Path(f"methods/prompt_images/{scene}/bathroom.png"))
    base64_image_4 = encode_image(image_path= project_path / Path(f"methods/prompt_images/{scene}/livingroom.png"))
    base64_image_test = encode_image(image_path=image_path)
    query = [
    {
      "role": "system",
      "content": [
        {
          "text": "Which of the following rooms are you in now?\n- bedroom\n- bathroom\n- kitchen\n- livingroom",
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
                "url": f"data:image/png;base64,{base64_image_1}"
            }
            }
        ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": "kitchen"
        }
      ]
    },
    {
        "role": "user",
        "content": [
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{base64_image_2}"
            }
            }
        ]
    },
    {
        "role": "assistant",
        "content": [
            {
            "type": "text",
            "text": "bedroom"
            }
        ]
    },
    {
        "role": "user",
        "content": [
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{base64_image_3}"
            }
            }
        ]
    },
    {
        "role": "assistant",
        "content": [
            {
            "type": "text",
            "text": "bathroom"
            }
        ]
    },
    {
        "role": "user",
        "content": [
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{base64_image_4}"
            }
            }
        ]
        },
    {
        "role": "assistant",
        "content": [
            {
            "type": "text",
            "text": "livingroom"
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

def get_action(project_path: Path,image_path: Path,scene: str, activity: str, action_list: list, qa_num=None):
    client = OpenAI(api_key=API_KEY)
    base64_image_test = encode_image(image_path=image_path)
    action_text = "\n".join(action_list)
    if qa_num is not None:
        query = [
        {
        "role": "system",
        "content": [
            {
            "text": f"Which of the following rooms are you in now?\n{action_text}\nOnly output one action. Do not output in the sentence format.",
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
    else:
        query = [
        {
        "role": "system",
        "content": [
            {
            "text": f"Which of the following rooms are you in now?\n{action_text}\nOnly output one action. Do not include the word 'walk'. Do not output in the sentence format.",
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

# 1. 画像から部屋の記述の生成 room: kitchen, bedroom, bathroom, livingroom
# 2. 画像から行動の記述
def call_openai_api(PROJECT_PATH:Path, scene:str, activity:str, file_dict:dict, j:int, time:float, duration:float, mode:str="room", action_list=None, qa_num=None):
    # 動画のパス
    MOVIE_PATH = PROJECT_PATH / Path("data/Movie")
    if mode == "room":
        # 画像/動画/記述のパス
        video_path = file_dict[activity.replace("_"," ") + "_3" + "_" + scene]
        # activity_#event_3
        img_path = PROJECT_PATH / Path(f"data/imgs/{activity}_{j}_3_{scene}.png")
        text_path = PROJECT_PATH / Path(f"data/places/{activity}_{j}_3_{scene}.txt")
    elif mode == "action":
        # 画像/動画/記述のパス
        video_path = file_dict[activity.replace("_"," ") + "_2" + "_" + scene]
        # activity_#event_2
        img_path = PROJECT_PATH / Path(f"data/imgs/{activity}_{j}_2_{scene}.png")
        text_path = PROJECT_PATH / Path(f"data/actions/{activity}_{j}_2_{scene}.txt")
    # 画像ディレクトリの確認
    if not os.path.exists(PROJECT_PATH/Path("data/imgs")):
        os.makedirs(PROJECT_PATH/Path("data/imgs"), exist_ok=True)
    # テキストディレクトリの確認
    if not os.path.exists(PROJECT_PATH/Path("data/places")):
        os.makedirs(PROJECT_PATH/Path("data/places"), exist_ok=True)
    if not os.path.exists(PROJECT_PATH/Path("data/actions")):
        os.makedirs(PROJECT_PATH/Path("data/actions"), exist_ok=True)
    # activityの画像の確認
    if not os.path.exists(img_path):
        # 動画から画像を生成
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.set(cv2.CAP_PROP_POS_FRAMES, round((time+(duration*0.7))*fps))
        ret, frame = cap.read()
        if ret:
            cv2.imwrite(img_path, frame)
    # 部屋の記述の生成
    if mode == "room":
        if not os.path.exists(text_path):
            print("using GPT-4o-mini to get room")
            room = get_room(PROJECT_PATH, img_path, scene, activity)
            with open(text_path, "w", encoding="utf-8") as f:
                f.write(room)
        else:
            with open(text_path, "r", encoding="utf-8") as f:
                room = f.read()
        return video_path, room
    elif mode == "action":
        if not os.path.exists(text_path):
            print("using GPT-4o-mini to get action")
            action = get_action(PROJECT_PATH, img_path, scene, activity, action_list, qa_num)
            with open(text_path, "w", encoding="utf-8") as f:
                f.write(action)
        else:
            with open(text_path, "r", encoding="utf-8") as f:
                action = f.read()
        return video_path, action