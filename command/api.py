from .windows_api import WindowsAPI, with_application


class API(WindowsAPI):
    def __init__(self):
        super().__init__()
