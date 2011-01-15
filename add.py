import MySQLdb
import cgi
from mod_python import Cookie
from jinja2 import Environment, FileSystemLoader

def show(req):
    colors = req.form.getlist('selected_shows')
    colors = map(lambda color: cgi.escape(color), colors)

    s = """\
<html><body>
<p>The submitted colors were "%s"</p>
<p><a href="./fill">Submit again!</a></p>
</body></html>
"""
    return s % ', '.join(colors)

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