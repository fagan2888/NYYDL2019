import pandas as pd
import numpy as np

import dateutil.parser 


class InjuriesWrangling(object):

    def __init__(self, cleaned_data):
        self.initial_header = ['player_id', 'team_id', 'player', 'team', 'placed_date', 'activated_date', 'note']
        self.positions = ['RHP','LHP','C','1B','2B','3B','SS','LF','RF','CF','DH', 'OF']
        self.potential_locations = ['shoulder','elbow','hamstring','knee','back','oblique','groin','forearm',
         'wrist','ankle','finger','thumb','calf','tommy john','hand','foot','quad',
         'hip','bicep','neck','rib','flexor','tricep','intercostal','rotator cuff','toe','abdominal',
         'achilles','lumbar','append','pectoral','cervical','adductor','ac joint','labrum',
         'trapezius','thoracic','meniscus']
        self.two_meanings_list = ['back','hip','flexor','hand','infection','hernia','toe','cervical']
        self.popular_locations_list = ['shoulder','elbow','hamstring','knee']
        self.potential_types = ['strain', 'inflam', 'concussion', 'contusion', 'sprain', 'surgery', 
         'tendinitis','fracture','tightness', 'sore', 'discomfort', 'bruise', 'spams','spasm', 'infection', 
         'dislocat','impingement','blister','bursitis','irritation','hyperext','tear','torn','broken',
         'injury','pain','fasciitis','fatigue','stiffness', 'sublux','disease', 'lacerat','reaction','hernia']
        self.cleaned_data = cleaned_data
        
    
    def organize(self):
        self.__joined_placed_and_activated()
        self.__get_time_data()
        self.__get_position_data()
        self.__get_location_data()
        self.__get_type_data()

        
    def __joined_placed_and_activated(self):
        placed_df = self.cleaned_data[self.cleaned_data['status'] == "placed"].\
                                     rename(columns={"effective_date": "placed_date"}).\
                                     reset_index(drop=True)
        activated_df = self.cleaned_data[self.cleaned_data['status'] == "activated"]\
                                        [['effective_date']].\
                                        rename(columns={"effective_date": "activated_date"}).\
                                        reset_index(drop=True)
        self.organized_data = placed_df.join(activated_df)
        self.organized_data = self.organized_data[self.initial_header]


    def __get_time_data(self):
        placed_dates = [dateutil.parser.parse(x) for x in self.organized_data['placed_date']]
        activated_dates = [dateutil.parser.parse(x) for x in self.organized_data['activated_date']]

        self.organized_data['placed_date'] = placed_dates
        self.organized_data['activated_date'] = activated_dates
        self.organized_data['injured_days'] = np.array([
            (activated_dates[i] - placed_dates[i]).days for i in range(len(placed_dates))
        ])

        
    def __get_position_data(self):
        self.organized_data['position'] = [
            position for note in self.organized_data['note'] for position in self.positions 
                if ' %s ' % position in note
        ]

        
    def __get_location_data(self):
        self.locations = [
            [location for location in self.potential_locations if location in note.lower()] 
                for note in self.organized_data['note']
        ]
        self.__remove_if_two_meanings_list()
        self.locations = [self.__popular_if_two(arr) for arr in self.locations]
        self.locations = [self.__dearray(arr) for arr in self.locations]
        self.__set_unknown('location')
        self.organized_data['location'] = self.locations
        self.locations = None

        
    def __get_type_data(self):        
        self.types = [
            [kind for kind in self.potential_types if kind in note.lower()] 
                for note in self.organized_data['note']
        ]
        self.types = [self.__dearray(arr) for arr in self.types]
        self.__set_unknown('type')
        self.organized_data['type'] = self.types
        self.types = None
        
        
    def __remove_if_two_meanings_list(self):
        
        def remove_if_two(arr, location):
            if len(arr) > 1 and location in arr:
                arr = [x for x in arr if x != location]
            return arr

        for location in self.two_meanings_list:
            self.locations = [remove_if_two(arr, location) for arr in self.locations]
        
                
    def __popular_if_two(self, arr):
        if len(arr) > 1 and len([popular for popular in self.popular_locations_list if popular in arr]) > 0 :
            arr = [popular for popular in self.popular_locations_list if popular in arr]
        return arr           
    
    
    def __dearray(self, arr):
        if arr:
            return(arr[0])
        else:
            return('other')
        
    
    def __set_unknown(self, attribute):
        
        def get_sentences(note, delim='.'):
            return [x for x in note.split(delim) if x]
        
        one_sentence_indices = [
            i for i, note in enumerate(self.organized_data['note']) if len(get_sentences(note)) == 1
        ]
        
        if attribute == 'location':
            for i in one_sentence_indices:
                if self.locations[i] == 'other':
                    self.locations[i] = 'unknown'
        elif attribute == 'type':
            for i in one_sentence_indices:
                if self.types[i] == 'other':
                    self.types[i] = 'unknown'
 