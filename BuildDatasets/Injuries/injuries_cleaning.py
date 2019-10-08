import pandas as pd
import numpy as np


class InjuriesCleaning(object):
    
    def __init__(self, raw_data):
        self.cleaned_header = ['player_id', 'team_id', 'effective_date', 'player', 'team', 'note', 'status']
        self.raw_data = raw_data

        
    def clean_raw_data(self):
        self.cleaned_data = self.raw_data[self.cleaned_header]
        self.cleaned_data = self.cleaned_data[self.cleaned_data['status'] != 'transferred'].\
                                             sort_values(['player_id', 'effective_date']) 
        print('Before the first cleaning...')
        self.__filter_missings()
        print('Before the second cleaning...')
        self.__filter_missings()
        self.cleaned_data = self.cleaned_data.reset_index(drop=True)

        
    def __filter_missings(self):
        
        self.__find_missing_records()
        print('The percentage of correct records was %d' % (round(100 * np.mean(self.non_missing))) + '%.' )
        self.cleaned_data = self.cleaned_data.iloc[np.array([record == 1 for record in self.non_missing])]
        
    
    def __find_missing_records(self):
        
        players = list(self.cleaned_data['player_id'])
        status = list(self.cleaned_data['status'])
        
        self.non_missing = []
        skip = 0

        for i in range(len(players) - 1):
            if skip:
                skip = 0
            else: 
                if players[i] == players[i+1] and status[i] == status[i+1]:
                    if status[i] == 'placed':
                        self.non_missing.append(0)
                    else:
                        self.non_missing = self.non_missing + [1,0]
                        skip = 1
                elif (players[i] != players[i+1] and status[i] == 'placed') or \
                     (players[i] != players[i-1] and status[i] == 'activated'):
                        self.non_missing.append(0)
                else:
                    self.non_missing.append(1)

        if len(self.non_missing) < len(players):
            if status[len(players) - 1] == 'placed':
                self.non_missing.append(0)
            else:
                self.non_missing.append(1)
                