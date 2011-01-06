import datetime
from pytz import timezone
import MySQLdb
from jinja2 import Environment, FileSystemLoader

def index():
    env = Environment(loader=FileSystemLoader('C:\server\public_html\wwia'))
    template = env.get_template('template.htm')
    
    eastern = timezone('US/Eastern')
    fmt = "%Y-%m-%d %H:%M:%S %Z%z"

    # Current time in UTC
    now_utc = datetime.datetime.now(timezone('UTC'))

    # Convert to US/Eastern time zone
    now_eastern = now_utc.astimezone(timezone('US/Eastern'))

    dfmt = "%Y-%m-%d"
    curDateStr = now_eastern.strftime(dfmt)
    tfmt = "%H:%M:%S"
    curTimeStr = now_eastern.strftime(tfmt)

    conn = MySQLdb.connect(host="localhost", user="root", passwd="root", db="tvdb")
    cursor = conn.cursor()
    
    getlatestquery = '''SELECT t1.tvshows_show_id, t1.season, t1.episode_no, t1.`date`, t2.`name`, t2.network, t2.`time`, t2.end_time
                        FROM episodes AS t1 JOIN tvshows AS t2
                        ON (t1.tvshows_show_id = t2.show_id)
                        WHERE t1.`date` > %s OR (t1.`date` = %s AND t2.end_time > %s)
                        ORDER BY t1.`date`;'''
    cursor.execute( getlatestquery, (curDateStr, curDateStr, curTimeStr))
    rowsLatestEp = cursor.fetchall()
    keys = [row[0] for row in rowsLatestEp]
    values = [row[1:] for row in rowsLatestEp]
    dictLatest = dict(zip(keys, values))
    
    tvshowsdata = []
    countdowndata = []

    for row in rowsLatestEp:
        SHOW_ID = row[0]

        if dictLatest.has_key(SHOW_ID):
            (season, episode_no, date, name,network, time, end_time) = dictLatest[SHOW_ID]
            starttime = datetime.datetime.combine(date, datetime.time()) + time
            endtime = datetime.datetime.combine(date, datetime.time()) + end_time
            starttime = eastern.localize(starttime)
            endtime = eastern.localize(endtime)
            
            if now_eastern > starttime and now_eastern < endtime:
                td = endtime - now_eastern
                # outStrl.append("It's on TV right now!!!")
                # outStrl.append("Ending at " + endtime.strftime(fmt))
            else:
                td = starttime - now_eastern
                # outStrl.append("Wait for it...")
                # outStrl.append("It airs on " + starttime.strftime(fmt))
            
            days = td.days
            totalSeconds = td.seconds
            seconds = totalSeconds % 60
            totalSeconds /= 60
            minutes = totalSeconds % 60
            totalSeconds /= 60
            hours = totalSeconds % 24
            
            info_t = { 'id' : SHOW_ID,
                       'name' : name,
                       'network' : network,
                       'season' : season,
                       'episodeNo' : episode_no
                     }
            tvshowsdata.append(info_t)
            
            countdown_t = { 'name' : 'tvshow' + str(SHOW_ID),
                            'day' : days,
                            'hour' : hours,
                            'min' : minutes,
                            'sec' : seconds
                          }
            countdowndata.append(countdown_t)

    cursor.close()
    conn.close()
    
    return template.render(tvshows = tvshowsdata, datalist = countdowndata)

if __name__=="__main__": index()
