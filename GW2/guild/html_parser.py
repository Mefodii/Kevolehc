from html.parser import HTMLParser


class IngredientParser(HTMLParser):
    def error(self, message):
        pass

    def __init__(self):
        super().__init__()
        self.in_recipe = False
        self.current_tag = ""
        self.element = {}
        self.ingredients = []

    def handle_starttag(self, tag, attrs):
        if self.in_recipe:
            self.current_tag = tag
            if tag == "img":
                for attr in attrs:
                    if attr[0] == "alt":
                        self.element["name"] = attr[1].replace(".png", "")
                    if attr[0] == "src":
                        self.element["src"] = attr[1].replace("20px", "40px")
        else:
            if tag == "div":
                for attr in attrs:
                    if attr[0] == "class" and attr[1] == "ingredients":
                        self.in_recipe = True

    def handle_endtag(self, tag):
        if self.in_recipe:
            if tag == "dl":
                self.in_recipe = False
            elif tag == "dd":
                self.ingredients.append(self.element.copy())
                self.element = {}

    def handle_data(self, data):
        if self.in_recipe:
            if self.current_tag == "dt":
                self.element["qty"] = data.replace(" ", "")
                self.current_tag = ""

    def handle_comment(self, data):
        pass

    def handle_entityref(self, name):
        pass

    def handle_charref(self, name):
        pass

    def handle_decl(self, data):
        pass


class MyHTMLParser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.in_recipe = False
        self.upgrades = []
        self.element_parsed = False
        self.max = 1000
        self.current = 0

    def handle_starttag(self, tag, attrs):
        if self.in_recipe:
            if tag == "tr":
                self.element_parsed = False
            if tag == "a" and not self.element_parsed and self.current < self.max:
                self.element_parsed = True
                self.current += 1
                element = {}
                for attr in attrs:
                    if attr[0] == "href":
                        element["href"] = attr[1]
                    if attr[0] == "title":
                        element["title"] = attr[1]
                self.upgrades.append(element)

        else:
            if tag == "table":
                for attr in attrs:
                    if attr[0] == "class" and attr[1] == "table":
                        self.in_recipe = True

    def handle_endtag(self, tag):
        if self.in_recipe:
            if tag == "table":
                self.in_recipe = False

    def handle_data(self, data):
        pass