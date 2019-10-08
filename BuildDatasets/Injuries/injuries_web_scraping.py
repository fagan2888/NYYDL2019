import pandas as pd
import numpy as np

import calendar
import requests
import json


class InjuriesWebScraping(object):
    
    def __init__(self, start_year, end_year):
        self.raw_header = ['orig_asset_type', 'player', 'team_id', 'trans_date_cd', 'player_id', 'conditional_sw', 'name_sort',                              'note', 'type_cd', 'trans_date', 'from_team', 'effective_date', 'type', 'transaction_id', 'orig_asset',                            'final_asset_type', 'from_team_id', 'final_asset', 'resolution_cd', 'resolution_date',                                            'name_display_last_first', 'name_display_first_last', 'team', 'status']
        self.raw_data = pd.DataFrame(columns = self.raw_header)
        self.start_year = start_year
        self.end_year = end_year
        
    
    def scrape(self):
        
        print('Web Scraping injury events from the MLB history.')
        
        for year in range(self.start_year, self.end_year + 1):
            for month in range(1, 13):
                self.__scrape_month(year,month)
        print('')
        
        
                
    def __scrape_month(self, year, month):

        maxday = calendar.monthrange(year,month)[1]
        monthstr = str(month) #convert number type to string type and make it two digits if it's less than 10
        if len(monthstr) < 2: 
            monthstr = '0' + monthstr
        start = '%s%s01' % (year, monthstr)
        end = '%s%s%02d' % (year, monthstr, maxday)
        url = "http://mlb.mlb.com/lookup/json/named.transaction_all.bam?start_date=%s&end_date=%s&sport_code='mlb'" % (start,end)

        print ('Year: %d, Month: %s' % (year, monthstr), end="\r")
        
        # Make the HTTP request.
        response = requests.get(url)
        # Use the json module to load CKAN's response into a dictionary.
        response_dict = json.loads(response.text)
        data = response_dict['transaction_all']['queryResults']

        if 'row' in data.keys():
            if type(data['row']) is dict:
                #only one transaction
                rows = [ data['row'], ]
            else:
                rows = data['row']
            for row in rows:
                descrip = row['note'].lower() #use lowercase text
                if 'disabled' in descrip or 'DL' in descrip or 'injur' in descrip: # we want only injuries
                    if 'placed' in descrip:
                        row['status'] = 'placed'
                    elif 'activated' in descrip:
                        row['status'] = 'activated'
                    else:
                        row['status'] = 'transferred'
                    row = pd.DataFrame.from_records([row])
                    self.raw_data = pd.concat([self.raw_data, row], sort=True)
