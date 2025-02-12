from editor.postprocessor import json_to_string
import datetime
import os

TODAY = datetime.datetime.now().strftime("%Y-%m-%d")

def kakao_uploader(file_path, selected_domain):
    content = json_to_string(selected_domain, file_path)
    return content