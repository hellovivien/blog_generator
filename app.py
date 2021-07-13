
import transformers
import random
import requests
import json
from fake_useragent import UserAgent
import people_also_ask
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine, Model, EmbeddedModel
from typing import List
from datetime import datetime

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
client = AsyncIOMotorClient("adresse de ta base mongodb: https://www.mongodb.com/try")
engine = AIOEngine(motor_client=client, database="blog")


class Article(EmbeddedModel):
    title: str
    content: str

class ArticleGenerator(EmbeddedModel):
    model_name: str    

class Blog(Model):
    title: str
    keywords: List[str]
    questions: List[str]
    generator: ArticleGenerator
    articles: List[Article]
    created_at: datetime

class BlogGenerator():

    query_url = 'https://suggestqueries.google.com/complete/search?output=chrome&hl=en&gl=us&q='
    
    def __init__(self, topic, model_name, max_articles=5, max_length=300, max_questions_by_keyword=5):
        self.topic = topic
        self.max_articles = max_articles
        self.max_length = max_length
        self.max_questions_by_keyword = max_questions_by_keyword
        self.generator = ArticleGenerator(model_name=model_name)
        self.articles = []
        self.related_questions = []
        self.keywords = []

    def get_keywords(self):
        ua = UserAgent()
        headers = {"user-agent": ua.chrome}
        url = self.query_url+self.topic 
        response = requests.get(url, headers=headers, verify=False)
        suggestions = json.loads(response.text)
        self.keywords = suggestions[1]
        return len(self.keywords) != 0      

    def get_questions(self):
        for keyword in enumerate(self.keywords):
            print('Generate question for {}'.format(keyword))
            if len(self.related_questions) < self.max_articles:
                questions_asked = people_also_ask.get_related_questions(keyword, self.max_questions_by_keyword)
                for question in questions_asked:
                    if question not in self.related_questions:
                        self.related_questions.append(question)
                        print(question)
        return len(self.related_questions) != 0

    def generate_articles(self):       
        print("**Generate articles with GPT2...**")
        generator = transformers.pipeline('text-generation', model='gpt2')
        transformers.set_seed(42)
        related_questions = self.related_questions[0:self.max_articles]
        for i,question in enumerate(related_questions):
            content = generator(question, max_length=self.max_length, num_return_sequences=2)
            content = content[0]['generated_text'][len(question):]
            self.articles.append(Article(title=question, content=content))
            print('{}/{} article(s)'.format(i+1, self.max_articles))
        return len(self.articles) != 0

    def pipeline(self):
        if self.get_keywords():
            if self.get_questions():
                if self.generate_articles():
                    return True
        return False

async def main():
    gen = BlogGenerator('restaurant paris', 'gpt2', max_articles=4)
    if gen.pipeline():
        blog = Blog(title=gen.topic, keywords=gen.keywords, questions=gen.related_questions, generator=gen.generator, articles=gen.articles, created_at=datetime.now())
        await engine.save(blog)

if __name__ == "__main__":
    loop.run_until_complete(main())
