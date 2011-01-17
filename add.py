import MySQLdb
import cgi
from mod_python import Cookie, util
from jinja2 import Environment, FileSystemLoader

def save(req):
    # Get a list with all the values of the selected_shows[]
    selected_shows = req.form.getlist('selected_shows[]')
    # Escape the user input to avoid script injection attacks
    selected_shows = map(lambda show: cgi.escape(show), selected_shows)
    
    # Value of the cookie is the list of selected shows seperated by ','
    cookie_str = ','.join(selected_shows)
    c = Cookie.Cookie('selected_shows', cookie_str)
    
    # Add the cookie to the HTTP header
    Cookie.add_cookie(req, c)
    
    util.redirect(req, 'http://localhost/wwia')

def index(req):
    # Configure Jinja2
    env = Environment(loader=FileSystemLoader('C:\server\public_html\wwia'))
    template = env.get_template('addshows.htm')
    
    all_cookies = Cookie.get_cookies(req)
    selected_shows = all_cookies.get('selected_shows', None)
    
    if selected_shows:
        sslist = selected_shows.value.split(',')
        sslist = [int(s) for s in sslist]
    else:
        sslist = [1,2,3]
    
    conn = MySQLdb.connect(host="localhost", user="root", passwd="root", db="tvdb_test")
    cursor = conn.cursor()
    
    getShowDataQuery = '''SELECT show_id, `name` FROM tvshows ORDER BY `name`'''
    cursor.execute( getShowDataQuery )
    rowsShowData = cursor.fetchall()
    
    dictShows = {}
    tvshowsdata = []

    for show in rowsShowData:
        SHOW_ID = int(show[0])
        NAME = show[1]
        CHECKED = True if SHOW_ID in sslist else False

        # Names are no longer preceeded with "The" - e.g. The Office -> Office [The]
        if NAME.startswith('The '):
            NAME = NAME[4:] + ' [The]'
        
        info_s = {
            'id' : SHOW_ID,
            'name' : NAME,
            'checked' : CHECKED
        }
        
        key = NAME[0] # First character of show name
        if key.isdigit():
            key = '#'
        key = key.upper()
 
        if dictShows.has_key(key):
            dictShows[key].append(info_s)
        else:
            dictShows[key] = [info_s]
        pass
    
    for k,v in dictShows.iteritems():
        info_l = { 
            'char' : k,
            'contents' : v
        }
        tvshowsdata.append(info_l)

    cursor.close()
    conn.close()
    
    return template.render(tvshowsdata = tvshowsdata)
    
if __name__=="__main__": index()
