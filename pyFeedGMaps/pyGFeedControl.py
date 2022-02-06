from include.pyFGMIO import ImproperEmailFormat, ImproperFileFormatError, MissingParameter, VerboseTypeError
from include.pyFGMIO import parse_args, validate_config, parse_config, request_passwords
from include.pyFeedGMaps import ExitType, set_calendar_dates
from include.pyFeedGMaps import is_close_to_expiration, deposit_ftp, store_last_update, validate_gtfs, get_expiration_date
from include.pyEmail import EmailType, notify
from include.pyScheduler import ScheduledJob

from datetime import datetime
import sys, signal

# set keyboard interrupt to not be awful
def gracious_decay() -> None:
    def int_handle(signum,frame):
        print("Received signal to quit")
        exit(0)

    signal.signal(signal.SIGINT, int_handle)

# read program arguments
def get_args() -> str:
    return parse_args(sys.argv[1:])

# read and parse configuration file and ask for passwords
def startup(config_src: str) -> dict:
    config: dict 

    # get the config file
    try:
        config = validate_config(parse_config(config_src))
    
    except FileNotFoundError:
        print(f"{config_src}: File not found.")
        exit(0)

    except (MissingParameter, VerboseTypeError, ImproperEmailFormat, ImproperFileFormatError) as ex:
        print(f"{ex.name}: {ex.message}")
        exit(0)

    email_pw, ftp_pw = request_passwords(
        config["notification_sender"],
        config["ftp_user"],
        config["ftp_host"]
        )

    first_update = config["starting_date"]

    print(f"Everything has been set up successfully. Do not exit program. First check-up scheduled for {first_update}, at 23:59h.")

    config["email_password"] = email_pw
    config["ftp_password"] = ftp_pw

    return config

# schedule and execute main loop
def main_loop(config: dict) -> None:

    file_src  = config["file_source"]
    file_dep  = config["ftp_host"]
    ftp_user  = config["ftp_user"]
    ftp_pw    = config["ftp_password"]
    sender    = config["notification_sender"]
    receivers = config["notification_receivers"]
    email_pw  = config["email_password"]

    # main job to be exectued every X days
    def basic_job():
        try:
            today = datetime.now()

            print(f"\n[{today}] Starting retrieval and validation")

            # fetch and validate the GTFS file
            local_src, feed_val, out_flag = validate_gtfs(file_src)

            # Something was amiss in the file, we don't send it, but we do send an ERROR notification
            # UNLESS: expiration date is almost due, in which case we notify with a special message
            if out_flag == ExitType.ERROR:

                # if it is close to expiration, notify of ERROR CLOSE TO EXPIRATION
                if is_close_to_expiration(today):
                    notify(EmailType.ERROR_CTE, payload=feed_val, email_dest=receivers, email_orig=sender, password=email_pw, expiration=get_expiration_date())
                # else, just notify of ERROR
                else:
                    notify(EmailType.ERROR, payload=feed_val, email_dest=receivers, email_orig=sender, password=email_pw)
                    

            # There were some problems (warnings), but they are acceptable. We send a notification and the feed
            elif out_flag == ExitType.WARNING:
                # send the file
                deposit_ftp(local_src, file_dep, user=ftp_user, password=ftp_pw)
                # update the last update date
                store_last_update(today)
                # notify with OK message
                notify(EmailType.WARNING_ONLY, payload=feed_val, email_dest=receivers, email_orig=sender, password=email_pw)

            # Everything was OK, we can send the file and an OK notification
            elif out_flag == ExitType.ALL_OK:
                # send the file
                deposit_ftp(local_src, file_dep, user=ftp_user, password=ftp_pw)
                # update the last update date
                store_last_update(today)
                # notify with OK message
                notify(EmailType.OK, email_dest=receivers, email_orig=sender, password=email_pw)
    
            # if the source is accpeptable but the GTFS file is the same as the one from 15 days ago, we don't send, and notify
            # UNLESS: expiration date is almost due, in which case we send and notify
            elif out_flag == ExitType.AEQUAL:
                # if it is close to the expiration date, then send it anyway, notify CLOSE TO EXPIRATION
                if is_close_to_expiration(today):
                    # send the file
                    deposit_ftp(local_src, file_dep, user=ftp_user, password=ftp_pw)
                    # update the last update date
                    store_last_update(today)
                    # notify with OK message
                    notify(EmailType.EXPIRATION, payload=None,email_dest=receivers, email_orig=sender, password=email_pw, expiration=get_expiration_date())
                # if it isn't, dont send and notify with NO CHANGE
                else:
                    notify(EmailType.NO_CHANGE, email_dest=receivers, email_orig=sender, password=email_pw)

        # if the source isn't acceptable, the user is notified and the program is closed
        # it is assumed this happens only when the server goes down or something
        except FileNotFoundError:
            notify(EmailType.NO_FILES, payload=feed_val, email_dest=receivers, email_orig=sender, password=email_pw)
            exit(0)

    starting_day = datetime.fromisoformat(config["starting_date"])

    sj = ScheduledJob(freq  = config["update_frequency"],
                      start = starting_day,
                      job   = basic_job)

    sj.run_forever()