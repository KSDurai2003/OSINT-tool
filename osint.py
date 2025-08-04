#!/home/kali/iget/bin/python3
import sys
import subprocess
import re
import urllib.parse
import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
import whois
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

def havefw(ipaddr:str):
    try:
        print("If the target has firewall it takes  time,wait for seconds....")
        results = subprocess.check_output(
            ["nmap","-sS",ipaddr],
            stderr=subprocess.STDOUT,
            text=True
        )
        if ping(ipaddr):
            if "1000 filtered tcp ports" in results:
            	print("Host           : Online")
            	print("firewall Status: Yes")
            else:
            	print("Host           : Online")
            	print("firewall Status: No")
        elif( ping(ipaddr)==False):
            print("Host Status    : OnLine")
            print("Firewall Status: No")
    except subprocess.CalledProcessError as e:
    	print(e)
    	return
 
def subDomains(domain: str, active: bool = True):
    try:
        subdomains = subprocess.check_output(
            ["assetfinder", "-subs-only", domain],
            stderr=subprocess.STDOUT,
            text=True
        )
	
        if subdomains is not None:
            print("Enumeration completed, checking for online...")
            subdomains = subdomains.strip().split("\n")  # Split by newline

            for subdomain in subdomains:
                if active:
                    if ping(subdomain):
                        print(f"Alive \t : {subdomain}")
                    else:
                        print(f"Offline \t : {subdomain}")
                else:
                    print(subdomain)

        else:
            print(f"Inactive host: {domain}")

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}", "\n assetfinder package needed: use 'sudo apt install assetfinder'")
        sys.exit(0)   


def init_dorking():
    print('''Usage: <option 1>:<keyword 1> <option2>:<keyword2>\nchoose options wisely for keywords:\n (1) intext(search for text) \n(2)inurl(search for 		 url text)\n(3)intitle(sarch for title)\n(4)site(sarch with site  full name)\n(5)filetype(specific filetype search)\n(6)link\n(7)inanchor(anchor tagged links)\n(8)inpostauthor(search of blog post authors) ''')



def google_dork():
    try:
        
        
        dork = input("🔍 Enter your Google Dork query: ").strip()

        encoded_query = urllib.parse.quote_plus(dork)
        search_url = f"https://www.google.com/search?q={encoded_query}"

        # Configure browser options to reduce bot detection
        options = Options()
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference("useAutomationExtension", False)
        options.set_preference("general.useragent.override",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")

        print("🚀 Launching browser...")
        driver = webdriver.Firefox(options=options)
        driver.get(search_url)

        time.sleep(3)

        
        links = []
        results = driver.find_elements(By.CSS_SELECTOR, "div.g")
        for result in results:
            try:
                link = result.find_element(By.TAG_NAME, "a").get_attribute("href")
                if link and link.startswith("http"):
                    links.append(link)
            except Exception:
                continue

        # Print all collected links
        print("\n🔗 Extracted Links:\n")
        for i, link in enumerate(links, start=1):
            print(f"{i}. {link}")

        input("\n🕒 Press Enter after closing the browser window...")

    except Exception as e:
        print(f"❌ Error occurred: {e}")

    finally:
        try:
            driver.quit()
            print("✅ Browser closed.")
        except:
            pass

         

def extract_all_host_info(url):
    host_data = []

    try:
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=60000)
            page.wait_for_load_state('networkidle')

            soup = BeautifulSoup(page.content(), 'html.parser')
            containers = soup.select("div.container.u-full-width")
            headings = soup.select("div.heading")

            for heading, container in zip(headings, containers):
                try:
                    banner_text = container.select_one("div.banner-data pre").text

                    login_ip_match = re.search(r"Loginip:\s*([\d\.]+)", banner_text)
                    login_ip = login_ip_match.group(1) if login_ip_match else None

                    host_data.append({
                        "Device Name": heading.select_one("a.title").text.strip(),
                        "Host Link": heading.select_one("a.title")["href"],
                        "External Access URL": heading.select_one("a.text-danger")["href"],
                        "Timestamp": heading.select_one("div.timestamp").text.strip(),
                        "IP Address": container.select_one("li.hostnames").text.strip(),
                        "Organization": container.select_one("a.filter-org").text.strip(),
                        "Country": container.select_one("img.flag")["title"],
                        "City": container.select_one("a[href*='city%3A']").text.strip(),
                        "Tags": [tag.text.strip() for tag in container.select("a.tag")],
                        "Login IP": login_ip,
                        "Raw Headers": banner_text.splitlines()
                    })
                except Exception as block_error:
                    print(f"[!] Error parsing block: {block_error}")
                    continue

            browser.close()
    except Exception as browser_error:
        print(f"❌ Browser failed to load or parse content: {browser_error}")

    return host_data

def shodan(keyword: str):
    print(f"🔍 Searching for keyword: '{keyword}'...")
    url = f"https://www.shodan.io/search?query={keyword}"

    try:
        results = extract_all_host_info(url)
        if not results:
            print("⚠️ No host information found or unable to parse content.")
            return

        for index, block in enumerate(results, start=1):
            print(f"\n--- Host #{index} ---")
            for key, value in block.items():
                print(f"{key}: {value}")
    except Exception as e:
        print(f"❌ Error while processing results: {e}")
    finally:
        print("✅ Scan complete.")



def ping(domain:str):
    try:
        results = subprocess.check_output(
            ["timeout","2","ping","-c1",domain],
            stderr=subprocess.STDOUT,
            text=True
        )
        if results is None:
            return False
        if "0% packet loss" in results:
            return True
        else:
            return False
            
    except subprocess.CalledProcessError:
        return False
    except Exception :
        return False
        
        
def manual():
    print("Options:\n \t -f \tfind the target having firewall.\n\t -sd \tsubdomain enumeration.\n\t -s \t start with shodan browsing.\n\t -w \twhois enumeration.\n\t -p \tping target connectivity.\n\t -d \tdorking with google about the target on chrome or your target browser.\n\t -h \thelp for tool usage") 	       


def whois_lookup():
    target = input("🔍 Enter IP or Domain address: ").strip()

    try:
        result = whois.whois(target)

        print("\n📄 WHOIS Information:\n")
        for key, value in result.items():
            key=key.capitalize()
            print("\n--------------",key,"----------------")
            if isinstance(value, list):
                for item in value:
                    print(item)
            else:
                print(value)
    except Exception as e:
        print(f"❌ Error fetching WHOIS data: {e}")

def main():
    print("Target Info v0.0.1")
    print("Generall framework for target systems and simple dorking.. \n use '-h' for help or tool usage")
   
    while True:
        option = input("\nEnter option (or type 'exit' to quit): ").strip()

        if option == "exit":
            print("Exiting... 👋")
            break

        elif option == "-h":
            manual()

        elif option == "-sd":
            domain = input("Domain name: ").strip()
            subDomains(domain)

        elif option == "-p":
            target = input("IP/Domain address: ")
            print("Target online is", ping(target))

        elif option == "-d":
            google_dork()

        elif option == "-f":
            target = input("IP/Domain address: ").strip()
            print(havefw(target))

        elif option == "-w":
            whois_lookup()
            
        elif option == "-s":
            target = input("Search keyword: ").strip()
            print(shodan(target))

        else:
            print("Unknown option. Use the options wisely.\n")
            manual()

def is_ip(s:str):
    regex = r'^((25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)(\.|$)){4}$'
    ip = "192.168.1.1"
    if re.match(ip_regex, test_ip):
        return True
    return False

    
if __name__=="__main__":    
    main()

