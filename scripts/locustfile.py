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
        l.client.get("/search")

    @task(3)
    def demo_1(l):
        l.client.get("/search/?searchTerm=skin")
        l.client.get("/search/?searchTerm=skin&type=Experiment")
        l.client.get("/search/?searchTerm=skin&type=Experiment&award.project=ENCODE")

    @task(4)
    def demo_2(l):
        l.client.get("/search")
        l.client.get("/search/?type=Annotation&organ_slims=skin+of+body")

    @task(5)
    def demo_3(l):
        l.client.get("/search/?searchTerm=skin")
        l.client.get("/search/?searchTerm=skin&type=Experiment")
        l.client.get("/search/?searchTerm=skin&type=Experiment&award.project=ENCODE")
        l.client.get("/search/?searchTerm=skin&type=Experiment&award.project=ENCODE&assay_title=total+RNA-seq")
        l.client.get("/search/?searchTerm=skin&type=Experiment&award.project=ENCODE&assay_title=total+RNA-seq&replicates.library.biosample.life_stage=adult")

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000
