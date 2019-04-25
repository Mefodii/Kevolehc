import json

from utils import File
from youtube.model.yt_monitors import YoutubeMonitor


class MonitorManager:
    def __init__(self, monitors_file, api_worker):
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
            monitor.id = response['items'][0]['id']

        return monitor

    def check_for_updates(self):
        for monitor in self.monitors:
            response = self.api.get_channel_videos_from_date(monitor.id, monitor.reference_date)
            for item in response['items']:
                print(item)
            # print(response['items'][0])

    def finish(self):
        updated_data = [self.header] + [repr(monitor) for monitor in self.monitors]
        File.write_lines_to_file_utf8(self.db, updated_data)


class YoutubeQueueManager:
    def __init__(self, api_instance):
        self.api = api_instance
        self.queue_list = []

    def add_queue(self, queue):
        self.queue_list.append(queue)
