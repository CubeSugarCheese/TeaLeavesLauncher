import time
import webview

class MicrosoftAccount:


    def __init__(self):
        window = webview.create_window("")
        webview.start(print(window.get_current_url), window)

if __name__ == '__main__':
    test = MicrosoftAccount()