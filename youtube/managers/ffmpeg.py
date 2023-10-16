import os
import re
from typing import Tuple

from utils import File
from ..utils.constants import MERGED_FORMAT

METADATA_HEADER = ";FFMETADATA1"


class Ffmpeg:
    @staticmethod
    def merge_audio_and_video(files_path, audio, video, merged):
        audio_abs_path = files_path + "\\" + video
        video_abs_path = files_path + "\\" + audio
        merged_abs_path = files_path + "\\" + merged
        temp_merged_file = files_path + "\\merged." + MERGED_FORMAT

        merge_command = "ffmpeg" \
                        " -i " + video_abs_path + \
                        " -i " + audio_abs_path + \
                        " -c:v copy -c:a copy " + temp_merged_file
        os.system(merge_command)
        os.remove(audio_abs_path)
        os.remove(video_abs_path)
        os.rename(temp_merged_file, merged_abs_path)

    @staticmethod
    def add_tags(file_abs_path, tags_dict):
        file_format = file_abs_path.split(".")[-1]

        file_path = "\\".join(file_abs_path.split("\\")[:-1])
        temp_abs_path = file_path + "\\temptags." + file_format
        tag_abs_path = file_path + "\\tags." + file_format

        os.rename(file_abs_path, temp_abs_path)

        tags = []
        for key, value in tags_dict.items():
            tag_value = value.replace("\"", "\\\"").replace("\'", "\"'\"")

            # The titles with symbol "&" and between quotes will be replaced with "^&"
            # In that way ffmpeg command will be generated correctly
            if "&" in file_abs_path and "\"" in tag_value:
                splitted = tag_value.split("\"")
                for i in range(1, len(splitted), 2):
                    if i != len(splitted):
                        splitted[i] = splitted[i].replace("&", "^&")
                tag_value = "\"".join(splitted)

            tag_str = "-metadata " + key + "=\"" + tag_value + "\""
            tags.append(tag_str)

        tags_command = " ".join(tags)
        command = "ffmpeg -i " + temp_abs_path + " -c copy  " + tags_command + " " + tag_abs_path
        os.system(command)

        os.rename(tag_abs_path, file_abs_path)
        os.remove(temp_abs_path)

    @staticmethod
    def get_metadata(file_abs_path):
        file_format = file_abs_path.split(".")[-1]
        file_path = "\\".join(file_abs_path.split("\\")[:-1])

        temp_abs_path = file_path + "\\tempmeta." + file_format
        temp_metadata_file = file_path + "\\tempmetadata.txt"

        os.rename(file_abs_path, temp_abs_path)

        read_metadata_command = "ffmpeg" \
                                " -i " + temp_abs_path + \
                                " -f ffmetadata " + temp_metadata_file

        os.system(read_metadata_command)
        os.rename(temp_abs_path, file_abs_path)

        metadata = File.get_file_lines(temp_metadata_file, "8")
        os.remove(temp_metadata_file)
        return metadata

    @staticmethod
    def metadata_to_json(raw_metadata):
        json_metadata = {}
        attr_match = "\\S*="
        attr_name = None
        attr_value = None

        for line in raw_metadata:
            parsed_line = re.search(attr_match, line)
            if line == METADATA_HEADER:
                pass
            else:
                if parsed_line and len(parsed_line.group()) > 1:
                    if attr_name:
                        json_metadata[attr_name] = attr_value

                    attr_name = parsed_line.group().replace("=", "").upper()
                    attr_value = "=".join(line.split("=")[1:])
                else:
                    attr_value += "\n" + line
        json_metadata[attr_name] = attr_value

        return json_metadata

    @staticmethod
    def get_video_resolution(video_abs_path) -> Tuple[int, int]:
        output = os.popen(f"ffprobe -v error -select_streams v:0 "
                          f"-show_entries stream=width,height -of csv=s=x:p=0 \"{video_abs_path}\"").read()
        width, height = output.split("x")
        return int(width), int(height)

    @staticmethod
    def get_video_bitrate(video_abs_path):
        pass # https://superuser.com/questions/1106343/determine-video-bitrate-using-ffmpeg

    @staticmethod
    def resize(file_abs_path, height: int = None, width: int = None, bitrate: str = None):
        if not height and not width:
            raise Exception("Both height and width are not specified. At least one should have a value")

        original_width, original_height = Ffmpeg.get_video_resolution(file_abs_path)
        if (width and int(original_width) <= width) or (height and int(original_height) <= height):
            print("File original size is already equal or less than resize value. Resize cancelled.\n"
                  f"Original resolution {original_width}x{original_height}. Resize: {width}x{height}")
            return

        h = height if height else -1
        w = width if width else -1

        file_format = file_abs_path.split(".")[-1]
        file_path = "\\".join(file_abs_path.split("\\")[:-1])
        temp_resize_file = file_path + "\\temp_resized." + file_format

        command = f"ffmpeg -hwaccel cuda -i \"{file_abs_path}\" -vf scale={str(w)}:{str(h)} -c:v h264_nvenc "
        if bitrate:
            command += f"-b:v {bitrate} "
        command += f"{temp_resize_file}"
        os.system(command)

        # Delete resized file if it is still larger or equal to original file
        original_size = os.path.getsize(file_abs_path)
        resized_size = os.path.getsize(temp_resize_file)

        if resized_size >= original_size:
            os.remove(temp_resize_file)
            print(f"Resized file ({resized_size}) is not smaller than original file ({original_size}). Resize cancelled")
        else:
            os.remove(file_abs_path)
            os.rename(temp_resize_file, file_abs_path)
