###################################################################################
### Summary
# This is the google app engine version of stevens_ee_627 server
# Deployment:
#         Install google gcloud sdk
#         >> gcloud app deploy app.yaml
# Test in local:
#         Install python package in google sdk
#         >> dev_appserver.py .

###################################################################################
### Libraries and Variables
## Import libraries
import re
import os
import webapp2
import jinja2
import datetime
from google.appengine.ext import ndb

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    #loader=jinja2.FileSystemLoader("."),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

DATASTORE_NAME = 'stevens_ee_627_datastore'
def data_key(ds_name = DATASTORE_NAME):
    return ndb.Key('Stevens', ds_name)

# Dictionary for team
dic_team={}
dic_team_member={}
dic_team_id={}
teamInfoFile = ["1|ICE-BREAKER|N",
    "2|LZZ|N",
    "3|Mc Trump|N",
    "4|OK|N",
    "5|Prototype|N",
    "6|Rocketeers|N",
    "7|Shaker|N",
    "8|Spiral of Data Secrets|N",
    "9|Splinter|N",
    "10|VANQUISHERS|N",
    "11|Wolves|N",
    "12|ZZZ|N"]

for line in teamInfoFile:
    line_temp = line.strip("\n").strip("\r").split("|")
    team = re.sub(r'[^a-zA-Z0-9]','_',line_temp[1].lower())
    dic_team[team]=line_temp[1]
    dic_team_member[team] = line_temp[2]
    dic_team_id[team] = int(line_temp[0])
list_team=[[dic_team[item],item] for item in dic_team]

# Data File
TURE_FILE = os.path.join(os.path.dirname(__file__),'/test_log.txt')
TURE_FILE = 'test_log.txt'
#TURE_FILE = os.path.join(".",'/test_log.txt')

class TeamRanking(ndb.Model):
    date = ndb.DateTimeProperty(auto_now_add=True)
    team = ndb.StringProperty(indexed=False)
    score = ndb.FloatProperty()
    teamid = ndb.IntegerProperty()

class Teamlog(ndb.Model):
    date = ndb.DateTimeProperty(auto_now_add=True)
    team = ndb.StringProperty(indexed=False)
    teamid = ndb.IntegerProperty()
    score = ndb.FloatProperty()

# Create Match Data
true_data = []
with open(TURE_FILE) as trueFile:
    for line in trueFile:
        true_data.append(line.strip("\n").strip("\r"))
###################################################################################
### Main pages

## Homepage, upload file
# /home
class ee_home(webapp2.RequestHandler):
    def get(self):
        pass_values = {
            'team_list': list_team,
            #'url_for_uploaded_file':webapp2.uri_for('check'),
            #'url_for_cur_ranking':webapp2.uri_for('ranking'),
            'url_for_uploaded_file':'/check',
            'url_for_cur_ranking':'/ranking',
        }
        template = JINJA_ENVIRONMENT.get_template('home.html')
        self.response.out.write(template.render(pass_values))

# /test
class ee_test(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("Hi, you found the test page")

# /check
class ee_check(webapp2.RequestHandler):
    def post(self):
        #f = self.request.POST.get('file')
        f = self.request.POST.multi['file'].file.read()
        team_name = self.request.get('team')
        correct_rate = 0
        #test_data = []
        #for item in f[:-1]:
        #    test_data.append(int(item.strip()))
        test_data = f.replace("\r","").split("\n")[:-1]
        #if not (test_data[-1] == 0 or test_data[-1] == 1):
        #    test_data = test_data[:-1]
        # Calculate correct rate
        if len(test_data) == len(true_data):
            ans = [ 1 if i == j else 0 for i,j in zip(test_data,true_data)]
            correct_rate = "%.4f"%(float(sum(ans))/float(len(ans)))

            record = Teamlog(parent = data_key())

            record.team = team_name
            record.score = float(correct_rate)
            record.teamid = dic_team_id[team_name]
            record.put()

            rank_list_query = TeamRanking.query(ancestor=data_key()).order(-TeamRanking.score)
            rank_list = rank_list_query.fetch(12)

            upload = 0
            for item in rank_list:
                if item.team ==team_name:
                    if float(correct_rate) > item.score:
                        item.score = float(correct_rate)
                        item.date = datetime.datetime.now()
                        item.put()
                        break
            else:
                rank_record = TeamRanking(parent = data_key())
                rank_record.team = team_name
                rank_record.score = float(correct_rate)
                rank_record.teamid = dic_team_id[team_name]
                rank_record.put()

            pass_values = {
                'team_name': team_name,
                'correct_rate':correct_rate,
                'date':datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                #'url_for_home':webapp2.uri_for('home'),
                #'url_for_cur_ranking':webapp2.uri_for('ranking'),
                'url_for_home':'/',
                'url_for_cur_ranking':'/ranking',
            }

            template = JINJA_ENVIRONMENT.get_template('uploaded_file.html')
            self.response.write(template.render(pass_values))

        else:
            error = "Length doesn't match, upload lenth %d and required length %d"%(len(test_data),len(true_data))
            #os.remove(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            pass_values = {
                'error': error,
                #'url_for_home':webapp2.uri_for('home'),
                #'url_for_cur_ranking':webapp2.uri_for('ranking'),
                'url_for_home':'/',
                'url_for_cur_ranking':'/ranking',
            }
            template = JINJA_ENVIRONMENT.get_template('error.html')
            self.response.write(template.render(pass_values))

# Leader Board
class ee_cur_ranking(webapp2.RequestHandler):
    def get(self):
        rank_list_query = TeamRanking.query(ancestor=data_key()).order(-TeamRanking.score)
        rank_list = rank_list_query.fetch(12)
        pass_values = {
            'rank_list': rank_list,
            #'url_for_home':webapp2.uri_for('home'),
            #'url_for_cur_ranking':webapp2.uri_for('ranking'),
            'team_name_dic':dic_team,
            'url_for_home':'/',
            'url_for_cur_ranking':'/ranking',
        }
        template = JINJA_ENVIRONMENT.get_template('leader_board.html')
        self.response.write(template.render(pass_values))

app = webapp2.WSGIApplication([
    ('/', ee_home, 'home'),
    ('/test', ee_test, 'test'),
    ('/check', ee_check, 'check'),
    ('/ranking', ee_cur_ranking, 'ranking')
], debug=True)
