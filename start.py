# -*- coding: utf-8 -*-
# © 2012, Lara Sorokina, KubSAU
__author__ = 'wid0ki <laricasorokina@gmail.com>'

import os.path
import tornado.ioloop
import tornado.web
import hashlib
import smtplib
import psycopg2
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer

def LoginUser(self):
    # Рабочий пользователь widoki@me.com и пароль qwerty
    cur = self.conn.cursor()
    cur.execute("SELECT id, passwd FROM \"user\" WHERE email=%s", (self.get_argument("email"),))
    uid = cur.fetchone()

    if uid[1] == hashlib.md5(self.get_argument("email")+self.get_argument("password")).hexdigest():
        self.set_cookie("user_id", str(uid[0]))
        return True
    else:
        return False

def GetProject(self, project_id):
    cur = self.conn.cursor()
    cur.execute("SELECT user_id, name, description, picture_path, status FROM project "
                "WHERE id = %s", (project_id,))
    prec = cur.fetchone()
    pr = {"id" : project_id,
         "user_id": prec[0],
         "name" : prec[1],
         "description": prec[2],
         "image_path":prec[3],
         "status": prec[4],
         }
    return pr

def nGetProject(self):
    cur = self.conn.cursor()
    cur.execute("SELECT id, name, description, picture_path, status FROM project "
                "WHERE user_id = %s", self.get_cookie("user_id"))
    prec = cur.fetchall()
    prs = []
    for p in prec:
        prs += [{"id" : p[0],
                "user_id": self.get_cookie("user_id"),
                "name" : p[1],
                "description": p[2],
                "image_path":p[3],
                "status": p[4],
                }]
    return prs

def GetResearch(self, research_id):
    cur = self.conn.cursor()
    cur.execute("SELECT id, date, description, name FROM research "
                "WHERE id = %s", [research_id])
    prec = cur.fetchone()
    rc = {"id": prec[0],
          "date": prec[1],
          "description": prec[2],
          "name": prec[3]}
    return rc

def SetResearch(self, pui):
    cur = self.conn.cursor()
    cur.execute("INSERT INTO research (id, name, project_id, user_id, date, description) "
                "VALUES (DEFAULT, %s, %s, %s, CURRENT_DATE, %s)",
                [self.get_argument("research"), pui, self.get_cookie("user_id"),
                 self.get_argument("description"),])
    self.conn.commit()
    rc = GetResearch(self, GetLastResearchId(self))
    return rc

def GetLastResearchId(self):
    cur = self.conn.cursor()
    cur.execute("SELECT id FROM research ORDER BY id DESC LIMIT 1")
    prec = cur.fetchone()
    return prec[0]

def nGetResearch(self, project_id):
    cur = self.conn.cursor()
    cur.execute("SELECT id, name, status, date, description FROM research "
                "WHERE project_id = %s", (project_id, ))
    prec = cur.fetchall()
    rc = []
    if prec:
        for p in prec:
            rc += [{
                "id" : p[0],
                "date" : p[3],
                "name" : p[1],
                "description" : p[4],
                "status": p[2],
            }]
    return rc

def nGetResearchU(self):
    cur = self.conn.cursor()
    cur.execute("SELECT research.id, research.date, research.name, research.description "
                "FROM research, user2research WHERE research.id = user2research.research_id "
                "AND (user2research.user_id = %s OR user2research.invited_id = %s) "
                "GROUP BY research.id", (self.get_cookie("user_id"), self.get_cookie("user_id")))
    prec = cur.fetchall()
    rc = []
    for p in prec:
        rc += [{"id":p[0], "date":p[1], "name":p[2], "description":p[3]}]
    return rc

def GetParticipants(self, project_id):
    cur = self.conn.cursor()
    cur.execute("SELECT COUNT(user2research.user_id) FROM research, user2research "
                "WHERE user2research.research_id = research.id AND research.project_id = %s",
                (project_id,))
    pc = cur.fetchone()
    return pc[0]+1

def GetUser(self):
    cur = self.conn.cursor()
    cur.execute("SELECT id, tarif_id, name, email, subscribe, passwd FROM \"user\""
                "WHERE id = %s",(self.get_cookie("user_id"),))
    prec = cur.fetchone()
    usr = {"id": prec[0], "name": prec[2], "email": prec[3], "subscribe": prec[4], "passwd": prec[5]}
    return usr

def GetSub(self):
    cur = self.conn.cursor()
    cur.execute("SELECT subscribe FROM \"user\""
                "WHERE id = %s",(self.get_cookie("user_id"),))
    prec = cur.fetchone()
    return {
        'never': ['checked', '', '', ''],
        'asis': ['', 'checked', '', ''],
        'daily':['', '', 'checked', ''],
        'week': ['', '', '', 'checked'],
    }.get(prec[0], '')

def GetScore(self, project_id):
    sc = 71
    return sc

def GetMethod(self):
    cur = self.conn.cursor()
    cur.execute("SELECT id, parent_id, name FROM method")
    p_md = []
    md = []
    sub = []
    parent = 1
    prec = cur.fetchall()
    for p in prec:
        if p[0] == p[1]:
            p_md += [p[2]]
        else:
            if parent == p[1]:
                sub += [{"id":p[0], "name":p[2]}]
            else:
                md += [sub]
                parent = p[1]
                sub = []
    return [p_md, md]

def GetCheckedMethod(self):
    cur = self.conn.cursor()
    cur.execute("SELECT id, parent_id, name, type, tester FROM method")
    prec = cur.fetchall()
    checked = self.request.arguments['characters']
    parent = 1
    p_id = [parent]
    p_md = []
    sub = []
    md = []
    for p in prec:
        if str(p[0]) in checked:
            if parent == p[1]:
                sub += [{"id":p[0], "name":p[2], "type":p[3], "tester":p[4]}]
                cur.execute("INSERT INTO research2method(research_id, method_id) VALUES ( %s, %s)",
                            (GetLastResearchId(self), p[0],))
                self.conn.commit()
            else:
                md += [sub]
                parent = p[1]
                p_id += [parent]
                sub = []

    for p in prec:
        if p[0] in p_id:
            p_md += [p[2]]
    return [p_md, md]

def GetResearchMethod(self):
    cur = self.conn.cursor()
    cur.execute("SELECT method.id, method.parent_id, method.name, method.type, method.tester "
                "FROM research2method, method WHERE research2method.method_id = method.id AND "
                "research2method.research_id = %s", (GetLastResearchId(self),))
    prec = cur.fetchall()
    parent = 1
    p_md = []
    sub = []
    md = []
    for p in prec:
        if parent == p[1]:
            sub += [{"id":p[0], "name":p[2], "type":p[3], "tester":p[4]}]
        else:
            md += [sub]
            sub = []
            parent = p[1]

    p_md = ['Надёжность', 'Единообразие']

    return [p_md, md]

class BaseHandler(tornado.web.RequestHandler):
    @property
    def conn(self):
        try:
            conn = psycopg2.connect("dbname=app user=larasorokina password=qwerty host='localhost' password='dbpass'")
            conn.autocommit = True
            return conn
        except:
            print "Unable to connect to the database"

class MainHandler(BaseHandler):
    def get(self):
        self.render("index.html")

class LoginHandler(BaseHandler):
    def get(self):
        self.render("login.html")

    def post(self):
        if LoginUser(self):
            self.render("projects.html", projects = nGetProject(self))
        else:
            self.render("login.html")

class RegisterHandler(BaseHandler):
    def get(self):
        self.render("register.html")

    def post(self):
        to = self.get_argument("email")
        # isert app email
        gmail_user = ''
        # isert email password
        gmail_pwd = ''
        smtpserver = smtplib.SMTP("smtp.mail.ru", 465)
        smtpserver.ehlo()
        smtpserver.starttls()
        smtpserver.ehlo()
        smtpserver.login(gmail_user, gmail_pwd)
        header = 'To:' + to + '\n' + 'From: ' + gmail_user + '\n' + 'Subject: Вас пригласили для тестирования нового проекта\n'
        msg = header.encode('utf-8') + "meow"
        smtpserver.sendmail(gmail_user, to, msg)
        smtpserver.close()
        print "done"
        self.set_header("Content-Type", "html5")
        self.write(self.get_argument("mes"))
        self.render("login.html")

class ProjectHandler(BaseHandler):
    def get(self, url):
        pui = self.get_argument("project_id")
        self.render("project.html",
                    researchs = nGetResearch(self, pui),
                    project = GetProject(self, pui),
                    participants_count = GetParticipants(self, pui),
                    score = GetScore(self, pui))

class ProjectsHandler(BaseHandler):
    def get(self):
        self.render("projects.html", projects = nGetProject(self))

class ResearchHandler(BaseHandler):
    def get(self, url):
        self.render("research.html",
                    project = GetProject(self, self.get_argument("project_id")),
                    research = GetResearch(self, GetLastResearchId(self)),
                    parent_methods = GetResearchMethod(self)[0],
                    methods = GetResearchMethod(self)[1])

    def post(self, url):
        rs = ["да", "нет", "5", "нет", "да","4"]
        sc = 76
        pr = GetProject(self)
        print "meow"
        self.render("result.html",
                    project = pr,
                    research = GetResearch(GetLastResearchId(self)),
                    participants_count = GetParticipants(pr["id"]),
                    parent_methods = GetResearchMethod(self)[0],
                    methods = GetResearchMethod(self)[1],
                    result = rs,
                    score  = sc)

class SettingsHandler(BaseHandler):
    def get(self, url):
        self.render("profile.html", person = GetUser(self), sub = GetSub(self))

class ActivityHandler(BaseHandler):
    def get(self, url):
        self.render("timeline.html", researchs = nGetResearchU(self))

class PrepareHandler(BaseHandler):
    def get(self, url):
        self.render("prepare.html",
                    project = GetProject(self,self.get_argument("project_id")),
                    parent_methods = GetMethod(self)[0],
                    methods = GetMethod(self)[1],
                    research_id = GetLastResearchId(self))

    def post(self, url):
        GetCheckedMethod(self)
        self.redirect("research.html?project_id="+self.get_argument("project_id"))
        # self.render("research.html",
        #             project = GetProject(self, self.get_argument("project_id")),
        #             research = GetResearch(self, GetLastResearchId(self)),
        #             parent_methods = GetCheckedMethod(self)[0],
        #             methods = GetCheckedMethod(self)[1])

class ResultHandler(BaseHandler):
    def get(self, url):
        rs = ["да", "нет", "5", "нет", "да","4"]
        sc = 75
        self.render("result.html",
                    project = GetProject(self, self.get_argument("project_id")),
                    research = GetResearch(self, GetLastResearchId(self)),
                    participants_count = GetParticipants(self,self.get_argument("project_id")),
                    parent_methods = GetResearchMethod(self)[0],
                    methods = GetResearchMethod(self)[1],
                    result = rs,
                    score  = sc)

    @property
    def mail_connection(self):
        return self.application.mail_connection

    def post(self):
        # to = self.get_argument("email")
        # # isert app email
        # gmail_user = ''
        # # isert email password
        # gmail_pwd = ''
        # smtpserver = smtplib.SMTP("smtp.mail.ru", 465)
        # smtpserver.ehlo()
        # smtpserver.starttls()
        # smtpserver.ehlo()
        # smtpserver.login(gmail_user, gmail_pwd)
        # header = 'To:' + to + '\n' + 'From: ' + gmail_user + '\n' + 'Subject: Результаты тестирования вашего проекта\n'
        # msg = header.encode('utf-8') + "meow"
        # smtpserver.sendmail(gmail_user, to, msg)
        # smtpserver.close()
        # self.set_header("Content-Type", "html5")
        # self.write(self.get_argument("mes"))

        rs = ["да", "нет", "5", "нет", "да","4"]
        sc = 75
        self.render("result.html",
                    project = GetProject(self, self.get_argument("project_id")),
                    research = GetResearch(self, GetLastResearchId(self)),
                    participants_count = GetParticipants(self,self.get_argument("project_id")),
                    parent_methods = GetResearchMethod(self)[0],
                    methods = GetResearchMethod(self)[1],
                    result = rs,
                    score  = sc)

class AddProjectHandler(BaseHandler):
    def get(self):
        self.render("add_project.html")

    def post(self):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO project (user_id, name, description) VALUES (%s, %s, %s)",
                   (self.get_cookie("user_id"), self.get_argument("project"),
                    self.get_argument("description"),))
        self.render("projects.html", projects = nGetProject(self))

class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
			template_path = os.path.join(os.path.dirname(__file__), "templates").decode('utf-8'),
			static_path = os.path.join(os.path.dirname(__file__), "static").decode('utf-8'),
            cookie_secret = "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
			debug=True,
			autoescape=None,
			)

        handlers = [
            (r".", MainHandler),
            (r"/index.html", MainHandler),
            (r"/login.html", LoginHandler),
            (r"/project.html/(.*)", ProjectHandler,),
            (r"/projects.html", ProjectsHandler),
            (r"/research.html(.*)", ResearchHandler),
            (r"/profile.html(.*)", SettingsHandler),
            (r"/timeline.html(.*)", ActivityHandler),
            (r"/prepare.html(.*)", PrepareHandler),
            (r"/result.html(.*)", ResultHandler),
            (r"/add_project.html", AddProjectHandler),
            (r"/register.html", RegisterHandler),
            (r'/(favicon\.ico)', tornado.web.StaticFileHandler, {"path": settings["static_path"]}),
        ]
        tornado.web.Application.__init__(self, handlers, **settings)

if __name__ == "__main__":
    app = Application()
    app.listen(8888)
    tornado.ioloop.IOLoop.instance().start()