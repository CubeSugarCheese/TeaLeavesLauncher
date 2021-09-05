import time
import webview


class MicrosoftAccount:

    def __init__(self):
        webview.create_window("https://login.live.com/oauth20_authorize.srf?client_id=00000000402b5328"
                              "&response_type=code&scope=service%3A%3Auser.auth.xboxlive.com%3A%3AMBI_SSL"
                              "&redirect_uri=https%3A%2F%2Flogin.live.com%2Foauth20_desktop.srf")
        webview.start()


if __name__ == '__main__':
    test = MicrosoftAccount()
