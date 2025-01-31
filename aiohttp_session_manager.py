import aiohttp
import asyncio

class AiohttpSessionManager:
    _instance = None
    _session: dict[str, aiohttp.ClientSession] = {}

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AiohttpSessionManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    async def __aexit__(self, exc_type, exc, tb):
        for session in self._session.values():
            await session.close()

    def get_session(self, url: str) -> aiohttp.ClientSession:
        if url not in self._session:
            self._session[url] = aiohttp.ClientSession(url)
        return self._session[url]