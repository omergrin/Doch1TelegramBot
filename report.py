import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import json


class Doch1_Report:

    def __init__(self, config):
        self.session = requests.session()
        self.config = config
        self.session.cookies = requests.utils.cookiejar_from_dict(self.config["cookies"])
        self.session.mount("https://", HTTPAdapter(max_retries=Retry(connect=10, backoff_factor=0.8)))
    
    def login_and_get_soldiers(self):
        res = self.is_logged_in()
        if not res[0]:
            return False, 'Error: ' + res[1]
        
        res = self.login()
        if not res[0]:
            return False, 'Error: ' + res[1]
            
        res = self.get_soldiers()
        if not res[0]:
            return False, 'Error: ' + res[1]
        
        return True, res[1]
    
    def is_logged_in(self):
        burp_url = "https://one.prat.idf.il/api/account/getUser"
        burp_headers = {"authority": "one.prat.idf.il", "access-control-allow-origin": "*", "accept": "application/json, text/plain, */*", "sec-ch-ua-mobile": "?0", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.123 Safari/537.36'", "pragma": "no-cache", "crossdomain": "true", "sec-ch-ua": "\" Not;A Brand\";v=\"99\", \"GoogleChrome\";v=\"91\", \"Chromium\";v=\"91\"'", "sec-fetch-site": "same-origin", "sec-fetch-mode": "cors", "sec-fetch-dest": "empty", "referer": "https://one.prat.idf.il/", "accept-language": "he"}
        response = self.session.get(burp_url, headers=burp_headers)
        if "\"isUserAuth\":true" in response.text:
            return True, ""
        else:
            return False, "The original cookies are not working!\nhttp reason:{}".format(response.text)

    def login(self):
        burp0_url = "https://one.prat.idf.il:443/api/account/loginCommander"
        burp0_headers = {"authority": "one.prat.idf.il", "sec-ch-ua": "\" Not;A Brand\";v=\"99\", \"Google Chrome\";v=\"91\", \"Chromium\";v=\"91\"", "pragma": "no-cache", "sec-ch-ua-mobile": "?0", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.123 Safari/537.36", "content-type": "application/json;charset=UTF-8", "access-control-allow-origin": "*", "accept": "application/json, text/plain, */*", "crossdomain": "true", "origin": "https://one.prat.idf.il", "sec-fetch-site": "same-origin", "sec-fetch-mode": "cors", "sec-fetch-dest": "empty", "referer": "https://one.prat.idf.il/loginCommander", "accept-language": "he,en-US;q=0.9,en;q=0.8,he-IL;q=0.7"}
        burp0_json={"password": self.config["password"], "recaptchaValue": None, "username": self.config["username"]}
        response = self.session.post(burp0_url, headers=burp0_headers, json=burp0_json)
        if "\"isCommanderAuth\":true" in response.text:
            return True, ""
        else:
            return False, "Username And Password did for commander login did not work:{}".format(response.text)

    def get_soldiers(self):
        burp2_url = "https://one.prat.idf.il:443/api/attendance/GetGroups?groupcode="
        burp2_headers = {"authority": "one.prat.idf.il", "access-control-allow-origin": "*", "accept": "application/json, text/plain, */*", "sec-ch-ua-mobile": "?0", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.123 Safari/537.36", "pragma": "no-cache", "crossdomain": "true", "sec-ch-ua": "\" Not;A Brand\";v=\"99\", \"Google Chrome\";v=\"91\", \"Chromium\";v=\"91\"", "sec-fetch-site": "same-origin", "sec-fetch-mode": "cors", "sec-fetch-dest": "empty", "referer": "https://one.prat.idf.il/commander", "accept-language": "he,en-US;q=0.9,en;q=0.8,he-IL;q=0.7"}
        response = self.session.get(burp2_url, headers=burp2_headers)

        try:
            users = json.loads(response.content)['firstGroup']['users']
        except Exception as e:
            return False, "Cannot fetch soldier's names:{}".format(response.text, str(e))
        
        return True, users

    def do_report_and_get_statuses(self, users, pre_placements=None):   
        burp0_headers = {"authority": "one.prat.idf.il", "access-control-allow-origin": "*", "accept": "application/json, text/plain, */*", "sec-ch-ua-mobile": "?0", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.123 Safari/537.36", "pragma": "no-cache", "crossdomain": "true", "sec-ch-ua": "\" Not;A Brand\";v=\"99\", \"Google Chrome\";v=\"91\", \"Chromium\";v=\"91\"", "sec-fetch-site": "same-origin", "sec-fetch-mode": "cors", "sec-fetch-dest": "empty", "referer": "https://one.prat.idf.il/commander/otherStatus", "accept-language": "he,en-US;q=0.9,en;q=0.8,he-IL;q=0.7", "Origin": "https://one.prat.idf.il"}    
        for user in users:
            mainStatusCode = "01"
            secondaryStatusCode = "01"
            note = None
            if pre_placements is not None and user['mi'] in pre_placements:
                mainStatusCode = pre_placements[user['mi']]['mainStatusCode']
                secondaryStatusCode = pre_placements[user['mi']]['secondaryStatusCode']
                if 'note' in pre_placements[user['mi']].keys():
                    note = pre_placements[user['mi']]['note']

            burp1_url = "https://one.prat.idf.il:443/api/Attendance/GetStatusesForCommander"
            burp1_headers = {"authority": "one.prat.idf.il", "access-control-allow-origin": "*", "accept": "application/json, text/plain, */*", "sec-ch-ua-mobile": "?0", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.123 Safari/537.36", "pragma": "no-cache", "crossdomain": "true", "sec-ch-ua": "\" Not;A Brand\";v=\"99\", \"Google Chrome\";v=\"91\", \"Chromium\";v=\"91\"", "sec-fetch-site": "same-origin", "sec-fetch-mode": "cors", "sec-fetch-dest": "empty", "referer": "https://one.prat.idf.il/commander/otherStatus", "accept-language": "he,en-US;q=0.9,en;q=0.8,he-IL;q=0.7", "Origin": "https://one.prat.idf.il"}
            burp1_json={"groupCode": user['groupCode'], "pratMi": user['mi']}
            resp1 = self.session.post(burp1_url, headers=burp1_headers, json=burp1_json)
            burp0_url = "https://one.prat.idf.il:443/api/Attendance/updateAndSendPrat"
            burp0_json={"groupCode": user['groupCode'], "mainStatusCode": mainStatusCode, "mi": user['mi'], "note": note, "secondaryStatusCode": secondaryStatusCode}
            resp2 = self.session.post(burp0_url, headers=burp0_headers, json=burp0_json)

        # get statuses from server
        burp0_url = "https://one.prat.idf.il:443/api/Attendance/GetGroups"
        r = self.session.get(burp0_url, headers=burp0_headers)
        if not r.ok:
            return "Could not get group for confirmation!"
        group = json.loads(r.content)


        final = ""

        for user in group['firstGroup']['users']:
            name = "{} {}".format(user['firstName'], user['lastName'])
            status = "{} {}".format(user['approvedMainName'], user['approvedSecondaryName'])
            note = user['note'] if user['note'] else ''
            final = final + "{name}   -   {status} {note}\n".format(name=name, status=status, note=note)

        return final