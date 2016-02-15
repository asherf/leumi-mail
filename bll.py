# -*- coding: utf-8 -*-
import json
import collections
import os
from bs4 import BeautifulSoup
from dumppdf import extract_attachments
from dateutil.parser import parse as parse_date

MailDetails = collections.namedtuple('MailDetails', 'account date subject')
ACCOUNT_HINT = u'חוקל .סמ'
SUBJECT_HINT = u"ןודנה"
ACCOUNT_COMMON = "10-"
SP = u'\xa0'

def pn(lines):
    for p in lines:
        print p

def do_work():
    password, location = load_config()
    export_htmls(location, password)


def load_config():
    fn = os.path.join(os.environ['HOME'], ".leumi-mail-params.json")
    config = json.loads(open(fn).read())
    return config['pdf_password'], config['pdfs_location']

def export_htmls(pdf_location, pdf_password):
    accounts = set()
    years = set()
    base_path = "leumi_attachments"
    os.mkdir(base_path)
    for p in list_files(pdf_location, "pdf"):
        extract_attachments(p, pdf_password, base_path)
        for attchs in list_files(base_path, "html"):
            details = get_details(attchs)
            accounts.add(details.account)
            years.add(details.date.year)
            os.remove(attchs)
    print accounts
    print years

def list_files(base_path, file_type):
    for item in os.listdir(base_path):
        p = os.path.join(base_path, item)
        if os.path.isfile(p):
            if item.endswith(".%s" % file_type):
                yield os.path.join(base_path, item)
        elif os.path.isdir(p):
            for d in list_files(p, file_type):
                yield d


def _remove_chars(value, *to_remove):
    for r in to_remove:
        value = value.replace(r, "")
    return value


def _reslove_subject(lines, account_line_index):
    subject = filter(lambda ln: SUBJECT_HINT in ln, lines)
    if subject:
        return _remove_chars(subject[0], SUBJECT_HINT, "|", ":").strip(SP)
    subject = ("%s %s" % (lines[account_line_index+2].strip(SP), lines[account_line_index+3].strip(SP))).strip()
    if not subject:
        subject = _remove_chars(lines[account_line_index+7],":", '"').replace(SP+SP, SP).strip(SP)
        if not subject:
            raise Exception("can't determine subject")
    return subject


def _reslove_date(lines, account_line, account_line_index):
    account_offset = 25
    try:
        dt_str = str(account_line[:account_offset].strip())
    except UnicodeEncodeError:
        account_offset = 0
        dt_str = str(lines[account_line_index-1].strip())
    dt = parse_date(dt_str, dayfirst=True).date()
    return dt, account_offset


def get_details(fn):
    soup = BeautifulSoup(open(fn).read(), 'html.parser')
    lines = [t.find("span").text for t in soup.find_all("td") if t.find("span")]

    account_line = filter(lambda ln: ACCOUNT_HINT in ln, lines)[0]
    account_line_index = lines.index(account_line)
    dt, account_offset = _reslove_date(lines, account_line, account_line_index)
    account_number = str(account_line[account_offset:].replace(ACCOUNT_HINT, "").replace(SP, "").replace("/", "-"))
    if not account_number.startswith(ACCOUNT_COMMON):
        raise Exception("unexpected account number %s" % account_number)
    account_number = account_number.replace(ACCOUNT_COMMON, "")
    subject = _reslove_subject(lines, account_line_index)
    print subject
    return MailDetails(account=account_number, date=dt, subject=subject)


def prepare_path(basepath, details):
    fn = "%s %s.html" % (details.date.strftime("%d-%m-%Y"), details.subject[::-1])
    folder = os.path.join(basepath, details.account, str(details.date.year))
    if not os.path.exists(folder):
        os.makedirs(folder)
    p1 = os.path.join(folder, fn)
    return p1
