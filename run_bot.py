"""
Запуск Telegram бота отдельным процессом.
Использование: python run_bot.py --business-id 1
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from bot.telegram_bot import run_bot

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--business-id", type=int, default=1, help="ID бизнеса из БД")
    args = parser.parse_args()
    run_bot(business_id=args.business_id)
