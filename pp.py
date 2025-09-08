# ===========> DON'T CHANGE THIS
# SCRIPT : VALIDATOR PAYPAL DETECT COUNTRY
# VERSION : 4.0
# TELEGRAM AUTHOR : https://t.me/zlaxtert
# SITE : https://darkxcode.site/
# TEAM : DARKXCODE
# ================> END

import os
import requests
import threading
import time
import json
import re
from colorama import *
from termcolor import colored
from configparser import ConfigParser
from concurrent.futures import ThreadPoolExecutor, as_completed

#colors
merah = Fore.LIGHTRED_EX
hijau = Fore.LIGHTGREEN_EX
biru = Fore.LIGHTBLUE_EX
kuning = Fore.LIGHTYELLOW_EX
magenta = Fore.LIGHTMAGENTA_EX
cyan = Fore.CYAN
reset = Fore.RESET
bl = Fore.BLUE
wh = Fore.WHITE
gr = Fore.LIGHTGREEN_EX
red = Fore.LIGHTRED_EX
res = Style.RESET_ALL
yl = Fore.YELLOW
cy = Fore.CYAN
mg = Fore.MAGENTA
bc = Back.GREEN
fr = Fore.RED
sr = Style.RESET_ALL
fb = Fore.BLUE
fc = Fore.LIGHTCYAN_EX
fg = Fore.GREEN
br = Back.RED

# BANNER 

banner = f"""{hijau}
                                 /           /                          
                                /' .,,,,  ./ \                           
                               /';'     ,/  \                                
                              / /   ,,//,'''                         
                             ( ,, '_,  ,,,' ''                 
                             |    /{merah}@{hijau}  ,,, ;' '               
                            /    .   ,''/' ',''       
                           /   .     ./, ',, ' ;                      
                        ,./  .   ,-,',' ,,/''\,'                 
                       |   /; ./,,'',,'' |   |                                               
                       |     /   ','    /    |                                               
                        \___/'   '     |     |                                               
                         ',,'  |      /     '\                                              
                              /  (   |   )    ~\                                            
                             '   \   (    \     \~                                            
                             :    \                \                                                 
                              ; .         \--                                                  
                               :   \         ; {magenta}                                                 
,------.    ,---.  ,------. ,--. ,--.,--.   ,--. ,-----.  ,-----. ,------.  ,------. 
|  .-.  \  /  O  \ |  .--. '|  .'   / \  `.'  / '  .--./ '  .-.  '|  .-.  \ |  .---' 
|  |  \  :|  .-.  ||  '--'.'|  .   '   .'    \  |  |     |  | |  ||  |  \  :|  `--,  
|  '--'  /|  | |  ||  |\  \ |  |\   \ /  .'.  \ '  '--'\ '  '-'  '|  '--'  /|  `---. 
`-------' `--' `--'`--' '--'`--' '--''--'   '--' `-----'  `-----' `-------' `------' {reset}
{fr}       ===================================================================={reset}
                  |{fb} SCRIPT{reset}  :{fg} VALIDATOR PAYPAL DETECT COUNTRY{reset} |
                  |{fb} VERSION{reset} :{fg} 4.0{reset}                             |
                  |{fb} AUTHOR {reset} :{fg} https://t.me/zlaxtert{reset}           |
{fr}       ===================================================================={reset}
"""

class PayPalValidator:
    def __init__(self):
        self.config = ConfigParser()
        self.load_config()
        self.lists = []
        self.proxies = []
        self.results = {'live': [], 'die': []}
        self.checked = 0
        self.lock = threading.Lock()
        
    def load_config(self):
        if not os.path.exists('settings.ini'):
            self.create_default_config()
        self.config.read('settings.ini')
        
        # Validate required settings
        if self.config['SETTINGS']['APIKEY'] == 'PASTE_YOUR_API_KEY_HERE':
            print(f"{res}[{yl}!{res}]{fb} Please configure your API key in {yl}settings.ini{fb} {res}[{yl}!{res}]{fb}\n\n")
            exit()
        elif self.config['SETTINGS']['API'] == 'PASTE_YOUR_API_HERE':
            print(f"{res}[{yl}!{res}]{fb} Please configure your API in {yl}settings.ini{fb} {res}[{yl}!{res}]{fb}\n\n")
            exit()
        elif self.config['SETTINGS']['PROXY_AUTH'] == 'PASTE_YOUR_PROXY_AUTH_HERE':
            print(f"{res}[{yl}!{res}]{fb} Please configure your PROXY AUTH in {yl}settings.ini{fb} {res}[{yl}!{res}]{fb}")
            print(f"{res}[{yl}!{res}]{fb} If your proxy does not use Authentication, then leave the PROXY AUTH section in the {yl}settings.ini{fb} file blank {res}[{yl}!{res}]{fb}\n\n")
            exit()
        
    def create_default_config(self):
        self.config['SETTINGS'] = {
            'APIKEY': 'PASTE_YOUR_API_KEY_HERE',
            'API': 'PASTE_YOUR_API_HERE',
            'PROXY_AUTH': 'PASTE_YOUR_PROXY_AUTH_HERE',
            'TYPE_PROXY': 'http'
        }
        with open('settings.ini', 'w') as f:
            self.config.write(f)
        print(f"{res}[{yl}!{res}]{fb} Default {fg}settings.ini{fb} created. Please configure it before running {res}[{yl}!{res}]{fb}\n\n")
        exit()
        
    def validate_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
        
    def load_lists(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"{res}[{yl}!{res}]{fb} Lists file {fg}{file_path}{fb} not found {res}[{yl}!{res}]{fb}\n\n")
            
        with open(file_path, 'r') as f:
            emails = [line.strip() for line in f.readlines() if line.strip()]
            
        valid_emails = [email for email in emails if self.validate_email(email)]
        invalid_emails = set(emails) - set(valid_emails)
        
        if invalid_emails:
            print(f"{res}[{yl}!{res}]{fb} Filtered out {fg}{len(invalid_emails)}{fb} invalid emails {res}[{yl}!{res}]{fb}\n\n")
            
        return valid_emails
        
    def load_proxies(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"{res}[{yl}!{res}]{fb} Proxy file {fg}{file_path}{fb} not found {res}[{yl}!{res}]{fb}\n\n")
            
        with open(file_path, 'r') as f:
            proxies = [line.strip() for line in f.readlines() if line.strip()]
        return proxies
        
    def make_request(self, email, proxy=None):
        params = {
            'apikey': self.config['SETTINGS']['APIKEY'],
            'list': email,
            'proxy': proxy if proxy else '',
            'proxyAuth': self.config['SETTINGS']['PROXY_AUTH'],
            'type_proxy': self.config['SETTINGS']['TYPE_PROXY']
        }
        
        try:
            response = requests.get(
                f"https://{self.config['SETTINGS']['API']}/validator/paypalV2/",
                params=params,
                timeout=50
            )
            return response.json()
        except Exception as e:
            return {'error': str(e)}
            
    def process_result(self, result, email):
        if 'data' in result:
            if result['data'].get('valid') == 'true':
                info = result['data']['info']
                return 'live', {
                    'email': email,
                    'status': 'LIVE',
                    'country': info.get('country', 'N/A'),
                    'country_code': info.get('country_code', 'N/A'),
                    'msg': info.get('msg', 'N/A')
                }
            else:
                return 'die', {
                    'email': email,
                    'status': 'DIE',
                    'msg': result['data']['info'].get('msg', 'N/A')
                }
        else:
            return 'die', {
                'email': email,
                'status': 'DIE',
                'msg': result.get('error', 'UNKNOWN RESPONSE')
            }
            
    def check_email(self, email, proxy=None):
        result = self.make_request(email, proxy)
        status, data = self.process_result(result, email)
        
        with self.lock: 
            self.checked += 1
            self.results[status].append(data)
            
            # Display progress
            progress = f"{yl}Checked {res}[{fr}{self.checked}{res}/{fg}{len(self.lists)}{res}]"
                                    
            if status.upper() == "LIVE" :
                stats = f"{hijau}{status.upper()}{reset}"
                print(f"{progress}{res} -{yl} {email}{res} -> {stats} | {yl}{data['country'].upper()}{res} | {data['msg']} |{cyan} BY DARKXCODE V4.0{reset}")
                self.save_results()
            else :
                stats = f"{merah}{status.upper()}{reset}"
                print(f"{progress} - {email} -> {stats} | {data['msg']} |{cyan} BY DARKXCODE V4.0{reset}")
                self.save_results()
                
    def save_results(self):
        os.makedirs('result', exist_ok=True)
        
        with open('result/live.txt', 'w') as f:
            for result in self.results['live']:
                f.write(f"{result['email']} | {result['country']} | {result['country_code']}\n")
                
        with open('result/die.txt', 'w') as f:
            for result in self.results['die']:
                f.write(f"{result['email']} | {result['msg']}\n")
            
    def run(self):
        lists_file = input(f"{res}[{yl}+{res}]{fb} Enter Email lists file{fg} >> {fb}").strip()
        proxy_file = input(f"{res}[{yl}+{res}]{fb} Enter Proxy lists file{fg} >> {fb}").strip()
        
        try:
            self.lists = self.load_lists(lists_file)
            self.proxies = self.load_proxies(proxy_file) if proxy_file else []
        except Exception as e:
            print(f"Error: {e}")
            return
            
        threads = 0
        while threads < 3 or threads > 10:
            try:
                threads = int(input(f"{res}[{yl}+{res}]{fb} Enter number of Threads (3-10){fg} >> {fb}").strip())
                
            except ValueError:
                print(f"{res}[{yl}!{res}]{fb} Please enter a valid number {res}[{yl}!{res}]{fb}")
                
        print(f"\n{yl}Starting validation with {fg}{len(self.lists)}{yl} emails and {fb}{len(self.proxies)}{yl} proxies{res}")
        print(f"{fr}={res}" * 60)
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = []
            for i, email in enumerate(self.lists):
                proxy = self.proxies[i % len(self.proxies)] if self.proxies else None
                futures.append(executor.submit(self.check_email, email, proxy))
                
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Error: {e}")
                    
        print(f"{fr}={res}" * 60)
        print(f"Checking completed! Live: {fg}{len(self.results['live'])}{res} | Die: {fr}{len(self.results['die'])}{res}")
        print(f"Time taken: {time.time() - start_time:.2f} seconds")
        print(f"{res}[{yl}!{res}]{fb} Results saved in 'result' folder {res}[{yl}!{res}]{fb}")
        print(f"{fr}={res}" * 60)
        
if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    print(banner)
    validator = PayPalValidator()
    validator.run()
