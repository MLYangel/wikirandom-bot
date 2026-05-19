import os, asyncio, aiohttp
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.client.session.aiohttp import AiohttpSession
TOKEN = os.getenv("BOT_TOKEN")
PROXI = os.getenv("PROXY_URL")
if not TOKEN:
    raise ValueError("Нет BOT_TOKEN в переменных окружения")

API = "https://en.wikipedia.org/w/api.php"
WIKI_PARAM = {
    "action": "query", "generator": "random", "grnnamespace": 0,
    "prop": "extracts", "exintro": 1, "explaintext": 1, "format": "json"
}
AGENT = "WikiRandomBot/1.0 (https://t.me/random_wiki125bot; chara080807@gmail.com)"
async def sluch_stat(proxy=None):
    zagol = {"User-Agent": AGENT, "Accept": "application/json"}
    try:
        sess = aiohttp.ClientSession(headers=zagol)
        if proxy:
            sess._default_headers = zagol
            sess = aiohttp.ClientSession(headers=zagol, proxy=proxy) if proxy else aiohttp.ClientSession(headers=zagol)
    except:
        pass
    try:
        if proxy:
            async with aiohttp.ClientSession(headers=zagol, proxy=proxy) as s:
                async with s.get(API, params=WIKI_PARAM) as r:
                    if r.status != 200: return None
                    data = await r.json()
        else:
            async with aiohttp.ClientSession(headers=zagol) as s:
                async with s.get(API, params=WIKI_PARAM) as r:
                    if r.status != 200: return None
                    data = await r.json()
    except:
        return None
    try:
        stranici = data.get("query", {}).get("pages", {})
        if not stranici: return None
        pervaya = next(iter(stranici.values()))
        zagolovok = pervaya.get("title", "Без названия")
        tekst = pervaya.get("extract", "Нет описания")
        ssylka = f"https://en.wikipedia.org/wiki/{zagolovok.replace(' ', '_')}"
        return {"zagolovok": zagolovok, "tekst": tekst, "ssylka": ssylka}
    except:
        return None
router = Router()
@router.message(Command("start", "help"))
async def start_help(msg: types.Message):
    await msg.answer(
        "Привет! Я бот, который присылает случайные статьи из Википедии.\n\n"
        "Команды:\n"
        "/wiki_random — случайная статья\n"
        "/help — это сообщение"
    )
@router.message(Command("wiki_random"))
async def wiki_random(msg: types.Message):
    statya = await sluch_stat(proxy=PROXI)
    if not statya:
        await msg.answer("Не удалось получить статью. Попробуйте позже.")
        return
    otvet = (
        f"<b>{statya['zagolovok']}</b>\n\n"
        f"{statya['tekst']}\n\n"
        f"<a href='{statya['ssylka']}'>Читать полностью на Wikipedia</a>"
    )
    await msg.answer(otvet, parse_mode="HTML")
@router.message()
async def neizvestno(msg: types.Message):
    await msg.answer("Неизвестная команда. Используйте /help для списка команд.")

async def main():
    if PROXI:
        bot = Bot(token=TOKEN, session=AiohttpSession(proxy=PROXI))
    else:
        bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    print("Бот запущен. Ожидание сообщений...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())