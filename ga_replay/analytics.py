import json
from httplib2 import Http

from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient import errors
from apiclient.discovery import build

import config

class Analytics(object):
    """
    Singleton object for accessing google analytics API.
    """

    def __init__(self):
        credentials = ServiceAccountCredentials.from_p12_keyfile(config.CLIENT_EMAIL, config.KEY_FILE, scopes='https://www.googleapis.com/auth/analytics.readonly')
        http_auth = credentials.authorize(Http())
        ga_service = build('analytics', 'v3', http=http_auth)
        self.ga = ga_service.data().ga()   
    
    def execute_query(self, query):
        return query.execute()	

    def get_itinerary(self, start, end, ga_id, extra_dimensions=[]):
        """
        """
        metrics = ['ga:pageviews']
        dimensions = ['ga:pagePath', 'ga:hour', 'ga:minute']
        dimensions.extend(extra_dimensions)
        ga_metrics = ','.join(metrics)
        ga_dimensions = ','.join(dimensions)
        max_results = 10000
        query_kwargs = {
            'ids': ga_id,
            'start_date': start.isoformat(),
            'end_date': end.isoformat(),
            'metrics': ga_metrics,
            'dimensions': ga_dimensions,
            'max_results': max_results,
            'start_index': 1,
        }
        results_needed = True
        all_rows = []
        while results_needed:
            query = self.ga.get(**query_kwargs)
            result = self.execute_query(query)
            all_rows.extend(result['rows'])
            current_index = query_kwargs['start_index'] + max_results
            if current_index >= result['totalResults']:
                results_needed = False
                break
            else:
                print("Requesting results [%s:%s] of %s" % (query_kwargs['start_index'], query_kwargs['max_results'], result['totalResults']))
                query_kwargs['start_index'] = query_kwargs['start_index'] + max_results
        return all_rows
        
analytics = Analytics()
