#!/usr/bin/python3

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from time import sleep
import requests, selenium, argparse

class CustomFormatter(argparse.RawDescriptionHelpFormatter):
    def __init__(self, prog):
        super().__init__(prog, max_help_position=40, width=80)
    def _format_action_invocation(self, action):
        if not action.option_strings:
            metavar, = self._metavar_formatter(action, action.dest)(1)
            return metavar
        else:
            parts = []
            if action.nargs == 0:
                parts.extend(action.option_strings)
            else:
                default = action.dest.upper()
                args_string = self._format_args(action, default)
                for option_string in action.option_strings:
                    parts.append('%s' % option_string)
                parts[-1] += ' %s'%args_string
            return ', '.join(parts)

parser=argparse.ArgumentParser(description="Gets ovpns from freevpn.us with supplied username and password. \
Ovpns will be in config.zip", formatter_class=CustomFormatter, usage="%(prog)s [-h] [-u USERNAME] [-p PASSWORD] \
[-f PATH] [-g PATH] [-o PATH]")

parser.add_argument("-u", "--username", help="username to register account with", metavar="   USERNAME")
parser.add_argument("-p", "--password", help="password to register account with", metavar="   PASSWORD")
parser.add_argument("-f", "--firefox_bin", default='/usr/local/bin/firefox/firefox', help="path to firefox", metavar="PATH")
parser.add_argument("-g", "--gecko_bin", default='/usr/local/bin/geckodriver', help="path to geckodriver", metavar="  PATH")
parser.add_argument("-o", "--output", default='config.zip', help="output file (zip)", metavar="     PATH")
args=parser.parse_args()


usr=args.username
passwd=args.password
username=None
output=args.output

options=Options()
options.binary_location = args.firefox_bin
options.add_argument("--headless")
serv=Service(args.gecko_bin)

driver = webdriver.Firefox(options=options, service=serv)
driver.get("https://www.freevpn.us/vpn/us/")
srvs={}
srvs[1]=int(driver.find_element_by_xpath("//div[contains(@class, 'col-xl-3')][1]//div[contains(@class, 'card-body')]//span[1]").text)
srvs[2]=int(driver.find_element_by_xpath("//div[contains(@class, 'col-xl-3')][2]//div[contains(@class, 'card-body')]//span[1]").text)
srvs[3]=int(driver.find_element_by_xpath("//div[contains(@class, 'col-xl-3')][3]//div[contains(@class, 'card-body')]//span[1]").text)
srvs[4]=int(driver.find_element_by_xpath("//div[contains(@class, 'col-xl-3')][4]//div[contains(@class, 'card-body')]//span[1]").text)
srvs={key: value for key, value in sorted(srvs.items(), key=lambda item: item[1])}

best=driver.find_element_by_xpath("//div[contains(@class, 'col-xl-3')]["+str(srvs[4])+"]//div[contains(@class, 'card-body')]/a\
").get_attribute("href")

driver.get(best)
sleep(3)
driver.find_element_by_xpath("//input[contains(@name, 'username')]").send_keys(usr)
driver.find_element_by_xpath("//input[contains(@name, 'password')]").send_keys(passwd)
driver.find_element_by_xpath("//button[contains(@class, 'btn btn-primary')]").click()
sleep(2)
while username == None:
    global password, hostname
    try: 
        username=driver.find_element_by_xpath("//ul[contains(@id, 'savetoimage')]/li[1]").text
        password=driver.find_element_by_xpath("//ul[contains(@id, 'savetoimage')]/li[2]").text
        hostname=driver.find_element_by_xpath("//ul[contains(@id, 'savetoimage')]/li[3]").text
        config=driver.find_element_by_xpath("//ul[contains(@id, 'savetoimage')]/li[6]/a").get_attribute("href")
        open(output, "wb").write(requests.get(config).content)
    except exceptions.NoSuchElementException as e:
        pass
    except Exception as e:
        print(e)
driver.quit()
print(username)
print(password)
print(hostname)
print("Config: "+output)
