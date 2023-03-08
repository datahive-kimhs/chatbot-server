from data.data import ModelDataExample


model_data = ModelDataExample()


def init_extensions():
    model_data.load_data("some path")
