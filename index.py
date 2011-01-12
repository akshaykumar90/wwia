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
    now_date = now_eastern.date()
    now_time = now_eastern.time()

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
    
    # Get the upcoming 2 episodes for all tvshows found in the database
    # If the episode has alreaady aired for today's date, it should not be
    # counted as upcoming, rather the next episode is the upcoming episode,
    # hence 2 episodes are retrieved from the database
    getUpcomingEps = '''(SELECT tvshows_show_id, season, episode_no, `name`, `date` 
                         FROM episodes 
                         WHERE tvshows_show_id = %s and `date` >= "''' + str(now_date) + '''"
                         ORDER BY `date` 
                         LIMIT 2)'''
    fquery = [getUpcomingEps] * len(dictShowData.keys())
    getUpcomingEps = ' UNION '.join(fquery) + ';'
    cursor.execute( getUpcomingEps, dictShowData.keys())
    rowsUpcomingData = cursor.fetchall()
    
    dictUpcoming = {} # Stores all the upcoming/on tv episodes for all tvshows
    dictPrevious = {} # Stores all the previous episodes for all tvshows
    
    # Insert in dictUpcoming if the episode has not aired yet,
    # hence the check for time if episode for today has already aired or not
    # In that case, insert the next episode from db which has been already
    # retrieved. Remember 2? Also insert that episode into dictPrevious
    for row in rowsUpcomingData:
        if dictUpcoming.has_key(row[0]):
            continue 
        else:
            if (now_date == row[4] and now_time < end_time) or (now_date < row[4]):
                dictUpcoming[row[0]] = row[1:]
            else:
                dictPrevious[row[0]] = [row[1:]]
    
    # Get the previous 2 episodes for all tvshows found in the database
    getPreviousEps = '''(SELECT tvshows_show_id, season, episode_no, `name`, `date` 
                         FROM episodes 
                         WHERE tvshows_show_id = %s and `date` < "''' + str(now_date) + '''"
                         ORDER BY `date` DESC
                         LIMIT 2)'''
    fquery = [getPreviousEps] * len(dictShowData.keys())
    getPreviousEps = ' UNION '.join(fquery) + ';'
    cursor.execute( getPreviousEps, dictShowData.keys())
    rowsPreviousData = cursor.fetchall()
    
    for row in rowsPreviousData:
        if dictPrevious.has_key(row[0]):
            if len(dictPrevious[row[0]]) == 2: # Do not insert more that 2 episodes
                pass
            else:
                dictPrevious[row[0]].append(row[1:])
        else:
            dictPrevious[row[0]] = [row[1:]]
    
    # To pass on to the template
    tvshowsdata = []
    countdowndata = []

    for SHOW_ID in dictShowData.keys():
        upcomingEps = []
        previousEps = []
        
        if dictUpcoming.has_key(SHOW_ID):
            (season, episode_no, name, date) = dictUpcoming[SHOW_ID]
            
            info_u = { 'name' : name,
                       'season' : season,
                       'episode_no' : episode_no,
                       'date' : date
                     }
            
            time = dictShowData[SHOW_ID][2] # From `tvshows`
            end_time = dictShowData[SHOW_ID][3] # From `tvshows`
            starttime = datetime.datetime.combine(date, datetime.time()) + time
            endtime = datetime.datetime.combine(date, datetime.time()) + end_time
            starttime = eastern.localize(starttime)
            endtime = eastern.localize(endtime)
        
            if now_eastern > starttime:
                # It's on TV right now!!!
                td = endtime - now_eastern 
                info_u['on_tv'] = True
            else:
                # Wait for it..."
                td = starttime - now_eastern
        
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
            
            upcomingEps.append(info_u)
        
        if dictPrevious.has_key(SHOW_ID):
            pEps = dictPrevious[SHOW_ID]
            for ep in pEps:
                (season, episode_no, name, date) = ep
                info_t = { 'name' : name,
                           'season' : season,
                           'episode_no' : episode_no,
                           'date' : date
                         }
                previousEps.append(info_t)
            
        info_s = { 'id' : SHOW_ID,
                   'name' : dictShowData[SHOW_ID][0], # From `tvshows`
                   'network' : dictShowData[SHOW_ID][1], # From `tvshows`
                   'upcomingEps' : upcomingEps,
                   'previousEps' : previousEps
                 }
        
        tvshowsdata.append(info_s)

    cursor.close()
    conn.close()
    
    return template.render(tvshows = tvshowsdata, countdown = countdowndata)

if __name__=="__main__": index()
