from locust import HttpLocust, TaskSet, task
import re

class UserBehavior(TaskSet):
    def login(self):
        self.client.post("/login", {"username":"testUser", "password":"testpass"})

    @task(2)
    def index(self):
        self.client.get("/files/ENCFF445ANP")
        #arr = []
        #getFile = open('access.log', 'r')
        #for line in getFile:
            #match = re.findall(r'\"(.+?)\"', line)
            #if match and 'GET' in match[0]:
                #if not any(term in match[0] for term in ['limit=all', 'icon', '.png', '.ico', '@download']):
                    #print arr.append(match[0].split()[1]) 
        #self.client.get("/")

    @task(1)
    def profile(self):
        self.client.get("/profile")

    def on_start(self):
        self.login()

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait=5000
    max_wait=9000