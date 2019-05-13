import os

from ..utils.constants import MERGED_FORMAT


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
            tag_str = "-metadata " + key + "=\"" + value + "\""
            tags.append(tag_str)

        tags_command = " ".join(tags)
        command = "ffmpeg -i " + temp_abs_path + " -c copy  " + tags_command + " " + tag_abs_path
        os.system(command)

        os.rename(tag_abs_path, file_abs_path)
        os.remove(temp_abs_path)
