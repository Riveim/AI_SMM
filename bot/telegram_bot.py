import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from sqlalchemy import select
from app.config import settings
from app.database import AsyncSessionLocal
from app.models import Business, Product, PromptTemplate, ChatMessage
from app.ai import get_ai_reply

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Хранение истории диалогов в памяти (chat_id -> список сообщений)
# Для production лучше хранить в Redis или БД
conversation_history: dict[str, list[dict]] = {}


async def get_business_context(business_id: int):
    """Загружает бизнес, товары и активный шаблон промпта."""
    async with AsyncSessionLocal() as db:
        business = (await db.execute(
            select(Business).where(Business.id == business_id)
        )).scalar_one_or_none()

        if not business:
            return None, [], None

        products = (await db.execute(
            select(Product).where(Product.business_id == business_id)
        )).scalars().all()

        template = (await db.execute(
            select(PromptTemplate).where(
                PromptTemplate.business_id == business_id,
                PromptTemplate.platform == "telegram",
                PromptTemplate.content_type == "reply",
                PromptTemplate.is_active == True,
            )
        )).scalar_one_or_none()

        return business, list(products), template


async def save_message(business_id: int, chat_id: str, username: str | None, message: str, reply: str):
    """Сохраняет сообщение и ответ в БД."""
    async with AsyncSessionLocal() as db:
        record = ChatMessage(
            business_id=business_id,
            telegram_chat_id=chat_id,
            sender_username=username,
            message=message,
            ai_reply=reply,
        )
        db.add(record)
        await db.commit()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Здравствуйте! Чем могу помочь? 👋"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    username = update.effective_user.username
    user_message = update.message.text

    # business_id берётся из переменной окружения или bot_data
    # Каждый бот привязан к одному бизнесу
    business_id = context.bot_data.get("business_id", 1)

    business, products, template = await get_business_context(business_id)

    if not business:
        await update.message.reply_text("Сервис временно недоступен.")
        return

    # Получаем историю диалога
    history = conversation_history.get(chat_id, [])

    try:
        # Показываем "печатает..."
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")

        reply = await get_ai_reply(user_message, business, products, template, history)

        # Обновляем историю
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": reply})
        # Храним только последние 20 сообщений
        conversation_history[chat_id] = history[-20:]

        await update.message.reply_text(reply)

        # Сохраняем в БД асинхронно
        await save_message(business_id, chat_id, username, user_message, reply)

    except Exception as e:
        logger.error(f"Ошибка при генерации ответа: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")


def run_bot(business_id: int = 1):
    app = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Привязываем бизнес к боту
    app.bot_data["business_id"] = business_id

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info(f"Бот запущен для бизнеса ID={business_id}")
    app.run_polling(drop_pending_updates=True)
