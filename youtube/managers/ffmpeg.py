import os
import re

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
            tag_value = value.replace("\"", "\"\"\"").replace("\'", "\"'\"")
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
