from webbrowser import Mozilla
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv()
DAILY_COOKIE = os.getenv("DAILY_COOKIE")
DAILY_SESSION = os.getenv("DAILY_SESSION")

def bookCourt(park, court, date, time):
    url = "https://tennissheffield.com/ajax/basket-court"

    headers = {
        "accept": "application/json",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://tennissheffield.com",
        "referer": "https://tennissheffield.com/book/courts/weston-park/2025-12-08",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Safari/605.1.15",
        "x-requested-with": "XMLHttpRequest",
    }
    
    cookies = {
        "ct": DAILY_COOKIE,
        "sess": DAILY_SESSION
    }
        
    park_IDs = {
        "weston_park": "37",
        "graves_park": "36",
        "bingham_park": "76"
    }

    court_IDs = {
        "weston_park": {
            "1": "69",
            "2": "70",
        },
        "graves_park": {
            "1": "71",
            "2": "72",
            "3": "73",
            "4": "74",
            "5": "75",
        },
        "bingham_park": {
            "1": "100",
            "2": "101",
        }
    }


    data = {
        "mode": "add",
        "court": f"{park_IDs[park]}_{court_IDs[park][court]}_{date}_{time}"  
    }

    response = requests.post(url, headers=headers, cookies=cookies, data=data)

    return response.status_code

def addDiscount(discountCode):
    url = "https://tennissheffield.com/basket/discount"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://tennissheffield.com",
        "Referer": "https://tennissheffield.com/basket",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Safari/605.1.15"
    }

    cookies = {
        "ct": DAILY_COOKIE,
        "sess": DAILY_SESSION
    }

    basket_page = requests.get(
        f"https://tennissheffield.com/basket",
        headers=headers,
        cookies=cookies
    )

    soup = BeautifulSoup(basket_page.text, "html.parser")

    csrf_name = soup.find("input", {"name": "csrf_name"})["value"]
    csrf_value = soup.find("input", {"name": "csrf_value"})["value"]

    data = {
        "code": discountCode,
        "csrf_name": csrf_name,
        "csrf_value": csrf_value
    }

    response = requests.post(url, headers=headers, cookies=cookies, data=data)

    return response.status_code


def checkCourtAvailability(park, date, time):
    url = f"https://tennissheffield.com/book/courts/{park}/{date}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Safari/605.1.15",
        "Accept-Language": "en-US,en;q=0.9"
    }

    cookies = {
        "ct": DAILY_COOKIE,
        "sess": DAILY_SESSION
    }

    response = requests.get(url, headers=headers, cookies=cookies)
    html_content = response.text

    soup = BeautifulSoup(html_content, "html.parser")

    form = soup.find("form", action="/book/courts")

    if not form:
        print("Could not find the court booking form!")
    else:
        table = form.find("table")
        
        if table:
            for row in table.find_all("tr"):
                time_slot = row.find("th", class_="time").text

                if time_slot == time:
                    for court in row.find_all("label", class_="court"):
                        button_span = court.find("span", class_="button")
                        court_name = button_span.contents[0]

                        status = button_span.get("class", [])[1]

                        if status == "available":
                            return True, court_name
                    
                    return False, "n/a"
        else:
            print("Could not find the table inside the form.")

def checkVoucher():
    url = f"https://tennissheffield.com/account"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Safari/605.1.15",
        "Accept-Language": "en-US,en;q=0.9"
    }

    cookies = {
        "ct": DAILY_COOKIE,
        "sess": DAILY_SESSION
    }

    response = requests.get(url, headers=headers, cookies=cookies)
    html_content = response.text

    soup = BeautifulSoup(html_content, "html.parser")

    discount_header = soup.find("h2", id="discounts")
    table = discount_header.find_next_sibling("table") 

    table = table.find_all("tr")[1]
    code = table.find_all("td")[0].text.strip()
    uses = table.find_all("td")[2].text.strip()

    return code, uses

def to_ampm(time_str):
    hour = int(time_str.split(":")[0])
    if hour == 0:
        return "12am"
    elif hour < 12:
        return f"{hour}am"
    elif hour == 12:
        return "12pm"
    else:
        return f"{hour-12}pm"

if __name__ == "__main__":

    code, uses = checkVoucher()
    print (f"Current voucher: {code} with {uses} uses remaining")

    bookingDevs = False 
    if bookingDevs:
        courts = ["1", "2", "3", "4", "5"]
        times = ["12:00", "13:00", "14:00", "15:00"]
        location = "graves_park"
        date = "2026-03-07"

        for time in times:
            print (f"Booking for {time}...")
            for court in courts:
                print (f"Booking for court {court}...")

                bookCourt(location, court, date, time)
                addDiscount(code)

                buffer = input("Press Enter to continue...")