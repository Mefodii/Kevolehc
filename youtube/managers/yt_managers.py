from utils import File
from youtube.model.yt_monitors import YoutubeMonitor
from youtube.model.yt_video import YoutubeVideo
from youtube.utils import yt_datetime


class MonitorManager:
    def __init__(self, monitors_file, api_worker, log_file):
        self.log_file = log_file
        self.api = api_worker
        self.db = monitors_file
        data = File.get_file_lines(self.db)

        self.header = data[0]

        self.monitors = []
        for i in range(1, len(data)):
            monitor = YoutubeMonitor(data[i])
            monitor = self.validate_id(monitor)
            self.monitors.append(monitor)

    def __repr__(self):
        return "\n".join([self.header] + [repr(monitor) for monitor in self.monitors])

    def validate_id(self, monitor):
        if not monitor.id:
            response = self.api.get_channel_id_from_name(monitor.name)
            monitor.id = response.get('items')[0].get('id')

        return monitor

    def log(self, message):
        File.append_to_file(self.log_file, message)

    def check_for_updates(self):
        self.log(str(yt_datetime.get_current_ytdate()) + " - starting update process for monitors")
        for monitor in self.monitors:
            monitor.check_date = yt_datetime.get_current_ytdate()
            response = self.api.get_channel_videos_from_date(monitor.id, monitor.reference_date)

            if response[-1].get("snippet").get("publishedAt") == monitor.reference_date:
                response.pop()

            self.log(monitor.name + " - New videos from last check - " + len(response))
            for item in response:
                self.log("\t-\t" + item)
                yt_video = YoutubeVideo(item, monitor.video_number)

                monitor.video_number += 1
                monitor.append_video(yt_video)

    def finish(self):
        updated_data = [self.header]
        for monitor in self.monitors:
            monitor.reference_date = monitor.check_date
            updated_data.append(repr(monitor))
        File.write_lines_to_file_utf8(self.db, updated_data)


class YoutubeQueueManager:
    def __init__(self, api_instance):
        self.api = api_instance
        self.queue_list = []

    def add_queue(self, queue):
        self.queue_list.append(queue)
