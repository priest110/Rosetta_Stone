#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pandas import DataFrame
from enum import Enum
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import timedelta, date, datetime
from typing import Union
from datetime import datetime
import os



class EmailType(Enum):
    ERROR        = 8991
    OK           = 8992
    NO_CHANGE    = 8993
    EXPIRATION   = 8994
    NO_FILES     = 8995
    WARNING_ONLY = 8996
    ERROR_CTE    = 8997


def notify_errors(
    payload: Union[str, list, DataFrame, None],
    email_orig: str = None,
    email_dest: list = None,
    password: str = None,
    subject: str = None
):

    tday = datetime.today().strftime("%Y-%m-%d")

    message = MIMEMultipart("alternative")
    message["Subject"] = f"[GTFS Val] {tday} Validation Report"
    message["From"] = email_orig

    html_string_start = '''\
    <html>
        <head>
            <title>Report Title</title>
        </head>
      <body>
        <table  border = "1" width = "700">
    '''
    html_string_end = '''
            </table>
        </body>
    </html>
    '''

    # Escrita do HTML com o report
    with open('public/verbose_error_report.html', 'w') as f:
        f.write(html_string_start)
        for header in payload.columns.values:
            f.write('<th>'+str(header)+'</th>\n')
        for i in range(len(payload)):
            f.write('<tr>')
            for col in payload.columns:
                value = payload.iloc[i][col]    
                f.write('<td>'+str(value)+'</td>\n')
            f.write('</tr>\n')
        f.write(html_string_end)

    with open('public/report.txt','w') as ff:
        error_n = len(payload)
        warnings = [(payload.message[w], payload.table[w],payload.rows[w]) 
                    for w in range(0, error_n) if payload.type[w] == "warning"]
        errors = [(payload.message[w], payload.table[w],payload.rows[w]) 
                    for w in range(0, error_n) if payload.type[w] == "error"]

        ff.write("--- Errors ---\n")
        for a in range(0,len(errors)):
            ff.write("Description:  " + str(errors[a][0]) + "\n")
            ff.write("Table:           " + str(errors[a][1]) + "\n")
            if (len(errors[a][2])) < 6:
                if (len(errors[a][2]) > 0):
                    ff.write("Entry:        " + str(errors[a][2]) + "\n")
            else:
                ff.write("Entry:           " + str(errors[a][2][:6]) + " and " + str(len(str(errors[a][2])) - 6) + " more\n")
            ff.write("---           \n")

        ff.write("\n\n--- Warnings ---\n")
        for a in range(0,len(warnings)):
            ff.write("Description:  " + str(warnings[a][0]) + "\n")
            ff.write("Table:           " + str(warnings[a][1]) + "\n")
            if (len(warnings[a][2])) < 6:
                if (len(warnings[a][2]) > 0):
                    ff.write("Entry:        " + str(warnings[a][2]) + "\n")
            else:
                ff.write("Entry:           " + str(warnings[a][2][:6]) + " and " + str(len(str(warnings[a][2])) - 6) + " more\n")
            ff.write("---           \n")
                
    report_file = (open("public/report.txt","r")).read()


    # Mensagem do email
    text1 = f"""
Greetings,
\n
The GTFS feed provided has fatal errors which prevent it from being submitted.
\n
{report_file}
Attached you will find the detailed and verbose error report."""


#   Anexo do email
    file_name = "public/verbose_error_report.html"
    attachment = open("public/verbose_error_report.html","rb")
    p = MIMEBase('application', 'octet-stream')
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename= " + file_name)
    message.attach(p)
    
    message.attach(MIMEText(text1, "plain"))
    send_email(message, email_orig, email_dest, password)


def notify_ok(
    payload: Union[str, list, DataFrame, None] = None,
    email_orig: str = None,
    email_dest: str = None,
    password: str = None,
    subject: str = None
):

    tday = datetime.today().strftime("%Y-%m-%d")

    message = MIMEMultipart("alternative")
    message["Subject"] = f"[GTFS Val] {tday} Validation Report"
    message["From"] = email_orig

    text2 = """\
Greetings,
\n
The file provided presents no fatal errors and was submitted.
"""

    message.attach(MIMEText(text2, "plain"))
    send_email(message, email_orig, email_dest, password)

def notify_no_change(
    payload: Union[str, list, DataFrame, None] = None,
    email_orig: str = None,
    email_dest: str = None,
    password: str = None,
    subject: str = None
):

    tday = datetime.today().strftime("%Y-%m-%d")

    message = MIMEMultipart("alternative")
    message["Subject"] = f"[GTFS Val] {tday} Validation Report"
    message["From"] = email_orig

    text3 = """\
Greetings,
\n
The attempted submission in the current period is the same as the last period's and, as such, won't be submitted.
"""

    message.attach(MIMEText(text3, "plain")) 
    send_email(message, email_orig, email_dest, password)


def notify_expiration(
    payload = None,
    email_orig: str = None,
    email_dest: str = None,
    password: str = None,
    subject: str = None,
    expiration: datetime = None
):
    validade = expiration.strftime("%Y-%m-%d")

    tday = datetime.today().strftime("%Y-%m-%d")

    message = MIMEMultipart("alternative")
    message["Subject"] = f"[GTFS Val] {tday} Validation Report"
    message["From"] = email_orig
    
    text4 = f"""\
Greetings,
\n
The file provided presents no fatal errors and was submitted. It was similar to the last one submitted, by the expiration date ({validade}) was too close.

"""
        
    message.attach(MIMEText(text4, "plain"))
    send_email(message, email_orig, email_dest, password)

def notify_file_not_found(
    payload: Union[str, list, DataFrame, None]= None,
    email_orig: str = None,
    email_dest: str = None,
    password: str = None,
    subject: str = None
):
    tday = datetime.today().strftime("%Y-%m-%d")

    message = MIMEMultipart("alternative")
    message["Subject"] = f"[GTFS Val] {tday} Validation Report"
    message["From"] = email_orig

    text5 = """\
Greetings,
\n
The file source provided in the configuration document cannot be accessed. Please make it available before the next update, or stop thprogram, update the configuration file and start over.
        """
    
    message.attach(MIMEText(text5, "plain"))
    send_email(message, email_orig, email_dest, password)

def notify_error_cte(
    payload: Union[str, list, DataFrame, None]= None,
    email_orig: str = None,
    email_dest: str = None,
    password: str = None,
    subject: str = None,
    expiration: datetime = None
):
    tday = datetime.today().strftime("%Y-%m-%d")

    error_payload = payload

    message = MIMEMultipart("alternative")
    message["Subject"] = f"[GTFS Val] {tday} Validation Report"
    message["From"] = email_orig

    html_string_start = '''\
    <html>
        <head>
            <title>Report Title</title>
        </head>
      <body>
        <table  border = "1" width = "700">
    '''
    html_string_end = '''
            </table>
        </body>
    </html>
    '''

    # Escrita do HTML com o report
    with open('public/verbose_error_report.html', 'w') as f:
        f.write(html_string_start)
        for header in error_payload.columns.values:
            f.write('<th>'+str(header)+'</th>\n')
        for i in range(len(error_payload)):
            f.write('<tr>')
            for col in error_payload.columns:
                value = error_payload.iloc[i][col]    
                f.write('<td>'+str(value)+'</td>\n')
            f.write('</tr>\n')
        f.write(html_string_end)

    with open('public/report.txt','w') as ff:
        error_n = len(error_payload)
        warnings = [(error_payload.message[w], error_payload.table[w],error_payload.rows[w]) 
                    for w in range(0, error_n) if error_payload.type[w] == "warning"]
        errors = [(error_payload.message[w], error_payload.table[w],error_payload.rows[w]) 
                    for w in range(0, error_n) if error_payload.type[w] == "error"]

        ff.write("--- Errors ---\n")
        for a in range(0,len(errors)):
            ff.write("Description:  " + str(errors[a][0]) + "\n")
            ff.write("Table:           " + str(errors[a][1]) + "\n")
            if (len(errors[a][2])) < 6:
                if (len(errors[a][2]) > 0):
                    ff.write("Entry:        " + str(errors[a][2]) + "\n")
            else:
                ff.write("Entry:           " + str(errors[a][2][:6]) + " and " + str(len(str(errors[a][2])) - 6) + " more\n")
            ff.write("           ---           \n")

        ff.write("\n\n--- Warnings ---\n")
        for a in range(0,len(warnings)):
            ff.write("Description:  " + str(warnings[a][0]) + "\n")
            ff.write("Table:           " + str(warnings[a][1]) + "\n")
            if (len(warnings[a][2])) < 6:
                if (len(warnings[a][2]) > 0):
                    ff.write("Entry:        " + str(warnings[a][2]) + "\n")
            else:
                ff.write("Entry:           " + str(warnings[a][2][:6]) + " and " + str(len(str(warnings[a][2])) - 6) + " more\n")
            ff.write("---           \n")
                
    report_file = (open("public/report.txt","r")).read()


    # Mensagem do email
    text1 = f"""\
Greetings,
\n
The GTFS feed has come with some errors. Please fix them before the next update.\n
Be warned that the last update has an expiration date of {expiration.strftime("%Y-%m-%d")}.

{report_file}

Attached you will find a more detailed report. """


    # Anexo do email
    file_name = "public/verbose_error_report.html"
    attachment = open("public/verbose_error_report.html","rb")
    p = MIMEBase('application', 'octet-stream')
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename= %s" % file_name)
    message.attach(p)
    
    message.attach(MIMEText(text1, "plain"))
    send_email(message, email_orig, email_dest, password)


def notify_warnings(
    payload: Union[str, list, DataFrame, None]= None,
    email_orig: str = None,
    email_dest: str = None,
    password: str = None,
    subject: str = None
):
    tday = datetime.today().strftime("%Y-%m-%d")

    message = MIMEMultipart("alternative")
    message["Subject"] = f"[GTFS Val] {tday} Validation Report"
    message["From"] = email_orig

    html_string_start = '''\
    <html>
        <head>
            <title>Report Title</title>
        </head>
      <body>
        <table  border = "1" width = "700">
    '''
    html_string_end = '''
            </table>
        </body>
    </html>
    '''

    # Escrita do HTML com o report
    with open('public/verbose_error_report.html', 'w') as f:
        f.write(html_string_start)
        for header in payload.columns.values:
            f.write('<th>'+str(header)+'</th>\n')
        for i in range(len(payload)):
            f.write('<tr>')
            for col in payload.columns:
                value = payload.iloc[i][col]    
                f.write('<td>'+str(value)+'</td>\n')
            f.write('</tr>\n')
        f.write(html_string_end)

    with open('public/report.txt','w') as ff:
        error_n = len(payload)
        warnings = [(payload.message[w], payload.table[w],payload.rows[w]) 
                    for w in range(0, error_n) if payload.type[w] == "warning"]


        ff.write("--- Warnings ---\n")
        for a in range(0,len(warnings)):
            ff.write("Description:  " + str(warnings[a][0]) + "\n")
            ff.write("Table:           " + str(warnings[a][1]) + "\n")
            if (len(warnings[a][2])) < 6:
                if (len(warnings[a][2]) > 0):
                    ff.write("Entry:        " + str(warnings[a][2]) + "\n")
            else:
                ff.write("Entry:           " + str(warnings[a][2][:6]) + " and " + str(len(str(warnings[a][2])) - 6) + " more\n")
            ff.write("---           \n")
                
    report_file = (open("public/report.txt","r")).read()


    # Mensagem do email
    text1 = f"""\
Greetings,
\n
The GTFS feed provided has no fatal errors, but does, however, contain several warnings.
\n
{report_file}
Attached you will find the detailed and verbose warning report."""


    # Anexo do email
    file_name = "public/verbose_error_report.html"
    attachment = open("public/verbose_error_report.html","rb")
    p = MIMEBase('application', 'octet-stream')
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename= %s" % file_name)
    message.attach(p)
    
    message.attach(MIMEText(text1, "plain"))
    send_email(message, email_orig, email_dest, password)



# function to send an email
def send_email(message, email_orig: str, email_dest: list, password: str):
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(email_orig, password)
        for receiver in email_dest:
            server.sendmail(email_dest, receiver, message.as_string())





def notify(
    msg_type: EmailType,
    payload: Union[str, list, DataFrame, None] = None,
    email_orig: str = None,
    email_dest: list = None,
    password: str = None,
    subject: str = None,
    expiration: datetime = None
) -> None:

    if msg_type == EmailType.ERROR:
        notify_errors(payload, email_orig = email_orig, email_dest = email_dest, password = password, subject = subject)

    elif msg_type == EmailType.EXPIRATION:
        notify_expiration(payload, email_orig = email_orig, email_dest = email_dest, password = password, subject = subject, expiration = expiration)

    elif msg_type == EmailType.NO_CHANGE:
        notify_no_change(payload, email_orig = email_orig, email_dest = email_dest, password = password, subject = subject)
    
    elif msg_type == EmailType.NO_FILES:
        notify_file_not_found(payload, email_orig = email_orig, email_dest = email_dest, password = password, subject = subject)

    elif msg_type == EmailType.OK:
        notify_ok(payload, email_orig = email_orig, email_dest = email_dest, password = password, subject = subject)

    elif msg_type == EmailType.ERROR_CTE:
        notify_error_cte(payload, email_orig = email_orig, email_dest = email_dest, password = password, subject = subject, expiration = expiration)

    elif msg_type == EmailType.WARNING_ONLY:
        notify_warnings(payload, email_orig = email_orig, email_dest = email_dest, password = password, subject = subject)

    if os.path.exists(os.getcwd() + "/public/report.txt"):
        os.remove(os.getcwd() + "/public/report.txt")

    if os.path.exists(os.getcwd() + "/public/verbose_error_report.html"):
        os.remove(os.getcwd() + "/public/verbose_error_report.html")

