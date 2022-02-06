#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
from enum import Enum
from zipfile import ZipFile
from pandas import DataFrame
from typing import Optional, Union
from chardet import detect
from pathlib import Path
import gtfs_kit as gk
import re as regex
import os, shutil, wget, ftplib



'''
AUXILIARY EXCEPTION/ENUM CLASSES
'''
class ExitType(Enum):
    ERROR   = 7899
    WARNING = 7900
    ALL_OK  = 7901
    AEQUAL  = 7902


'''
AUXILIARY FILE FETCHING/HANDLING FUNCTIONS
'''
# compress all files in a directory
def compress(path: str) -> str:
    
    output_filename = str((Path(path)).parent) + "/gtfs_feed"

    shutil.make_archive(output_filename, 'zip', path)

    return output_filename + ".zip"

# convert a file's encoding to utf-8
def convert(srcfile: str) -> None:

    trgfile = srcfile + ".tmp"

    # get file encoding type
    def get_encoding_type(file):
        with open(file, 'rb') as f:
            rawdata = f.read()
        return detect(rawdata)['encoding']

    from_codec = get_encoding_type(srcfile)

    # add try: except block for reliability
    try: 
        with open(srcfile, 'r', encoding=from_codec) as f, open(trgfile, 'w', encoding='utf-8') as e:
            text = f.read()
            if regex.search(r'\x00', text): # throw out the NULL character
                if srcfile == (os.getcwd() + "/public/tmp_in/agency.txt"):
                    text = regex.sub(r'\x00',"https://www.tub.pt", text)
                else:
                    text = regex.sub(r'\x00',"", text)

            e.write(text)

        os.remove(srcfile) # remove old encoding file
        os.rename(trgfile, srcfile) # rename new encoded file
    except UnicodeDecodeError:
        print('Decode Error')
    except UnicodeEncodeError:
        print('Encode Error')

# convert all files in a given diretory to utf-8
def unicodify(srcdir: str) -> None:

    srcdir = srcdir if srcdir[-1] == "/" else srcdir + "/"

    files = os.listdir(srcdir)
    
    for f in files:
        if f[0:len(f) - 4] in gk.constants.FEED_ATTRS:
            convert(srcdir + f)
    
# fetch the GTFS file from a given url through wget
def fetch(src: str, tmp_out = os.getcwd() + "/public/tmp_in") -> str:

    if not os.path.isdir(tmp_out):
        os.mkdir(tmp_out)

    ff = wget.download(src, out=tmp_out)

    if ff is None:
        os.rmdir(tmp_out)
        raise FileNotFoundError()

    with ZipFile(ff, 'r') as zip:
        zip.extractall(tmp_out)

    os.remove(ff)

    print()

    return tmp_out


'''
AUXILIARY DATE STORING/READING FUNCTIONS
'''

# get expiration date
def get_expiration_date(path: Optional[str] = os.getcwd() + "/public/.last_date") -> Union[datetime, None]:
    if os.path.exists(path):
        with open(path, "r") as f:
            return datetime.fromisoformat(f.readline()) + relativedelta(months=+6)
    else:
        return None


# store the last date of update
def store_last_update(date: datetime, path: Optional[str] = os.getcwd() + "/public/.last_date") -> None:
    with open(path, "w") as f:
        f.write(date.isoformat())

# read the last date of update
def read_last_update(path: Optional[str] = os.getcwd() + "/public/.last_date") -> Union[datetime, None]:
    if os.path.exists(path):
        with open(path, "r") as f:
            return datetime.fromisoformat(f.readline())
    else:
        return None

# check if a date is close to the expiration date of a gtfs feed
def is_close_to_expiration(arg_date: datetime) -> bool:
    last_update = read_last_update()

    if not last_update:
        return False #if there has never been an update, we aren't close to its expiration

    expiration = last_update + relativedelta(months=+6)

    return abs((expiration - arg_date).days) <= 20


'''
CALENDAR DATE UPDATE FUNCTIONS
'''
# get the weekdays for each day
def get_weekdays(dates: list) -> list:
    weekdays_l = []
    for day in dates:
        dday =  datetime.strptime(day, "%Y%m%d")
        if dday.weekday() not in weekdays_l:
            weekdays_l.append(dday.weekday())

    return weekdays_l

# generate service_dates from start, for n_months months
def generate_service_days_from(start_day: datetime, weekdays: list, n_months: int) -> list:
    start = start_day
    end = start + relativedelta(months=+n_months)
    service_days = []
    while start != end:
        if start.weekday() in weekdays:
            service_days.append(start.strftime("%Y%m%d"))
        start = start + relativedelta(days=1)

    return service_days
        
# set the dates for the next 6 months
def set_dates (current_dates: dict) -> dict:
    today = datetime.today()
    all_service_days = {}

    for service_id, dates in current_dates.items():
        weekdays = get_weekdays(dates)
        service_days = generate_service_days_from(today, weekdays, 6)
        all_service_days[service_id] = service_days

    return all_service_days

# write the new service days
def write_new_service_days(fp, current_dates: dict, service_id_exceptions: dict, header: str) -> None:
    new_dates = set_dates(current_dates)

    fp.write(header)

    for service_id, dates in new_dates.items():
        for sday in dates:
            fp.write(f"{service_id},{sday},{service_id_exceptions[service_id]}")
    
# get the base dates for the service days
def read_old_service_days(fp) -> tuple:
    service_id_dates = {}
    service_id_exceptions = {}
    is_first_line = True


    for line in fp:
        if is_first_line:
            is_first_line = not is_first_line
            first_line = line
        else:
            entries = line.split(r",")
            service_id = entries[0]
            service_date = entries[1]
            service_exception = entries[2]

            if not service_id_dates.get(service_id):
                service_id_dates[service_id] = []
            if service_date not in service_id_dates[service_id]:
                service_id_dates[service_id].append(service_date)

            service_id_exceptions[service_id] = service_exception

    return first_line, service_id_dates, service_id_exceptions

# sets the calendar dates in calendar_dates to a date six months in the future
def set_calendar_dates(cdsrc: str = os.getcwd() + "/public/tmp_in/calendar_dates.txt") -> None:
    if os.path.exists(cdsrc):
        tmpfile = cdsrc + ".tmp"
        with open(cdsrc, "r") as source, open(tmpfile, "w") as dest:
            header, service_id_dates, exceptions = read_old_service_days(source)
            write_new_service_days(dest, service_id_dates, exceptions, header)

        os.remove(cdsrc) # remove old encoding file
        os.rename(tmpfile, cdsrc) # rename new encoded file

        
'''
GTFS HANDLING FUNCTIONS
'''
# function to check if two gtfs feed are the same, or "almost equal"
# don't question the name, embrace it
def sneed(feed: gk.feed.Feed, seed: gk.feed.Feed) -> bool:
    from gtfs_kit.helpers import almost_equal

    flag = True

    if not feed and not seed:
        return True
    
    if feed and seed:
        if feed.agency is not None and seed.agency is not None:
            flag = flag and almost_equal(feed.agency, seed.agency)

        if feed.stops is not None and seed.stops is not None:
            flag = flag and almost_equal(feed.stops, seed.stops)

        if feed.routes is not None and seed.routes is not None:
            flag = flag and almost_equal(feed.routes, seed.routes)

        if feed.trips is not None and seed.trips is not None:
            flag = flag and almost_equal(feed.trips, seed.trips)

        if feed.stop_times is not None and seed.stop_times is not None:
            flag = flag and almost_equal(feed.stop_times, seed.stop_times)

        if feed.calendar is not None and seed.calendar is not None:
            flag = flag and almost_equal(feed.calendar, seed.calendar)

        if feed.calendar_dates is not None and seed.calendar_dates is not None:
            flag = flag and almost_equal(feed.calendar_dates, seed.calendar_dates)

        if feed.fare_attributes is not None and seed.fare_attributes is not None:
            flag = flag and almost_equal(feed.fare_attributes, seed.fare_attributes)

        if feed.fare_rules is not None and seed.fare_rules is not None:
            flag = flag and almost_equal(feed.fare_rules, seed.fare_rules)

        if feed.shapes is not None and seed.shapes is not None:
            flag = flag and almost_equal(feed.shapes, seed.shapes)

        if feed.frequencies is not None and seed.frequencies is not None:
            flag = flag and almost_equal(feed.frequencies, seed.frequencies)

        if feed.transfers is not None and seed.transfers is not None:
            flag = flag and almost_equal(feed.transfers, seed.transfers)

        if feed.feed_info is not None and seed.feed_info is not None:
            flag = flag and almost_equal(feed.feed_info, seed.feed_info)


        return flag

    else: 
        return False

# validate a Static GTFS Feed from a given directory.
def validate_gtfs(dir: str) -> tuple:

    src_dir = dir

    exit_type: ExitType

    last_fetch_dir = os.getcwd() + "/public/tmp_in" # always the same
    last_feed: gk.feed.Feed = None

    # store the original feed first, if it existed
    if os.path.isdir(last_fetch_dir) and os.listdir(last_fetch_dir):
        # set the calendar date on the last feed in case it isn't right (in order to properly compare it with the new feed)
        set_calendar_dates(src_dir + "/calendar_dates.txt")
        # we don't need the try/catch block because it was already done the last time
        last_feed = gk.read_feed(last_fetch_dir, dist_units='km')

    # if the directory isn't found, we assume it's from an internet server
    # we must fetch it
    if not os.path.isdir(src_dir):
        try:
            src_dir = fetch(src_dir, tmp_out=last_fetch_dir)

        except FileNotFoundError as e:

            print("\n\n-Unable to get file!")

            raise FileNotFoundError(e)

    feed: gk.feed.Feed

    # set the new feeds's calendar dates before validating it (or else the feeds will be different without necessity)
    set_calendar_dates(src_dir + "/calendar_dates.txt")

    # get the gtfs feed
    # it's common for the feed to have encoding errors, we fix them quickly and without warning
    try:
        feed = gk.read_feed(src_dir, dist_units='km')

    except UnicodeDecodeError:

        unicodify(src_dir)

        print("\n- Found Encoding Problems. They have been corrected, no further action is required.")

        feed = None

        unicodify(src_dir)

        feed = gk.read_feed(src_dir, dist_units='km')

    # validate the feed
    feed_val = feed.validate(include_warnings = True)
    # use a secondary validation for checking whether only warnings exist or not
    feed_val_error_only = feed.validate(include_warnings = False)

    # get the exit type
    if type(feed_val) is DataFrame:
        if len(feed_val_error_only) == 0:
            exit_type = ExitType.WARNING
        else:
            exit_type = ExitType.ERROR
    elif type(feed_val) is list:
        exit_type = ExitType.ALL_OK

    # check whether the newly fetched feed is the same as the one from the last checkup
    if (last_feed is not None) and (exit_type != ExitType.ERROR) and sneed(feed, last_feed):
        exit_type = ExitType.AEQUAL

    # return the local source directory path, the feed validation results and the exit type
    return src_dir, feed_val, exit_type


'''
FTP SERVER INTERACTION FUNCTIONS
'''
# deposit resulting feed in FTP server
def deposit_ftp(src: str, host: str, user: Optional[str] = "", password: Optional[str] = "") -> None:
    
    zip_file = compress(src)

    ftp = ftplib.FTP(host=host)

    ftp.login(user,password)

    zp = open(zip_file, "rb")

    remote_zip_file = "gtfs_feed.zip"
    
    ftp.storbinary("STOR " + remote_zip_file, zp)

    ftp.quit()



    


