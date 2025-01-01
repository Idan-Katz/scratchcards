import streamlit as st
import requests
import pandas as pd

st.title("Test API Request in Streamlit")

# Make a GET request
print("1")
try:
    response = requests.get('https://www.pais.co.il/hishgad/', headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Cookie": "_gcl_au=1.1.1600652248.1733943100; glassix-visitor-id-v2-39c0fdd7-b927-4baa-9b03-a69376715a8a=a50bc35b-b5b8-4d17-a2c7-87f73328c861; _gid=GA1.3.1488352399.1735428800; kjsdfghkjsdfhgjksdf4=poq5sfalxbw1f5rmyfs5z1rh; BIGipServerPais2019-Pool=940943552.20480.0000; _ga_NY9B0P1RZD=GS1.1.1735494848.22.1.1735497282.60.0.1200897607; _ga=GA1.1.365096061.1733943100; _ga_YZ88Z2NRSN=GS1.1.1735494848.22.1.1735497282.0.0.1762795621; TS014141d5=01400e68b24a979225873cd0afd5f3fa09c9dd4ed04023c4f23d2b26ab60090bbc990b991484f750a6a66d647fd92203a82b1034a00a82aa5aa1fa99b0415a939b2836573f08c62a2743de4876ed4cfe1f0ddff7b3",
    "DNT": "1",
    "Host": "www.pais.co.il",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\""
}, timeout=10, proxies={'https': 'http://81.218.86.226:8080'}, verify=False)
    print("2")
    if response.status_code == 200:
        print(response.text)
        pd.to_pickle(response.text,"output")
    else:
        print(f"Error: {response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")