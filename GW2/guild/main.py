import time, ast
from utils.File import get_file_lines, write_lines_to_file
import urllib.request
from GW2.guild.html_parser import IngredientParser, MyHTMLParser
from GW2.constants import paths

ROOT_URL = "https://wiki.guildwars2.com"
ICON = "=IMAGE(\"https://wiki.guildwars2.com<SRC>\")"


def extract_ingredients(url):
    contents = urllib.request.urlopen(url).read()
    parser = IngredientParser()
    parser.feed(contents.decode("utf-8"))
    return parser.ingredients


def parse_workshop(name, url):
    result = []

    contents = urllib.request.urlopen(url).read()
    parser = MyHTMLParser()
    data = get_file_lines(paths.INPUT_FILE_PATH)
    one_line = ""
    for line in data:
        one_line += line
    parser.feed(contents.decode("utf-8"))

    print(parser.upgrades)
    for upgrade in parser.upgrades:
        line = upgrade.copy()
        ing = extract_ingredients(ROOT_URL + upgrade["href"])
        line["ingredients"] = ing

        result.append(line)

    write_lines_to_file(paths.OUTPUT_FILES_PATH + "\\" + name + ".txt", str(result))

    return result


def build_ingredient_list(data):
    ingredient_dict = {}
    for upgrade in data:
        for ingredient in upgrade.get("ingredients"):
            if not ingredient_dict.get(ingredient.get("name")):
                ingredient_dict[ingredient.get("name")] = ingredient.get("src")

    return ingredient_dict


def build_header(data):
    header = ["Icon", "Name"]
    for upgrade in data:
        header.append(upgrade.get("title"))
    return "\t".join(header)


def build_resource_line(ingredient, data):
    values = []

    cell_index = [64, 67]
    for upgrade in data:
        value = ""

        if cell_index[-1] == 90:
            cell_index[0] = cell_index[0] + 1
            cell_index[-1] = 65
        else:
            cell_index[-1] = cell_index[-1] + 1

        for upg_ing in upgrade.get("ingredients"):

            if ingredient == upg_ing.get("name"):
                qty = upg_ing.get("qty")

                if cell_index[0] == 64:
                    value = "=IF(" + chr(cell_index[1]) + "1=TRUE;" + qty + ";)"
                else:
                    value = "=IF(" + chr(cell_index[0]) + chr(cell_index[1]) + "1=TRUE;" + qty + ";)"

        values.append(value)

    return values


def pretty_excel(workshop, data):
    ingredient_dict = build_ingredient_list(data)

    lines = [build_header(data)]
    for name, src in ingredient_dict.items():
        record = [ICON.replace("<SRC>", src), name] + build_resource_line(name, data)
        lines.append("\t".join(record))

    write_lines_to_file(paths.OUTPUT_FILES_PATH + "\\" + workshop + "_pretty.txt", lines)


#######################################################################################################################
# Main function
#######################################################################################################################
def __main__():
    workshops = ["Guild_Workshop",
                 "Guild_Arena",
                 "Guild_Market",
                 "Guild_Mine",
                 "Guild_Tavern",
                 "War_Room",
                 ]
    name = "Complete"
    result = []

    for ws in workshops:
        result += parse_workshop(name, ROOT_URL + "/wiki/" + ws)
    pretty_excel(name, result)


#######################################################################################################################
# Process
#######################################################################################################################
if __name__ == "__main__":
    # Start time of the program
    start = time.time()

    # Main functionality
    __main__()

    # End time of the program
    end = time.time()
    # Running time of the program
    print("Program ran for: ", end - start, "seconds.")
