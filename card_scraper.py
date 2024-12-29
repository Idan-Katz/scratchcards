import pandas as pd
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import os
import time

CUSTOM_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Cookie": "_gcl_au=1.1.1600652248.1733943100; glassix-visitor-id-v2-39c0fdd7-b927-4baa-9b03-a69376715a8a=a50bc35b-b5b8-4d17-a2c7-87f73328c861; _gid=GA1.3.1854987571.1734211625; kjsdfghkjsdfhgjksdf4=wpf1f4iaci01zeq4eldm0zs4; BIGipServerPais2019-Pool=907389120.20480.0000; TS014141d5=01400e68b2db3593e2f07f170226a5a383f1f4ecfffbed5498fe8fd718a8a7dda9b4df75db0b378c39c886646c24b9ac6414031cae6bd28c7e39d84a2eeb8e1318f952a6d9df925aa2d0378e2d870d132bf2b201dc; _ga_NY9B0P1RZD=GS1.1.1734269574.8.1.1734270163.23.0.1491055021; _ga_YZ88Z2NRSN=GS1.1.1734269574.8.1.1734270163.0.0.441404195; _ga=GA1.3.365096061.1733943100",
    "DNT": "1",
    "Host": "www.pais.co.il",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"'
}
def page_to_soup(url,save = 0):
    response = requests.get(url, headers=CUSTOM_HEADERS) 
    # Optional - Save the HTML for debug
    if save == 1:
        with open("output.html", "w", encoding="utf-8") as file:
            file.write(response.text)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

def fetch_scartchcard_urls(url):  
    soup = page_to_soup(url)
    url_list_soup = soup.find('div',{'data-w-tab': 'Tab 1'}).find_all('a','hishgat_add_link w-inline-block')
    url_list = ['https://www.pais.co.il'+ link.get('href') for link in url_list_soup]
    return url_list

def fetch_scartchcard_data(url):
    soup = page_to_soup(url)

    # Finding the prizes data
    prizes_soup = soup.find('ol',"w-list-unstyled") 
    items = [li.get_text() for li in prizes_soup.find_all('li')]

    # Create a pandas DataFrame and clean it
    df = pd.DataFrame({'Items': items})
    df = df.map(lambda x: str(x).replace(',', ''))
    df_split = df["Items"].str.split("\n", expand=True)
    df_split = df_split.rename(columns={
        3: "prize",
        8: "prize_count",
    })
    df_split
    prizes=df_split.loc[:,["prize","prize_count"]]
    prizes = prizes.astype(int)
    prizes

    #Finding tickets data
    ticket_cost_and_count = soup.find_all("div","game_info_txt")
    details = [div.get_text().strip() for div in ticket_cost_and_count]
    tickets = pd.DataFrame({'Tickets': details})
    tickets = tickets.iloc[[0,4]]
    tickets = tickets.rename(index={0:"ticket_cost",4:"total_tickets_count"})
    tickets = tickets.map(lambda x: str(x).replace(',', ''))
    tickets = tickets.astype(int)

    #Finding scratch card basic details
    scratchcards_soup = soup.find("div","hishgat_game_mainpict").find("img") 
    scratchcards_image = 'https://www.pais.co.il'+scratchcards_soup['src']
    scratchcards_name = scratchcards_soup['alt']
    #Fixing From bug on specific card which does not have price
    if scratchcards_name == "כספת":
        tickets.loc['ticket_cost'] = 25
        tickets.loc['total_tickets_count'] = 4000000

    #Calculate total prizes, cost of all tickets
    total_tickets_cost = tickets.prod(axis=0).iloc[0]

    #Combining ticket and prize data into 1 DataFrame who representing all the scratchcard data
    scratchcards = prizes.copy()
    scratchcards['total_tickets_cost'] = total_tickets_cost
    scratchcards = scratchcards.set_index('total_tickets_cost')
    scratchcards = scratchcards.groupby(level=0).agg({
        'prize': list,         # Combine prize values into a list
        'prize_count': list    # Combine prize_count values into a list
    })
    scratchcards['image'] = scratchcards_image
    scratchcards['name'] = scratchcards_name
    scratchcards = scratchcards.reset_index().set_index(['image','name','total_tickets_cost'])
    return scratchcards

def time_since_creation(file_path):
    creation_time = os.path.getctime(file_path)
    current_time = time.time()
    time_diff = current_time - creation_time
    return time_diff

def fetch_all_scratchcards(all_cards_url):
    scartchcard_urls = fetch_scartchcard_urls(all_cards_url)
    try:
        # Check if there is new card brfore fetching all URLS
        database = pd.read_pickle('scratchcards_database.pkl')
        if database['urls'] == scartchcard_urls:
            return

    except FileNotFoundError:
        # Handle the case where the pickle file doesn't exist
        print(f"Pickle file '{'test.pkl'}' not found. Creating a new one.")   
    
    # Use ThreadPoolExecutor to fetch data in parallel
    with ThreadPoolExecutor(max_workers=10) as executor:  # Adjust max_workers based on your system
        results = list(executor.map(fetch_scartchcard_data, scartchcard_urls))

    # Concatenate the resulting DataFrames
    scratchcards = pd.concat(results)
    pd.to_pickle({'data': scratchcards, 'urls': scartchcard_urls},'/workspaces/scratchcards/scratchcards_database.pkl')