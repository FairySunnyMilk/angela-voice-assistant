import wikipediaapi
import pymorphy3


class Wiki:
    def __init__(self):
        self.morfh = pymorphy3.MorphAnalyzer()
        self.wiki_wiki = wikipediaapi.Wikipedia(
            user_agent="MyWikiBot/1.0 (contact: myemail@example.com)",
            language="ru"
            ) 

    def normal_wive(self, text:str) -> str:
        return " ".join([self.morfh.parse(word)[0].normal_form for word in text.split()])

    def search_in_wiki(self, question:str) -> None:
        question = self.normal_wive(question)  
        page = self.wiki_wiki.page(question)
        if page.exists():
            return page.summary.split('\n')[0]
        else:
            page = self.wiki_wiki.page(question.split()[-1])
            if page.exists():
                return page.summary.split('\n')[0]
            else:
                return 'Я не нашла информацию по вашему запросу'
