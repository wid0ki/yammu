# -*- coding: utf-8 -*-
# © 2012, Lara Sorokina, KubSAU
__author__ = 'wid0ki <laricasorokina@gmail.com>'

import os.path
import tornado.ioloop
import tornado.web

def Logic():
    pass

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("login.html")

    def post(self):
        self.set_secure_cookie("user", self.get_argument("name"))
        self.redirect("/projects.html")

class ProjectHandler(tornado.web.RequestHandler):
    def get(self, url):
        img = os.path.join("/static", "img", "1mbank.png").decode('utf-8')
        pr = {"name" : "Проект банка",
              "id" : self.get_argument("project_id"),
              "image_path": img,
              'description': 'Мы показываем здесь калькулятор для тех, кто попал на страницу заявки, минуя продуктовые, и перечисляем список избранного перед полями для заполнения. А еще можно выбрать какую-то услугу для себя, например, заказать кредитную карту, и оформить такой же пластик для своих сотрудников. Услуги для бизнеса и частных лиц в одной заявке.'}
        pc = 5
        rc = [{"id":0, "date":"27.05.2015", "description": "Тестирование банка"},
              {"id":1, "date":"17.06.2015", "description": "Тестирование страницы входа"},]
        self.render("project.html",
                    researchs = rc,
                    project = pr,
                    participants_count = pc)

class ProjectsHandler(tornado.web.RequestHandler):
    def get(self):
        img1 = os.path.join("/static", "img", "1mbank.png").decode('utf-8')
        img2 = os.path.join("/static", "img", "ebank.png").decode('utf-8')
        img3 = os.path.join("/static", "img", "sklad.png").decode('utf-8')
        img4 = os.path.join("/static", "img", "eda.png").decode('utf-8')
        prs = [{"name":"Банк Первомайский", "id":0, "image_path": img1},
               {"name":"ИБ Первомайский", "id":1, "image_path": img2},
               {"name":"Южный склад", "id":3, "image_path": img3},
               {"name":"IRecommend", "id":4, "image_path": img4},]
        self.render("projects.html", projects = prs)

class ResearchHandler(tornado.web.RequestHandler):
    def get(self):

        self.render("research.html")

class SettingsHandler(tornado.web.RequestHandler):
    def get(self, url):
        pr = {'name':'Larisa', 'email':'widoki@me.com'}
        self.render("profile.html", person = pr)

class ActivityHandler(tornado.web.RequestHandler):
    def get(self, url):
        rc = [{"id":0, "date":"27.05.2015", "description": "Тестирование банка"},
              {"id":1, "date":"17.06.2015", "description": "Тестирование страницы входа"},
              {"id":2, "date":"17.06.2015", "description": "Тестирование страницы входа"},]
        self.render("timeline.html", researchs = rc)

class PrepareHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("prepare.html")

class ResultHandler(tornado.web.RequestHandler):
    def get(self, url):
        pr = {"name" : "Проект банка",
              "id" : 1,
              "image_path": os.path.join("/static", "img", "1mbank.png").decode('utf-8'),
              'description': 'Мы показываем здесь калькулятор для тех, кто попал на страницу заявки, минуя продуктовые, и перечисляем список избранного перед полями для заполнения. А еще можно выбрать какую-то услугу для себя, например, заказать кредитную карту, и оформить такой же пластик для своих сотрудников. Услуги для бизнеса и частных лиц в одной заявке.'}
        pc = 47
        rc = {"id":0, "date":"27.05.2015", "name":"Проверка формы входа", "description": "Тестирование банка"}
        p_md = ["Надёжность", "Функциональность ресурса"]
        md = [[{"name":"Предотвращение пользовательских ошибок"},
               {"name":"Индикация возникновения случайных ошибок"},
               {"name":"Возможность отмены любого пользовательского действия (принцип Undo)"}],
             [{"name":"Достаточность необходимого функционала для решения пользовательских задач"},
              {"name":"Корректность работы функционала"},
              {"name":"Доступность функционала для пользователей"}],
            ]
        self.render("result.html",
                    project = pr,
                    research = rc,
                    participants_count = pc,
                    parent_methods = p_md,
                    methods = md)

class AddProjectHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("add_project.html")

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
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
        ]
        settings = dict(
			template_path = os.path.join(os.path.dirname(__file__), "templates").decode('utf-8'),
			static_path = os.path.join(os.path.dirname(__file__), "static").decode('utf-8'),
            cookie_secret = "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
			debug=True,
			autoescape=None,
			)
        tornado.web.Application.__init__(self, handlers, **settings)

if __name__ == "__main__":
    app = Application()
    app.listen(8888)
    tornado.ioloop.IOLoop.instance().start()