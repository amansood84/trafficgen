# Instructions
# Copy http_traffic_generator.py and http_traffic_generator.yaml in the same directory
# Run by executing python3 http_traffic_genertor.py


# ToDo: Check why exceptions are being generated. At this scale there should not be any exception
# ToDo: Doesnt work with SNI. Needs to be fixed
# ToDo: Add support for different tls versions and ciphers
# ToDo: Add support to generate a csv file with the results of the run
# ToDo: Add support for non HTTP traffic
import time
import requests
# Used to disable warning generated for failed SSL certificate verification
requests.packages.urllib3.disable_warnings()
import yaml
import sys
import re
import csv

def get_time_to_run (duration):
    seconds_to_run = 0
    re_match =  re.findall(r'((\d*)d)?((\d*)h)?((\d*)m)?((\d*)s)?', duration)
    #  if input is correct re_match will be in the format [('1d', '1', '3h', '3', '2m', '2', '', ''), ('', '', '', '', '', '', '', '')]

    days = re_match[0][1]
    hours = re_match[0][3]
    minutes = re_match[0][5]
    seconds = re_match[0][7]

    if days != "":
        days = int(days)
    else:
        days = 0
    if hours != "":
        hours = int(hours)
    else:
        hours = 0
    if minutes != "":
        minutes = int(minutes)
    else:
        minutes = 0
    if seconds != "":
        seconds = int(seconds)
    else:
        seconds = 0

    seconds_to_run = days*86400 + hours*3600 + minutes*60 + seconds
    return seconds_to_run

def get_user_agent_from_dev_type (dev_type):
    user_agent_string = None

    if dev_type == "android":
        user_agent_string = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36"
    elif dev_type == "windows":
        user_agent_string = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"
    elif dev_type == "iphone":
        user_agent_string = "Mozilla/5.0 (iPhone14,3; U; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Mobile/19A346 Safari/602.1"
    elif dev_type == "mac":
        user_agent_string = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9"

    return user_agent_string

def get_execution_mode (duration, num_requests):
    run_type = 'permanent'
    run_value = 0
    if duration != "":
        start_epoch = time.time() 
        run_duration = get_time_to_run (duration)
        end_epoch = start_epoch + run_duration
        run_type = 'time'
        run_value = end_epoch

    if num_requests != "":
        run_type = 'request'
        run_value = num_requests

    return {"execution_mode": run_type, "count": run_value}

if __name__ == '__main__':
    with open('http_traffic_generator.yaml', 'r') as file:
        targets = yaml.full_load(file)

    global_vars = targets.get("global_config")

    try:
        duration = global_vars.get("type").get("duration")  
        num_requests = int(global_vars.get("type").get("num_requests"))
        execution_mode = get_execution_mode(duration, num_requests)
        print (execuriton_mode)
        run_type = execution_mode.get("run_type")
        if run_type == 'time':
            end_epoch = execution_mode.get("count")
            print (run_type)
            print (end_epoch)
        elif run_type == 'request':
            num_requests = execution_mode.get("count")
            print (run_type)
            print (num_requests)
    except:
        run_type = 'permanent'

    requests_sent = 0
    iteration = 0

    while True:
        time.sleep (2)
        iteration = iteration + 1
        print ("Iteration %d" %(iteration))

        if run_type == 'time':
            curr_epoch = time.time()
            if (curr_epoch > end_epoch):
                sys.exit()
        elif run_type == 'request':
            requests_sent = requests_sent + 1
            if num_requests == requests_sent:
                sys.exit()

        for target in targets.get("endpoint"):
            vip = target.get("vip")
            if vip is None or vip == "":
                continue
            protocol = target.get("protocol")
            if protocol is None or protocol == "":
                continue
            for request in target.get("request"):
                http_req_type = request.get("type")
                http_url_path = request.get("path")

                # Header Processing
                # http_req_headers is urrently a list, however requests expects a dictionary
                http_req_headers_list = request.get("headers")
                http_req_headers = {}
                if http_req_headers_list is not None:
                    for header in http_req_headers_list:
                        http_req_headers.update({header.get("name"):header.get("value")})

                # Cookie Processing
                http_cookies_list = request.get("cookies")
                http_cookies = {}
                if http_cookies_list is not None:
                    for cookie in http_cookies_list:
                        http_cookies.update({cookie.get("name"):cookie.get("value")})

                # User Agent Processing
                http_user_agent = get_user_agent_from_dev_type(request.get("device_type"))
                if http_user_agent is not None and http_user_agent != "":
                    http_req_headers.update({"User-Agent": http_user_agent})

                # Generate URL
                req_url = protocol + '://' + vip + http_url_path
                if http_req_type == "get":
                    try:
                        requests.get(req_url, headers = http_req_headers, cookies = http_cookies, verify=False)
                    except requests.exceptions.ConnectionError:
                        print ("Connection Exception")
                    except requests.exceptions:
                        print ("Hitting exceptions")
                elif http_req_type == "post":
                    http_req_body = request.get("body")
                    try:
                        requests.post(req_url, headers = http_req_headers, cookies = http_cookies, json=http_req_body, verify=False)
                    except requests.exceptions.ConnectionError:
                        print ("Connection Exception")
                    except requests.exceptions:
                        print ("Hitting exceptions")
                else:
                    print ("Unsupported HTTP Method")

