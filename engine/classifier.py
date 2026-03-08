from browser.detector import QuestionDetector

class QuestionClassifier:
    def __init__(self, page):
        self.detector = QuestionDetector(page)

    def classify(self):
        return self.detector.detect_type_fallback()