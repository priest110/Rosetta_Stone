#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import schedule
from typing import Callable
from datetime import datetime, timedelta
import time

STARTING_HOUR = "23:59"

class ScheduledJob:

    __start: datetime
    __freq:  int
    __job:   Callable

    def __init__(self, start: datetime, freq: int, job: Callable):

        date_str = (start - timedelta(days=1)).strftime("%Y%m%d")
        date_str += ":" + STARTING_HOUR
        self.__start = datetime.strptime(date_str, "%Y%m%d:%H:%M")
        self.__freq  = freq
        self.__job   = job

    def run_forever(self):

        now = datetime.now()

        delay = int((self.__start - now).total_seconds())

        time.sleep(delay)

        self.__job()

        schedule.clear()
        schedule.every(self.__freq).days.at(STARTING_HOUR).do(self.__job)
        while True:
            schedule.run_pending()

    def stop_run(self):
        return schedule.CancelJob
