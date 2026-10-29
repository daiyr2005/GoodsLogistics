from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from mysite.config import OLLAMA_URL, OLLAMA_MODEL
from mysite.db.schema.order_schema import OrderListOutputSchema


parser = PydanticOutputParser(
    pydantic_object=OrderListOutputSchema
)

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        Ты помощник по подбору товаров.

        Определи, какие товары ищет пользователь.
        Сформируй короткий ответ на русском языке.
        Не придумывай товары, идентификаторы, цены и характеристики.
        Если каталог товаров не предоставлен, верни пустой список items.

        {format_instructions}
        """
    ),
    ("human", "Запрос пользователя: {text}")
]).partial(
    format_instructions=parser.get_format_instructions()
)

model = ChatOllama(
    model=OLLAMA_MODEL,
    base_url=OLLAMA_URL,
    temperature=0,
    num_predict=500
)

order_chain = prompt | model | parser