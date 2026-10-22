"""End-to-end check of the creator loop. Needs the site on :3000 with DEV_LOGIN=1, the MCP
server running, and `pip install playwright mcp`. Run: python e2e_test.py <folder for screenshots>"""
import asyncio, json, re, sys
from playwright.async_api import async_playwright
from mcp.client.streamable_http import streamable_http_client
from mcp import ClientSession
S = sys.argv[1]
async def make_video(address):
    script = json.load(open("/home/claude/cevg/examples/binary_search.json", encoding="utf-8"))
    script["canvas"]["width"], script["canvas"]["height"] = 960, 540
    async with streamable_http_client(address) as streams:
        async with ClientSession(streams[0], streams[1]) as s:
            await s.initialize()
            r = await s.call_tool("render", {"script": script, "voice": False, "captions": True, "language": "te"})
            assert not r.is_error, r.content[0].text
            job = r.structured_content["job"]
            while True:
                st = (await s.call_tool("status", {"job": job})).structured_content
                if st["state"] in ("done", "failed"): return st
                await asyncio.sleep(1)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={"width": 1200, "height": 900}, color_scheme="dark")
        page = await ctx.new_page()
        await page.goto("http://localhost:3000/login")
        await page.fill('input[name="name"]', "Asha Rao")
        await page.click("text=Sign in without Google")
        await page.wait_for_url("**/dashboard")
        address = await page.inner_text(".copy code")
        print("address:", re.sub(r"/u/[^/]+/", "/u/<token>/", address))
        st = await make_video(address); print(st)
        await page.reload(); await page.screenshot(path=f"{S}/dash.png", full_page=True)
        await page.goto(st["watch_url"]); await page.screenshot(path=f"{S}/watch_private.png", full_page=True)
        # logged-out visitor cannot see a private video
        anon = await (await b.new_context()).new_page()
        r = await anon.goto(st["watch_url"]); print("anon private page:", r.status)
        r = await anon.request.get(st["watch_url"].replace("/v/", "/api/videos/") + "/file"); print("anon private file:", r.status)
        await page.click("text=Make public"); await page.wait_for_selector("text=Make private")
        r = await anon.goto(st["watch_url"]); print("anon public page:", r.status)
        r = await anon.request.get(st["watch_url"].replace("/v/", "/api/videos/") + "/file", headers={"range": "bytes=0-99"}); print("range:", r.status, r.headers.get("content-range"))
        await anon.goto("http://localhost:3000/"); await anon.screenshot(path=f"{S}/home.png", full_page=True)
        r = await anon.goto("http://localhost:3000/u/asha-rao"); print("creator page:", r.status, await anon.inner_text("p.muted"))
        m = await (await b.new_context(viewport={"width": 390, "height": 800})).new_page()
        await m.goto(st["watch_url"]); await m.screenshot(path=f"{S}/mobile.png", full_page=True)
        print("mobile overflow:", await m.evaluate("document.documentElement.scrollWidth > window.innerWidth"))
        await b.close()
asyncio.run(main())
