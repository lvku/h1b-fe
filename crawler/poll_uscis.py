# -*- coding: utf-8 -*
## @author: colin
## @date: 2016-11-30
## @filename: poll_uscis.py
from pyquery import PyQuery as pq
import requests
import smtplib
import os
import sys
import os.path
import re
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.utils import COMMASPACE, formatdate
from email import Encoders
from optparse import OptionParser
from datetime import datetime, date
import sqlite3
import time
import calendar
import setting

DATABASE=setting.DATABASE

STATUS_OK = 0
STATUS_ERROR = -1
FILENAME_LASTSTATUS = os.path.join(sys.path[0], "LAST_STATUS_{0}.txt")

# ----------------- SETTINGS -------------------
# set up your email sender here
# example settings: (if you use gmail)
# email: myname@gmail.com
# password: xxxx
# smtpserver: smtp.gmail.com:587
EMAIL_NOTICE_SENDER = setting.EMAIL_NOTICE_SENDER


def poll_optstatus(casenumber):
    """
    poll USCIS case status given receipt number (casenumber)
    Args:
        param1: casenumber the case receipt number

    Returns:
        a tuple (status, details) containing status and detailed info
    Raise:
        error:
    """
    headers = {
        'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language':
        'en-US, en; q=0.8, zh-Hans-CN; q=0.5, zh-Hans; q=0.3',
        'Cache-Control': 'no-cache',
        'Connection': 'Keep-Alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'egov.uscis.gov',
        'Referer': 'https://egov.uscis.gov/casestatus/mycasestatus.do',
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586'
    }
    url = "https://egov.uscis.gov/casestatus/mycasestatus.do"
    data = {"appReceiptNum": casenumber, 'caseStatusSearchBtn': 'CHECK+STATUS'}

    res = requests.post(url, data=data, headers=headers)
    doc = pq(res.text)
    status = doc('h1').text()
    code = STATUS_OK if status else STATUS_ERROR
    details = doc('.text-center p').text()
    return (code, status, details)


def send_mail(sentfrom,
              to,
              subject="nil",
              text="",
              files=[],
              server=EMAIL_NOTICE_SENDER['smtpserver'],
              user=EMAIL_NOTICE_SENDER['email'],
              password=EMAIL_NOTICE_SENDER['password']):
    "send email to a list of receivers"
    assert type(to) == list
    assert type(files) == list
    # get email settings
    if not (server and user and password):
        raise LookupError("Invalid email sending settings")
    msg = MIMEMultipart()
    msg['From'] = sentfrom
    msg['To'] = COMMASPACE.join(to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    for f in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(f, 'rb').read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename="%s"' % os.path.basename(f))
        msg.attach(part)
    try:
        smtp_s = smtplib.SMTP(server)
        smtp_s.ehlo()
        smtp_s.starttls()
        smtp_s.login(user, password)
        smtp_s.sendmail(sentfrom, to, msg.as_string())
        smtp_s.close()
        print "successfully sent the mail !"
    except Exception as err:
	print(err)
        print 'failed to send a mail '


def get_days_since_received(status_detail):
    "parse case status and computes number of days elapsed since case-received"
    date_regex = re.compile(r'^(On|As of) (\w+ +\d+, \d{4}), .*')
    m = date_regex.match(status_detail)
    datestr = m.group(2)
    if not datestr:
        return -1
    recv_date = datetime.strptime(datestr, "%B %d, %Y").date()
    today = date.today()
    span = (today - recv_date).days
    return span

def do_check(case):

    casenumber = case['case_id']
    # poll status
    code, status, detail = poll_optstatus(casenumber)
    if code == STATUS_ERROR:
        raise Exception("The case number %s is invalid." % casenumber)
    # report format
    report_format = ("-------  Your USCIS Case [{0}]---------"
                     "\nCurrent Status: [{1}]"
                     "\nDays since received: [{2}]")
    days_elapsed = get_days_since_received(detail)

    report = report_format.format(casenumber, status, days_elapsed)
    # compare with last status
    changed = False
    if case['status'] != status:
        changed = True
    # generate report
    report = '\n'.join(
        [report, "Previous Status:%s \nChanged?: %s" % (case['status'], changed),
         "Current Timestamp: %s " % datetime.now().strftime("%Y-%m-%d %H:%M"),
	 "For details: http://h1b.laiaolai.com",
	 "Donation is welcome!!"])
    # email notification on status change
    if case['email'] and changed:
        recv_list = case['email'].split(',')
        subject = "Your USCIS Case %s Status Change Notice " % casenumber
        send_mail("USCIS Case Status Notify", recv_list, subject, report)
    return status

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

def query_db(db, query, args=(), one=False):
    db.row_factory = make_dicts
    cur = db.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def insert_db(db, query, args=()):
    db.cursor().execute(query, args)
    db.commit()

CASES_SQL = '''
SELECT
    case_id, email, interval
FROM
    h1b_case
'''
STATUS_SQL = '''
SELECT
    status, last_check
FROM
    h1b_case_history
WHERE case_id = ?
ORDER BY last_check DESC
LIMIT 1
'''
INSERT_HISTORY = '''
INSERT INTO
    h1b_case_history(case_id, status)
VALUES(?, ?)
'''

def get_all_cases(db):
    to_check_cases = []
    cases = query_db(db, CASES_SQL)
    for case in cases:
        status = query_db(db, STATUS_SQL, [case['case_id']], one=True)
        if status and status['status'] != 'Case Was Approved':
            case['status'] = status['status']
            time_stamp = calendar.timegm(
                time.strptime(status['last_check'], "%Y-%m-%d %H:%M:%S"))
            now_time_stamp = int(time.time())
            if now_time_stamp - time_stamp > case['interval']:
                to_check_cases.append(case)
        else:
            case['status'] = None
            to_check_cases.append(case)
    return to_check_cases

def main():
    db = sqlite3.connect(DATABASE)
    to_check_cases = get_all_cases(db)
    for case in to_check_cases:
        print(case)
        try:
            status = do_check(case)
            insert_db(db, INSERT_HISTORY, [case['case_id'], status])
        except Exception as err:
            print(err)

if __name__ == '__main__':
    main()
