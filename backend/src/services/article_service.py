from markdown import markdown

from domain.entities.article import Article


class ArticleService:
    def convert_to_html(self, article: Article):
        if article.content:
            return markdown(article.content)

    async def save(self, article: Article): ...

    async def get_recommendations(self, article: Article) -> list[Article]: ...
