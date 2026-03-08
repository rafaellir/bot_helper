from database.repository import Repository

class Matcher:
    def __init__(self):
        self.repo = Repository()

    def match(self, url):
        return self.repo.find_task_by_url(url)