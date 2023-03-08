class ModelDataExample:
    def __init__(self):
        self.a = None
        self.b = None
        self.c = None

    def load_data(self, path):
        self.a = open(path)
        self.b = open(path)
        self.c = open(path)

    def get_a(self):
        return self.a
