from openai import AsyncOpenAI
from app.config import settings
from app.models import Business, Product, PromptTemplate

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


def build_system_prompt(business: Business, products: list[Product], template: PromptTemplate | None) -> str:
    """Собирает системный промпт из данных бизнеса."""

    products_text = ""
    if products:
        lines = []
        for p in products:
            line = f"- {p.name}"
            if p.description:
                line += f": {p.description}"
            if p.price:
                line += f" (цена: {p.price})"
            lines.append(line)
        products_text = "Товары и услуги:\n" + "\n".join(lines)

    keywords_text = ""
    if business.keywords:
        keywords_text = "Ключевые слова: " + ", ".join(business.keywords)

    # Если есть кастомный шаблон — используем его
    if template:
        prompt = template.template
        prompt = prompt.replace("{business_name}", business.name)
        prompt = prompt.replace("{description}", business.description or "")
        prompt = prompt.replace("{tone}", business.tone)
        prompt = prompt.replace("{target_audience}", business.target_audience or "")
        prompt = prompt.replace("{products}", products_text)
        prompt = prompt.replace("{keywords}", keywords_text)
        return prompt

    # Стандартный промпт
    return f"""Ты — ИИ-ассистент компании "{business.name}".

{f"О компании: {business.description}" if business.description else ""}
Тон общения: {business.tone}
{f"Целевая аудитория: {business.target_audience}" if business.target_audience else ""}
{products_text}
{keywords_text}

Отвечай на вопросы клиентов от лица компании. Будь вежливым, полезным и придерживайся указанного тона.
Если вопрос не относится к компании или продуктам — вежливо перенаправь к теме бизнеса.
Отвечай кратко и по делу."""


async def get_ai_reply(
    user_message: str,
    business: Business,
    products: list[Product],
    template: PromptTemplate | None = None,
    history: list[dict] | None = None,
) -> str:
    """Отправляет сообщение в OpenAI и возвращает ответ."""
    system_prompt = build_system_prompt(business, products, template)

    messages = [{"role": "system", "content": system_prompt}]

    # Добавляем историю переписки (последние 10 сообщений)
    if history:
        messages.extend(history[-10:])

    messages.append({"role": "user", "content": user_message})

    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=messages,
        max_tokens=500,
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()
