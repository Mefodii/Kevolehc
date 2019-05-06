import os
import re


class FFMPEG():
    RESTRICTED_CHARS = ['<', '>', ':', '\"', '/', '\\', '?', '*']

    def __init__(self):
        self.restrict_replacer = "#"

    def set_restrict_replacer(self, value):
        self.restrict_replacer = value

    def normalize_file_name(self, file_abs_path):
        split_abs_path = file_abs_path.split("\\")

        path = split_abs_path[:-1]
        file_name = split_abs_path[-1]
        normalized_file_name = re.sub('[' + re.escape(''.join(FFMPEG.RESTRICTED_CHARS)) + ']', self.restrict_replacer, file_name)

        return path + '\\' + normalized_file_name + ".mp4"


    def merge_audio_and_video(self, audio_abs_path, video_abs_path, merged_abs_path, remove_source=True):
        temp_merged_file = queue.save_location + "\\merged.mp4"

        merge_command = "ffmpeg -i " + audio_abs_path + " -i " + video_abs_path + " -c:v copy -c:a copy " + temp_merged_file
        os.system(merge_command)
        os.rename(temp_merged_file, merged_file)

        if remove_source:
            os.remove(audio_abs_path)
            os.remove(video_abs_path)
