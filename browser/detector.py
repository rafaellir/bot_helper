class QuestionDetector:
    def __init__(self, page):
        self.page = page

    def is_plurall_question(self):
        return "plurall.net" in self.page.url

    def get_question_id(self):
        return self.page.url

    def get_question_text(self):
        try:
            return self.page.inner_text("body")
        except:
            return ""

    def detect_type_fallback(self):
        if self.page.locator("textarea").count() > 0:
            return "discursiva"
        if self.page.locator("input[type=radio]").count() > 0:
            return "objetiva"
        return "leitura"  # Assume leitura se desconhecido