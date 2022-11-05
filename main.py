import requests
from bs4 import BeautifulSoup

cookies = {
    'WCO_ID': 'jhsing24%40cmc.edu%3Dfb96cb68f8f69230b3a148074d5ea7bb',
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    # 'Cookie': 'WCO_ID=jhsing24%40cmc.edu%3Dfb96cb68f8f69230b3a148074d5ea7bb',
    'DNT': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
}

response = requests.get('https://cmc.mywconline.net/', cookies=cookies, headers=headers)
html_doc = response.text
soup = BeautifulSoup(html_doc, 'html.parser')
tables=soup.select('table', class_=".sch")
tags=soup.select('tr', {'class':'sch_row'})

for table in tables:
    slots=[]
    date_raw=table.find('td', class_='sch_date')
    colonIndex=date_raw.text.index(':')
    date=date_raw.text[:colonIndex]
    tags=table.select('tr', class_='.sch_row')
    for tag in tags:
        td=tag.select('td', {'class':'sch_resource'})
        for t in td:
            if t.find("p"):
                mentor_name=t.find("p")
                if mentor_name.text[:6]=='Jerome':
                    appointments=tag.find_all('td', class_='sch_slots')
                    appointments=appointments[1:3]
                    
                    for i in appointments:
                        if i['title'][:7]!='Reserve':
                            ind=i['title'].index('</b>')
                            slots.append(f"{date}:{i['title'][3:ind]}")
                        else:
                            slots.append('Open')
    import datetime
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request

    from datetime import datetime, timedelta
    from cal_setup import get_calendar_service
    import pytz


    service = get_calendar_service()
    for index,i in enumerate(slots):
        try:
            d = datetime.now().date()
            colonIndex=i.index(':')
            if slots.index(i)==0:
                time=15
            else:
                time=16
            date=i[0:colonIndex]+f', {d.year} {time}'
            start=datetime.strptime(date, '%b. %d, %Y %H')
            end = start + timedelta(hours=1)
            user=i[colonIndex+1:]
            teststart=(start+timedelta(minutes=5)).isoformat('T')+'.000Z'
            testend=(end-timedelta(minutes=5)).isoformat('T')+'.000Z'
            local = pytz.timezone("America/Los_Angeles")
            local_dt = local.localize(start, is_dst=None)
            start_utc_dt = local_dt.astimezone(pytz.utc).isoformat('T')[:19]+'.000Z'
            local_dt = local.localize(end, is_dst=None)
            end_utc_dt = local_dt.astimezone(pytz.utc).isoformat('T')[:19]+'.000Z'

            
            
            workcalID='c_hdnujb0mp1opk7adlkbeqb2p70@group.calendar.google.com'
            events_result = service.events().list(calendarId=workcalID, timeMin=start_utc_dt,
                                          timeMax=end_utc_dt).execute()
            events = events_result.get('items')
            if not events:
                start = start.isoformat()
                end = end.isoformat()
                event_result = service.events().insert(calendarId=workcalID,
                    body={
                        "summary": user,
                        "start": {"dateTime": start, "timeZone": 'America/Los_Angeles'},
                        "end": {"dateTime": end, "timeZone": 'America/Los_Angeles'},
                    }
                ).execute()

                print("created event")
                print("id: ", event_result['id'])
                print("summary: ", event_result['summary'])
                print("starts at: ", event_result['start']['dateTime'])
                print("ends at: ", event_result['end']['dateTime'])
            else:
                print(f'GCal Event for {user} Already Created')

        except:
            pass
    
    