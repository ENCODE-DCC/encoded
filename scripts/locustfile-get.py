from locust import HttpLocust, TaskSet, task

'''
To use you must have python2 with pipinstalled locustion.
This script is not integrated with encoded or snovault python distribution
see http://locust.io
'''


def login(l):
    l.client.post("/login", {"username":"ellen_key", "password":"education"})


class UserBehavior(TaskSet):

    def on_start(self):
        # login(self)
        pass

    @task(1)
    def index(l):
        l.client.get("/")

    @task(2)
    def search(l):
        l.client.get("/experiments/ENCSR423SYP/?format=json&frame=embedded")

    @task(3)
    def demo_1(l):
        l.client.get("/experiments/ENCSR000EPU/?format=json&frame=embedded")
        l.client.get("/experiments/ENCSR328UMC/?format=json&frame=embedded")
        l.client.get("/experiments/ENCSR092WMD/?format=json&frame=embedded")

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000
