import datetime
from pytz import timezone
import MySQLdb
from jinja2 import Environment, FileSystemLoader

def index():
    # Configure Jinja2
    env = Environment(loader=FileSystemLoader('C:\server\public_html\wwia'))
    template = env.get_template('template.htm')
    
    eastern = timezone('US/Eastern')

    # Current time in UTC
    now_utc = datetime.datetime.now(timezone('UTC'))

    # Convert to US/Eastern time zone
    now_eastern = now_utc.astimezone(timezone('US/Eastern'))

    conn = MySQLdb.connect(host="localhost", user="root", passwd="root", db="tvdb", use_unicode=True)
    cursor = conn.cursor()
    
    # Get the tvshows data from `tvshows`
    getShowDataQuery = '''SELECT show_id, `name`, network, `time`, end_time FROM tvshows'''
    cursor.execute( getShowDataQuery )
    rowsShowData = cursor.fetchall()
    # Zip it up in a dictionary keyed on show_id
    keys = [row[0] for row in rowsShowData]
    values = [row[1:] for row in rowsShowData]
    dictShowData = dict(zip(keys, values))
    
    # Get the latest 3 episodes for all tvshows found in the database
    getlatestquery = '''(SELECT tvshows_show_id, season, episode_no, `name`, `date` 
                         FROM episodes 
                         WHERE tvshows_show_id = %s 
                         ORDER BY `date` DESC 
                         LIMIT 3)'''
    fquery = [getlatestquery] * len(dictShowData.keys())
    getlatestquery = ' UNION '.join(fquery) + ';'
    cursor.execute( getlatestquery, dictShowData.keys())
    rowsLatestData = cursor.fetchall()
    # Zip them up in a dictionary keyed on tvshows_show_id; value is a list of tuples of 
    # episode data
    dictLatest = {}
    for row in rowsLatestData:
        if dictLatest.has_key(row[0]):
            dictLatest[row[0]].append(row[1:])
        else:
            dictLatest[row[0]] = [row[1:]]
    
    # To pass on to the template
    tvshowsdata = []
    countdowndata = []

    for SHOW_ID, show_data in dictLatest.iteritems():
        upcoming = True
        seriesdata = [] # Data for a particular series; three episodes
        latestshow = show_data[0]
        
        (season, episode_no, name, date) = latestshow
        time = dictShowData[SHOW_ID][2] # From `tvshows`
        end_time = dictShowData[SHOW_ID][3] # From `tvshows`
        starttime = datetime.datetime.combine(date, datetime.time()) + time
        endtime = datetime.datetime.combine(date, datetime.time()) + end_time
        starttime = eastern.localize(starttime)
        endtime = eastern.localize(endtime)
        
        if now_eastern > endtime:
            # It's already over :(
            upcoming = False
        elif now_eastern > starttime:
            # It's on TV right now!!!
            td = endtime - now_eastern 
        else:
            # Wait for it..."
            td = starttime - now_eastern
        
        if (upcoming):
            days = td.days
            totalSeconds = td.seconds
            seconds = totalSeconds % 60
            totalSeconds /= 60
            minutes = totalSeconds % 60
            totalSeconds /= 60
            hours = totalSeconds % 24
            
            countdown_t = { 'name' : 'tvshow' + str(SHOW_ID),
                            'day' : days,
                            'hour' : hours,
                            'min' : minutes,
                            'sec' : seconds
                          }
            countdowndata.append(countdown_t)
        
        for show in show_data:
            (season, episode_no, name, date) = show
            info_t = { 'name' : name,
                       'season' : season,
                       'episode_no' : episode_no,
                       'date' : date
                     }
            seriesdata.append(info_t)
            if (upcoming):
                seriesdata[0]['latest'] = True
            
        info_s = { 'id' : SHOW_ID,
                   'name' : dictShowData[SHOW_ID][0], # From `tvshows`
                   'network' : dictShowData[SHOW_ID][1], # From `tvshows`
                   'shows' : seriesdata
                 }
        if (upcoming):
            info_s['upcoming'] = True
        tvshowsdata.append(info_s)

    cursor.close()
    conn.close()
    
    return template.render(tvshows = tvshowsdata, datalist = countdowndata)

if __name__=="__main__": index()
