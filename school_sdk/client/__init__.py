# -*- coding: utf-8 -*-
'''
    :file: __init__.py
    :author: -Farmer
    :url: https://blog.farmer233.top
    :date: 2021/09/02 22:20:52
'''
from typing import Dict, Union
import requests
from school_sdk.client.api.score import Score
from school_sdk.client.api.user_info import Info
from school_sdk.config import URL_ENDPOINT
from school_sdk.client.api.schedules import Schedule
from school_sdk.client.exceptions import LoginException
import time
from school_sdk.client.api.login import ZFLogin
from school_sdk.client.base import BaseUserClient


class SchoolClient():

    def __init__(self, host, port: int = 80, ssl: bool = False, name=None, exist_verify: bool = False,
                 captcha_type: str = "captcha", retry: int = 10, lan_host=None, lan_port=80, timeout=10,
                 login_url_path=None, url_endpoints=None) -> None:
        """初始化学校配置

        Args:
            host (str): 主机地址
            port (int, optional): 端口号. Defaults to 80.
            ssl (bool, optional): 是否启用HTTPS. Defaults to False.
            name (str, optional): 学校名称. Defaults to None.

            exist_verify (bool, optional): 是否有验证码. Defaults to False.
            captcha_type (str, optional): 验证码类型. Defaults to captcha. 
                    滑块传入cap开头, 图片传入kap开头 与教务系统的url地址对应, 默认识别滑块验证码.
            retry (int, optional): 登录重试次数. Defaults to 10.

            lan_host (str, optional): 内网主机地址. Defaults to None.
            lan_port (int, optional): 内网主机端口号. Defaults to 80.
            timeout (int, optional): 请求超时时间. Defaults to 10.
            login_url_path ([type], optional): 登录地址. Defaults to None.
            url_endpoints ([dict], optional): 地址列表. Defaults to None.
        """
        school = {
            "name": name,
            "exist_verify": exist_verify,
            "captcha_type": captcha_type,
            "retry": retry,
            "lan_host": lan_host,
            "lan_port": lan_port,
            "timeout": timeout,
            "login_url_path": login_url_path,
            "url_endpoints": url_endpoints or URL_ENDPOINT
        }

        self.base_url = f'https://{host}:{port}' if ssl else f'http://{host}:{port}'
        self.config: dict = school

    def user_login(self, account: str, password: str, **kwargs):
        """用户登录

        Args:
            account (str): 用户账号
            password (str): 用户密码
        """
        user = UserClient(self, account=account, password=password, **kwargs)
        return user.login()

    def init_dev_user(self, cookies: str = None):
        dev_user = UserClient(self, account="dev account",
                              password="dev password")
        return dev_user.get_dev_user(cookies)


class UserClient(BaseUserClient):
    schedule: Schedule = None
    score: Score = None
    info = None

    def __init__(self, school, account, password) -> None:
        """初始化用户类
        用户类继承自学校

        Args:
            school (SchoolClient): 学校实例
            account (str): 账号
            password (str): 密码
        """
        self.account = account
        self.password = password
        self.school = school
        self._csrf = None
        self.t = int(time.time())
        self._image = None

    def login(self):
        """用户登录，通过SchoolClient调用
        """
        user = ZFLogin(user_client=self)
        user.get_login()
        self._http = user._http
        return self


    def init_schedule(self):
        if self.schedule is None:
            self.schedule = Schedule(self)

    def get_schedule(self, year:int, term:int = 1, **kwargs):
        """获取课表"""
        kwargs.setdefault("year", year)
        kwargs.setdefault("term", term)
        if self.schedule is None:
            self.schedule = Schedule(self)
        return self.schedule.get_schedule_dict(**kwargs)

    def get_score(self, year:int, term:int = 1, **kwargs):
        """获取成绩"""
        kwargs.setdefault("year", year)
        kwargs.setdefault("term", term)
        if self.score is None:
            self.score = Score(self)
        return self.score.get_score(**kwargs)

    def get_info(self, **kwargs):
        """获取个人信息"""
        if self.info is None:
            self.info = Info(self)
        return self.info.get_info(**kwargs)

    # dev options
    def get_cookies(self):
        return self._http.cookies

    def set_cookies(self, cookies: str, **kwargs):
        """设置user cookies

        Args:
            cookies (str): Cookies 字符串
        """
        cookies = cookies.strip()
        key, value = cookies.split('=')
        self._http.cookies.set(key, value)

    def get_dev_user(self, cookies: str, **kwargs):
        self._http = requests.Session()
        self.set_cookies(cookies=cookies, **kwargs)
        return self
