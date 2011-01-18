import urllib2
from BeautifulSoup import BeautifulSoup
import MySQLdb
import datetime

def update():
    months = {"Jan" : 1, "Feb" : 2, "Mar" : 3, "Apr" : 4, "May" : 5, "Jun" : 6,
              "Jul" : 7, "Aug" : 8, "Sep" : 9, "Oct" : 10, "Nov" : 11, "Dec" : 12}

    conn = MySQLdb.connect(host="localhost", user="root", passwd="root", db="tvdb", use_unicode=True, charset="utf8")
    if conn:
        cursor = conn.cursor()

        # Get the URL for all shows from database
        cursor.execute('SELECT show_id, baseurl FROM tvshows')
        rowsAllShows = cursor.fetchall()
        
        # Get the latest episode for each show stored in database
        latestqueryStr = '''SELECT t1.tvshows_show_id, t1.season, t1.episode_no, t1.`date`
                          FROM episodes AS t1
                          LEFT OUTER JOIN episodes AS t2
                          ON (t1.tvshows_show_id = t2.tvshows_show_id AND t1.date < t2.date)
                          WHERE t2.tvshows_show_id IS NULL'''
        cursor.execute(latestqueryStr)
        rowsLatestEp = cursor.fetchall()
        # Zip it up in a dictionary keyed on tvshows_show_id
        keys = [row[0] for row in rowsLatestEp]
        values = [row[1:] for row in rowsLatestEp]
        dictLatest = dict(zip(keys, values))
        
        # Get the oldest episode with name as NULL
        nullqueryStr = '''SELECT t1.tvshows_show_id, t1.season, t1.episode_no, t1.`date`
                          FROM episodes as t1
                          LEFT OUTER JOIN episodes AS t2
                          ON t1.tvshows_show_id = t2.tvshows_show_id AND t1.`date` > t2.`date` AND t1.name IS NULL AND t2.name IS NULL
                          WHERE t2.tvshows_show_id IS NULL AND t1.name IS NULL'''
        cursor.execute(nullqueryStr)
        rowsNullEp = cursor.fetchall()
        # Zip it up in a dictionary keyed on tvshows_show_id
        keys = [row[0] for row in rowsNullEp]
        values = [row[1:] for row in rowsNullEp]
        dictNull = dict(zip(keys, values))
        
        for row in rowsAllShows:
            SHOW_ID = row[0]
            BASE_URL = row[1]
            print "Opening URL... " + BASE_URL
            f = urllib2.urlopen(BASE_URL)
            print "Reading Data..."
            data = f.read()
            f.close()

            print "Parsing..."
            soup = BeautifulSoup(data)

            episodes = soup.findAll("div", "news-content-inner-w")
            
            # DOM Structure of `episodes`
            # <div class="news-content-inner-w">
            # <h2><a href=""><i>House</i> Episode Recap: "Small Sacrifices"</a>Season 7, Episode 8</h2>
            # <ul class="byline">
            #   <li class="first">Nov 23, 2010 09:02 AM ET</li>
            #   <li>by <a href="">Gina DiNunno</a></li>
            #   <li><a href="" class="rednav">episode details</a></li>
            #   <li><a href=""><span id=""></span></a></li>
            # </ul>
            # <p><div class="watch-episode">
            #      <div class="watch-episode-thumb"><a><img /></a></div>
            #      <div class="watch-episode-link"><a>Watch Episode</a></div>
            # </div></p>
            # <p>A patient who makes a deal with... </p>
            # <a href="" class="rednav">read more</a>
            # <div class="share-bottom"></div>
            # </div>

            print "show_id : %d" % (SHOW_ID)
            
            latestEpName = ''.join(episodes[0].contents[1].contents[0].findAll(text=True))  # House Episode Recap: "Small Sacrifices"
            latestEp = episodes[0].contents[1].contents[1].strip()  # Season x, Episode x
            splitlatestEp = latestEp.split(",")
            latestSeason = int(splitlatestEp[0][7:])
            latestEpNo = int(splitlatestEp[1][8:])
            print "Latest episode on web : %d-%d" % (latestSeason, latestEpNo)

            if dictLatest.has_key(SHOW_ID):
                dblatestEp = dictLatest[SHOW_ID]
                print "Latest episode in database : %d-%d" % dblatestEp[:2]
            else:
                dblatestEp = [-1, -1, datetime.date(datetime.MINYEAR, 1, 1)] # No Episodes available in database
                print "No episode data in database"
            
            if dictNull.has_key(SHOW_ID):
                dbnullEp = dictNull[SHOW_ID]
                print "Oldest episode in database with name NULL : %d-%d" % dbnullEp[:2]
            else:
                dbnullEp = [500, 500, datetime.date(datetime.MAXYEAR, 1, 1)]; # No Episode with name `NULL`
                print "All episodes have name set"
                
            valuesList = []
            for episode in episodes:
                epName = ''.join(episode.contents[1].contents[0].findAll(text=True))
                ep = episode.contents[1].contents[1].strip() # Season x, Episode x
                splitEp = ep.split(",")
                season = int(splitEp[0][7:])
                epNo = int(splitEp[1][8:])
                rawdate = episode.contents[3].contents[1].string.strip() # Oct 18, 2010 09:00 PM ET
                ldate = rawdate.split()
                date = "-".join([ ldate[2], str(months[ldate[0]]), ldate[1][:-1]])
                date_obj = datetime.datetime.strptime(date, "%Y-%m-%d").date()
                if date_obj > dblatestEp[2]:
                    print "%d %d %s %d" % (season, epNo, date, SHOW_ID)
                    newValues = [str(season), str(epNo), epName if epName else 'NULL', date, str(SHOW_ID)]
                    valuesList.extend(newValues)
                elif date_obj >= dbnullEp[2] and epName:
                    print "%d %d %s %d" % (season, epNo, date, SHOW_ID)
                    try:
                        cursor.execute('UPDATE episodes SET name = %s WHERE tvshows_show_id = %s AND season = %s AND episode_no = %s', \
                                       (epName, SHOW_ID, season, epNo))
                        print "Number of rows updated: %d" % cursor.rowcount
                        conn.commit()
                    except:
                        conn.rollback()
                else:
                    break
            
            if valuesList:
                n = len(valuesList) / 5
                valuesStr = ('(%s, %s, %s, %s, %s),' * n)[:-1]
                try:
                    cursor.execute('INSERT INTO episodes (season, episode_no, name, date, tvshows_show_id) VALUES ' + valuesStr, \
                                    tuple(valuesList))
                    print "Number of rows inserted: %d" % cursor.rowcount
                    conn.commit()
                except:
                    conn.rollback()
            else:
                print "Nothing to INSERT"
            
        cursor.close()
        conn.close()
    else:
        print "Error establishing connection with database"

if __name__=="__main__" : update()
