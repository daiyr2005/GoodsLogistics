import asyncio
import logging
import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from mysite.api.deps import get_db
from mysite.chain.chat_chain import chat_chain
from mysite.db.model import Product
from mysite.db.schema import ChatInputSchema, ChatOutputSchema

logger = logging.getLogger(__name__)
ai_router = APIRouter(prefix="/ai", tags=["AI Assistant"])

STOP = {"найди", "покажи", "мне", "все", "всё", "доступные", "в", "каталоге",
        "каталог", "есть", "какие", "по", "из", "для", "до"}

# слова-синонимы, чтобы «смартфоны» находили «iPhone», «Galaxy» и т.д.
SYNONYMS = {
    "смартфон": ["phone", "iphone", "galaxy", "смартфон"],
    "телефон": ["phone", "iphone", "galaxy", "смартфон"],
}


def find_products(db: Session, question: str, limit: int = 15) -> list[dict]:
    words = [w for w in re.findall(r"[a-zа-яё0-9]+", question.lower())
             if w not in STOP and not w.isdigit() and len(w) > 2]

    patterns = set()
    for w in words:
        stem = w[:6]  # грубое сокращение окончаний: «смартфоны» -> «смартф»
        patterns.add(f"%{stem}%")
        for key, vals in SYNONYMS.items():
            if w.startswith(key[:6]):
                patterns.update(f"%{v}%" for v in vals)

    query = select(Product)
    if patterns:
        query = query.where(or_(*[
            c.ilike(p) for p in patterns
            for c in (Product.product_name, Product.description)
        ]))

    seen, items = set(), []
    for p in db.scalars(query.limit(limit * 3)).all():
        key = (p.product_name, str(p.price))
        if key in seen:           # убираем дубли (как два Galaxy S24)
            continue
        seen.add(key)
        items.append({
            "id": p.id,
            "product_name": p.product_name,
            "price": float(p.price),
            "store_id": p.store_id,
            "is_original": p.is_original,
            "description": p.description,
        })
        if len(items) >= limit:
            break
    return items

def clean_answer(text: str) -> str:      # <-- сюда
    text = re.sub(r"[*_`#]+", "", text)       # markdown
    text = re.sub(r"\s*\n+\s*", " ", text)    # переносы строк
    return text.strip()


@ai_router.post("/chat/", response_model=ChatOutputSchema)
async def chat(data: ChatInputSchema, db: Session = Depends(get_db)):
    question = data.question.strip()
    if not question:
        raise HTTPException(status_code=422, detail="Вопрос не может быть пустым")

    try:
        items = find_products(db, question)
        if not items:
            return ChatOutputSchema(answer="В каталоге ничего не найдено", items=[])

        products = "\n".join(
            f"- {i['product_name']}, {int(i['price'])} сом" for i in items
        )
        answer = await asyncio.wait_for(
            chat_chain.ainvoke({"question": question, "products": products}),
            timeout=120,
        )
        return ChatOutputSchema(answer=clean_answer(answer), items=items)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="AI не ответил за отведённое время")
    except Exception:
        logger.exception("Ошибка AI")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка AI")