from colorama import *
from datetime import datetime
from fake_useragent import FakeUserAgent
from faker import Faker
import gc
import json
import os
import pytz
import random
import requests
import string
import sys


class Tari:
    def __init__(self) -> None:
        with open('data.json', 'r') as file:
            self.config = json.load(file)

        self.session = requests.Session()
        self.faker = Faker()
        self.headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Host': 'universe.tari.com',
            'Origin': 'https://universe.tari.com',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': FakeUserAgent().random
        }

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_timestamp(self, message, timezone='Asia/Jakarta'):
        local_tz = pytz.timezone(timezone)
        now = datetime.now(local_tz)
        timestamp = now.strftime(f'%x %X %Z')
        print(
            f"{Fore.BLUE + Style.BRIGHT}[ {timestamp} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{message}",
            flush=True
        )

    def generate_emails(self):
        email_parts = self.config['email'].split('@')
        generated_emails = set()

        for _ in range(self.config['count']):
            random_string = ''.join(random.choices(string.ascii_lowercase, k=8))
            emails = f'{email_parts[0]}+{random_string}@{email_parts[1]}'.strip().splitlines()
            generated_emails.update(emails)

        sorted_emails = sorted(generated_emails)
        self.print_timestamp(f"{Fore.CYAN + Style.BRIGHT}[ Generated {len(sorted_emails)} Emails ]")
        return sorted_emails

    def sign_up_referral(self, email: str):
        url = 'https://universe.tari.com/api/email'
        data = json.dumps({'name':self.faker.name(),'email':email,'referralCode':self.config['referral_code']})
        self.headers.update({
            'Content-Type': 'application/json',
            'Content-Length': str(len(data)),
            'Referer': f'https://universe.tari.com/?referralCode={self.config['referral_code']}',
        })
        try:
            response = self.session.post(url=url, headers=self.headers, data=data)
            response.raise_for_status()
            sign_up_referral = response.json()
            if sign_up_referral is not None:
                if 'success' in sign_up_referral:
                    if sign_up_referral['success']:
                        self.print_timestamp(f"{Fore.GREEN + Style.BRIGHT}[ Success Referral For {email} ]{Style.RESET_ALL}")
                    else:
                        self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Failed Referral For {email} ]{Style.RESET_ALL}")
                else:
                    self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ There Is No 'success' In Sign Up Referral ]{Style.RESET_ALL}")
            else:
                self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Data In Sign Up Referral Is None ]{Style.RESET_ALL}")
        except requests.HTTPError as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Sing Up Referral: {str(e)} ]{Style.RESET_ALL}")
        except requests.RequestException as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ A Request Error Occurred While Sing Up Referral: {str(e)} ]{Style.RESET_ALL}")
        except Exception as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Sing Up Referral: {str(e)} ]{Style.RESET_ALL}")

    def main(self):
        while True:
            emails = self.generate_emails()
            try:
                for email in emails:
                    self.sign_up_referral(email=email)
                self.clear_terminal()
                gc.collect()
            except Exception as e:
                self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")


if __name__ == '__main__':
    while True:
        try:
            init(autoreset=True)
            tari = Tari()
            tari.main()
        except (Exception, requests.JSONDecodeError) as e:
            tari.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")
        except KeyboardInterrupt:
            tari.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ See You 👋🏻 ]{Style.RESET_ALL}")
            sys.exit(0)