# -*- coding:utf-8 -*-
import sys
import uuid
import os
from loguru import logger

from launcherCore.auth.mojangAuth import MojangAccount
from launcherCore.auth.microsoftAuth import MicrosoftAccount
from launcherCore.auth.offlineAuth import OfflineAccount
from launcherCore.auth.authlibInjectorAuth import AuthlibInjectorAccount
from launcherCore.launcher import Launcher
from launcherCore.config.appConfig import Config

config = Config()


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
            url = input("外置登录服务器url：")
            username = input("账户：")
            password = input("密码：")
            account = AuthlibInjectorAccount(url, username, password)
        elif choice == 4:
            username = input("玩家名：")
            account = OfflineAccount(username)
        else:
            logger.error("未添加账户，请检查输入是否合法")
            sys.exit(1)
        return account


def choose_game():
    print("请选择：")
    print("【0】手动输入 .minecraft 文件夹路径")
    mc_paths = config["MC_paths"]
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


def choose_java():
    print("请选择：")
    print("【0】使用系统环境 Java")
    java_paths = config["java_path"]
    if java_paths:
        for i in java_paths:
            print(f"【{java_paths.index(i) + 1}】{i}")
    choice = int(input("选择："))
    if choice == 0:
        path = "java"
    else:
        path = java_paths[choice - 1]
    return path


def main():
    if config["clientToken"] is None and config["auto_generate_clientToken"]:
        config["clientToken"] = uuid.uuid4().hex
    account = choose_account()
    mc_path, version = choose_game()
    java = choose_java()
    launcher = Launcher(mc_path, version, account.uuid, account.username, account.mc_access_token, java_path=java)
    launcher.launch_game()


if __name__ == "__main__":
    main()
