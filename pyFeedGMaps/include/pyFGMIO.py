from datetime import datetime, timedelta
import os, json, re, ftplib, sys, getpass, ssl, smtplib

"""
AUXILIARY EXCEPTION CLASSES
"""
class MissingParameter(Exception):
    def __init__(self, msg):
        self.message = msg
        self.name = "Missing Parameter"

class ImproperEmailFormat(Exception):
    def __init__(self, msg):
        self.message = msg
        self.name = "Improper Email Format"

class VerboseTypeError(TypeError):
    def __init__(self, msg):
        self.message = msg
        self.name = "Type Error"

class ImproperFileFormatError(Exception):
    def __init__(self, msg):
        self.message = msg
        self.name = "Improper File Format Error"


# auxiliary function to clear the screen on windows or UNIX
def clear_screen() -> None:
    if sys.platform == "win32":
        os.system("cls")
    else:
        os.system("clear")

# print a help guide
def print_help() -> None:
    clear_screen()


    print()
    print("----- Welcome to GTFS_Val v.1.0 -----")
    print('''
This software is used to periodically check on a server that provides a static GTFS source, validate it, and store it in an FTP server in order to facilitate communication with Google Maps.

Usage:
    python3 Main.py -src <config_file>

The argument src is the path to a configuration file. This file should be a JSON file, and follow the structure provided in the example "example_config_file.json". All fields are MANDATORY, and follow the following structure:

{
    file_source : STRING,
    notification_receivers : [STRING],
    notification_sender: STRING,
    update_frequency: INTEGER,
    starting_date: STRING,
    ftp_host: STRING,
    ftp_user: STRING
}

The file source can be a local or remote one. The update frequency is the number of days between checkups to the provider in <file_source>. These check ups start at <starting_date>, which should follow ISO format (YYYY-MM-DD) exactly, and will be executed at 23:59h. If the date is before the current day, updates start on the same day.

Once the configuration file is read and validated, two passwords will be requested: one for the notification sender email and one for the FTP user. Only after inputing both will the software start check ups. 

If any fields are changed, software must be restarted for the changes to take effect. If a force quit is performed during the process of validating a GTFS feed, it is recomended you run "python3 Main.py -clean" in order to erase all files, as they may be corrupted.
    
    
''')

# delete files in tmp_in
def clean_sources() -> None:
    source = os.getcwd() + "/public"

    if os.path.exists(source + "/gtfs_feed.zip"):
        os.remove(source + "/gtfs_feed.zip")

    if os.path.exists(source + "/verbose_error_report.html"):
        os.remove(source + "/verbose_error_report.html")

    if os.path.exists(source + "/report.txt"):
        os.remove(source + "/report.txt")

    source += "/tmp_in"

    if os.path.exists(source):
        for file in os.listdir(source):
            os.remove(source + "/" + file)
        os.rmdir(source)
    

# parse the configuration file
def parse_config(src: str) -> dict:
    if not os.path.exists(src):
        raise FileNotFoundError("Unable to locate configuration file")

    try:
        with open(src) as config_file:
            config = json.load(config_file)

    except json.decoder.JSONDecodeError:
        raise ImproperFileFormatError("Configuration file is misformatted")

    return config




# check base string
def check_base_string(config: dict, arg: str) -> None:
    if not config.get(arg):
        raise MissingParameter(f"Config file missing {arg}")
    if type(config[arg]) is not str:
        raise VerboseTypeError(f"{arg} must be String")

# check base integer
def check_base_integer(config: dict, arg: str) -> None:
    if not config.get(arg):
        raise MissingParameter(f"Config file missing {arg}")
    if type(config[arg]) is not int:
        raise VerboseTypeError(f"{arg} must be Integer")

# check email string
def check_email_string(config: dict, arg: str) -> None:
    email_regex = r"[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z])+"

    if not config.get(arg):
        raise MissingParameter("Config file missing notification_sender")
    if type(config[arg]) is not str:
        raise VerboseTypeError("{arg} must be String")
    elif not re.match(email_regex, config[arg]):
        ns = config[arg]
        raise ImproperEmailFormat(f"{ns}: not a valid email")

# check email list
def check_email_list(config: dict, arg: str) -> None:
    email_regex = r"[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z])+"
    if not config.get(arg):
        raise MissingParameter(f"Config file missing {arg}")
    if type(config[arg]) is not list:
        raise VerboseTypeError(f"{arg} must be a list")
    else:
        for email in config[arg]:
            if type(email) is not str:
                raise VerboseTypeError(f"{email}: not a String")
            elif not re.match(email_regex, email):
                raise ImproperEmailFormat(f"{email}: not a valid email")

# validate a configuration map
def validate_config(config: dict) -> dict:

    iso_date_regex = r"[0-9][0-9][0-9][0-9]\-(0[1-9]|(1[0-2]))\-(0[1-9]|([1-2][0-9])|(30)|(31))"

    # check file_source
    check_base_string(config, "file_source")

    # check notification receivers
    check_email_list(config, "notification_receivers")

    # check notification_sender
    check_email_string(config, "notification_sender")

    # check update_frequency
    check_base_integer(config, "update_frequency")

    # check starting_date
    if not config.get("starting_date"):
        raise MissingParameter("Config file missing starting_date")
    if type(config["starting_date"]) is not str or not re.match(iso_date_regex, config["starting_date"]):
        raise VerboseTypeError("starting_date must be a String of form yyyy-mm-dd")

    # if starting date is before today, set it to today
    sd = datetime.fromisoformat(config["starting_date"])
    today = datetime.today()

    if sd.date() < today.date():
        config["starting_date"] = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    
    
    # check ftp_host
    check_base_string(config, "ftp_host")

    # check ftp_user
    check_base_string(config, "ftp_user")

    return config





# ask for the FTP server password
def request_ftp_password(ftp_user: str, ftp_host: str) -> str:
    ftp_password = getpass.getpass(f"Please input password for the FTP user {ftp_user}: ")
    try:
        ftp = ftplib.FTP(ftp_host)
        ftp.login(user=ftp_user, passwd=ftp_password)
        ftp.quit()

        print(f"Login to FTP Server {ftp_host} successful")

        return ftp_password

    except ftplib.error_perm:
        print("FPT login authentication failed")
        exit(0)

# ask for email password
def request_email_password(email: str,) -> str:

    email_password = getpass.getpass(f"Please input password for {email}: ")
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(email, email_password)
        
        print(f"Login to GMail account successful")

        return email_password

    except smtplib.SMTPAuthenticationError:
        print("FPT login authentication failed")
        exit(0)

# ask for FTP server and email passwords
def request_passwords(email: str, ftp_user: str, ftp_host: str) -> tuple:
    return request_email_password(email), request_ftp_password(ftp_user, ftp_host)

    




# parse program argumets
def parse_args(args: list) -> str:

    config_source: str

    if len(args) == 1 and args[0] == "-h":
        print_help()
        exit(0)

    elif len(args) == 1 and args[0] == "-clean":
        clean_sources()
        exit(0)

    elif len(args) > 1 and args[0] == "-src":
        config_source = args[1]

    else:
        print("Invalid or insufficient arguments! Type python3 Main.py -h for help.")
        exit(0)

    return config_source
        

    