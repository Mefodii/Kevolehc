from utils import File


class MonitorManager:
    def __init__(self, monitors_file):
        self.db = monitors_file
        data = File.get_file_lines(self.db)

        self.header = data[0]

        self.monitors = []
        for i in range(1, len(data)):
            self.monitors.append(Monitor(data[i]))

    def __repr__(self):
        return "\n".join([self.header] + [repr(monitor) for monitor in self.monitors])

    def finish(self):
        updated_data = [self.header] + [repr(monitor) for monitor in self.monitors]
        File.write_lines_to_file_utf8(self.db, updated_data)


class Monitor:
    def __init__(self, data_string):
        object_elements = data_string.split(";")

        if len(object_elements) != 5:
            print("Incorrect declaration of " + data_string)

        self.name = object_elements[0]
        self.id = object_elements[1]
        self.reference_date = object_elements[2]
        self.video_number = object_elements[3]
        self.format = object_elements[4]

    def validate(self):
        pass

    def validate_name_and_id(self):
        pass

    def validate_reference_date(self):
        pass

    def validate_video_number(self):
        pass

    def validate_format(self):
        pass

    def __repr__(self):
        return ";".join([self.name, self.id, self.reference_date, self.video_number, self.format])