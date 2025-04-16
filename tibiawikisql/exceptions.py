
class AttributeParsingError(Exception):
    def __init__(self, cause: type[Exception]):
        super().__init__(f"{cause.__class__.__name__}: {cause}")


class ArticleParsingError(Exception):

    def __init__(self, article, cause: type[Exception]):
        super().__init__(f"Error parsing article: `{article.title}` | {cause.__class__.__name__}: {cause}")
