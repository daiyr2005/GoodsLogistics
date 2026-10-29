from langchain_core.messages import AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_ollama import ChatOllama
from mysite.config import OLLAMA_URL, OLLAMA_MODEL


answer_prompt = ChatPromptTemplate.from_messages(
    [
        (
            'system',
            "Ты готовишь текст ответа службы доставки. "
            "Ответ должен быть вежливым и на русском языке в 2-3 предложениях. "
            "Используй обращение клиента для понимания вопроса. "
            "Не представляй предположения клиента как проверенные факты. "
            "Не придумывай сроки, причины задержки, возвраты и компенсации. "
            "Не утверждай, что сотрудник уже выполнил действие, если этого нет в сведениях оператора. "
            "Если нужных сведений нет, сообщи, что информация требует уточнения, без обещаний. "
            "Верни только текст ответа клиенту."
        ),
        (
            'human',
            "Обращение клиента: {text}\n"
            "Сведения оператора: {facts}"
        ),
    ]
)


answer_model = ChatOllama(
    model=OLLAMA_MODEL,
    base_url=OLLAMA_URL,
    temperature=0,
    num_predict=250
)


def check_answer(response: AIMessage) -> AIMessage:
    if response.response_metadata.get('done_reason') == 'length':
        raise ValueError('Жообу толук чыкпай калды анткени чектелуу болчу')
    return response


answer_chain = answer_prompt | answer_model | RunnableLambda(check_answer) | StrOutputParser()

