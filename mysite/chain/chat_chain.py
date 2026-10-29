from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama

from mysite.config import OLLAMA_URL, OLLAMA_MODEL

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "Ты помощник магазина. Отвечай только на русском, живым человеческим языком, "
     "одним коротким абзацем из 1-2 предложений. "
     "Не используй списки, звёздочки, markdown и переносы строк. "
     "Не пиши ссылки и бренды в скобках. "
     "Называй товар и цену. Используй только товары из данных. Не выдумывай. "
     "Если подходящих товаров нет, ответь: «В каталоге ничего не найдено»."),
    ("human", "Вопрос: {question}\n\nТовары:\n{products}"),
])

model = ChatOllama(
    model=OLLAMA_MODEL,
    base_url=OLLAMA_URL,
    temperature=0,
    num_predict=300,
    num_ctx=4096,
    keep_alive="30m",
)

chat_chain = prompt | model | StrOutputParser()