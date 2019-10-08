import pandas as pd
import numpy as np

from .injuries_web_scraping import *
from .injuries_cleaning import *
from .injuries_wrangling import *


class Injuries(object):
    
    def __init__(self, start_year, end_year):
        self.start_year = start_year
        self.end_year = end_year

        
    def build(self):
        scrapper = InjuriesWebScraping(self.start_year, self.end_year)
        scrapper.scrape()
        cleaner = InjuriesCleaning(scrapper.raw_data)
        cleaner.clean_raw_data()
        wrangler = InjuriesWrangling(cleaner.cleaned_data)
        wrangler.organize()

        self.raw_data = scrapper.raw_data
        self.cleaned_data = cleaner.cleaned_data
        self.organized_data = wrangler.organized_data