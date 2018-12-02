import codecs


def get_file_lines(file_name, utf=None):
    if utf:
        input_file = codecs.open(file_name, 'r', "utf-" + str(utf))
    else:
        input_file = open(file_name, 'r')

    data = []
    for input_line in input_file:
        data.append(input_line.replace("\n", ""))
    return data


def write_lines_to_file(file_name, file_text):
    result_file = open(file_name, 'w')
    for result_line in file_text:
        result_file.write(str(result_line) + "\n")
    result_file.close()


def write_lines_to_file_utf8(file_name, file_text):
    result_file = codecs.open(file_name, 'w', "utf-8")
    for result_line in file_text:
        result_file.write(str(result_line) + "\n")
    result_file.close()