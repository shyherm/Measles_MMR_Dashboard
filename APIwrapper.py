import requests
import time

class APIwrapper:
    _access_point="https://api.ukhsa-dashboard.data.gov.uk"
    _last_access=0.0 
    
    def __init__(self, theme, sub_theme, topic, geography_type, geography, metric):
        """ Init the APIwrapper object, constructing the endpoint from the structure parameters """
        url_path=(f"/themes/{theme}/sub_themes/{sub_theme}/topics/{topic}/geography_types/" +
                  f"{geography_type}/geographies/{geography}/metrics/{metric}")
        self._start_url=APIwrapper._access_point+url_path
        self._filters=None
        self._page_size=-1
        self.count=None

    def get_page(self, filters={}, page_size=5):
        """ Access the API and download the next page of data. Sets the count attribute to the total number of items available for this query. 
        Changing filters or page_size will cause get_page to restart from page 1. Rate limited to three request per second. 
        The page_size parameter sets the number of data points in one response page (maximum 365); use the default value for debugging your structure and filters. """
        if page_size>365:
            raise ValueError("Max supported page size is 365")
        if filters!=self._filters or page_size!=self._page_size:
            self._filters=filters.copy()
            self._page_size=page_size
            self._next_url=self._start_url
        if self._next_url==None: 
            return [] 
        curr_time=time.time() 
        deltat=curr_time-APIwrapper._last_access
        if deltat<0.33: 
            time.sleep(0.33-deltat)
        APIwrapper._last_access=curr_time
        parameters={x: y for x, y in filters.items() if y!=None}
        parameters['page_size']=page_size
        response = requests.get(self._next_url, params=parameters).json()
        self._next_url=response['next']
        self.count=response['count']
        return response['results'] 

    def get_all_pages(self, filters={}, page_size=365):
        """ Access the API and download all available data pages of data. Sets the count attribute to the total number of items available for this query. 
        API access rate limited to three request per second. The page_size parameter sets the number of data points in one response page (maximum 365), 
        and controls the trade-off between time to load a page and number of pages; the default should work well in most cases. 
        The number of items returned should in any case be equal to the count attribute. """
        data=[] 
        while True:
            next_page=self.get_page(filters, page_size)
            if next_page==[]:
                break
            data.extend(next_page)
        return data