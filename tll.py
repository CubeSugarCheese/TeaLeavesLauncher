# -*- coding:utf-8 -*-
import uuid
import os

import ruamel.yaml as yaml

from launcherCore.auth.mojangAuth import MojangAccount
from launcherCore.auth.microsoftAuth import MicrosoftAccount
from launcherCore.auth.offlineAuth import OfflineAccount
from launcherCore.launcher import Launcher

config_path = f"{os.getcwd()}\\config.yml"


def save_config(data: dict):
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, Dumper=yaml.RoundTripDumper)


def load_config():
    if not os.path.exists(config_path):
        from launcherCore.utils.static import default_config
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(default_config)
    with open(config_path, "r", encoding="utf-8") as g:
        return yaml.load(g, Loader=yaml.Loader)


def choose_account():
    print("请选择一个账户：")
    print("【0】添加一个账户")
    choice = int(input())
    if choice == 0:
        print("""【1】mojang 账户
【2】微软账户
【3】外置登录（Authlib-injector）
【4】离线账户""")
        choice = int(input("请选择要添加的账户类型："))
        if choice == 1:
            username = input("邮箱：")
            password = input("密码：")
            account = MojangAccount(username, password)
        elif choice == 2:
            account = MicrosoftAccount()
        elif choice == 3:
            pass
        elif choice == 4:
            username = input("玩家名：")
            account = OfflineAccount(username)
        return account


def choose_game():
    print("请选择：")
    print("【0】手动输入 .minecraft 文件夹路径")
    mc_paths = load_config()["MC_paths"]
    if mc_paths:
        for i in mc_paths:
            print(f"【{mc_paths.index(i) + 1}】{i}")
    choice = int(input("选择："))
    if choice == 0:
        path = input(".minecraft 文件夹路径：")
    else:
        path = mc_paths[choice - 1]
    versions_path = path + "\\versions"
    versions = os.listdir(versions_path)
    for j in versions:
        print(f"【{versions.index(j)}】{j}")
    version_choice = int(input("请选择一个游戏版本（数字）："))
    version = versions[version_choice]
    return path, version


def main():
    config = load_config()
    if config["clientToken"] is None and config["auto_generate_clientToken"]:
        config["clientToken"] = uuid.uuid4().hex
    save_config(config)
    account = choose_account()
    mc_path, version = choose_game()
    launcher = Launcher(mc_path, version, account.uuid, account.username, account.mc_access_token)
    launcher.launch_game()


if __name__ == "__main__":
    main()
