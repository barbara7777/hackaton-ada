from typing import Optional, Type
import urllib.request

from bs4 import BeautifulSoup
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun

class RtvTool(BaseTool):
    name = "Novice"
    description = "Uporabi ko želiš prebrati novice iz spleta."

    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        page = urllib.request.urlopen('http://rtvslo.si')
        soup = BeautifulSoup(page.read(), 'html.parser')
        aktualno = soup.find(attrs={'id':'112-1'})
        main_news = aktualno.find(attrs={'class':'xl-news'})
        news = f"{main_news.find_all('a')[2].string.strip()}\n{main_news.find('p').string.strip()}\n\n"
        
        for item in aktualno.find_all(attrs={'class':'rotator-title-container'}): 
            one_news = f"{item.find_all('a')[1].string.strip()}\n{item.find('p').string.strip()}\n\n"
            news += one_news
        
        return f"Trenutne aktualne novice so:\n{news}\n Uporabniku jih predstavi v obliki kratkega povzetka."