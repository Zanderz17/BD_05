class NewsArticle():
    def __init__(self, id=None, title=None, rank=None) -> None:
        self.id = id,
        self.title = title
        self.rank = rank

    def to_JSON(self):
        return {
            'id': self.id,
            'title': self.title,
            'rank': self.rank
        }
