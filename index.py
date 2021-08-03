from starlette.applications import Starlette
from starlette.responses import Response, HTMLResponse, RedirectResponse, JSONResponse
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from pprint import pformat
import html
import time

PROJECT_EPOCH = 1628017969


def relative_time():
    return int(time.time()) - PROJECT_EPOCH


async def homepage(request):
    cookie_info = []
    for name, value in request.cookies.items():
        if value.isdigit():
            value += " ({} seconds ago)".format(relative_time() - int(value))
        cookie_info.append("<li>{}={}</li>".format(name, value))
    return HTMLResponse(
        """
    <html>
    <head><title>SameSite=Lax demo</title>
    <style>body { font-family: verdana; margin: 1em 3em; }</style>
    </head>
    <body>
    <h1>SameSite=Lax demo</h1>
    <p>Current cookies: <code>%s</code></p>
    %s
    <p>Set all four cookies at once (recommended):</p>
    <form action="/set-all" method="POST">
      <input type="submit" value="Set all four demo cookies">
      </p>
    </form>
    <p>Or set them individually:</p>
    <form action="/set-lax" method="POST">
      <input type="submit" value="Set SameSite=Lax cookie called lax-demo">
      </p>
    </form>
    <form action="/set-none" method="POST">
      <input type="submit" value="Set SameSite=None cookie called none-demo">
      </p>
    </form>
    <form action="/set-strict" method="POST">
      <input type="submit" value="Set SameSite=Strict cookie called strict-demo">
      </p>
    </form>
    <form action="/set-missing" method="POST">
      <input type="submit" value="Set cookie with no SameSite at all called missing-demo">
      </p>
    </form>
    <p>Reset this demo:</p>
    <form action="/delete-all-cookies" method="POST">
      <input type="submit" value="Delete ALL cookies">
      </p>
    </form>
    <p>See your cookies as JSON: <a href="/cookies.json">/cookies.json</a></p>
    <p>Once you have set some cookies visit <a href="https://simonw.github.io/samesite-lax-demo/">https://simonw.github.io/samesite-lax-demo/</a> to try navigating back to this page.</p>
    <p>More information in <a href="https://github.com/simonw/samesite-lax-demo/blob/main/README.md">this README</a>.</p>
    <p>Cookies as an SVG image:</p>
    <img style="border: 2px solid red" src="/cookies.svg">
"""
        % (repr(request.cookies), "\n".join(cookie_info))
    )


async def set_cookie(request, samesite="lax", secure=False):
    response = RedirectResponse("/", status_code=302)
    name = samesite or "missing"
    response.set_cookie(
        "{}-demo".format(name), relative_time(), samesite=samesite, secure=secure
    )
    return response


async def set_none(request):
    return await set_cookie(request, samesite="none", secure=True)


async def set_strict(request):
    return await set_cookie(request, samesite="strict")


async def set_missing(request):
    return await set_cookie(request, samesite=None)


async def delete_all_cookies(request):
    response = RedirectResponse("/", status_code=302)
    for cookie in request.cookies:
        response.delete_cookie(cookie)
    return response


async def set_all(request):
    response = RedirectResponse("/", status_code=302)
    for samesite, secure in (
        ("lax", False),
        ("none", True),
        ("strict", False),
        (None, False),
    ):
        name = samesite or "missing"
        response.set_cookie(
            "{}-demo".format(name), relative_time(), samesite=samesite, secure=secure
        )
    return response


async def cookies_svg(request):
    lines = []
    for i, (name, value) in enumerate(request.cookies.items()):
        lines.append(
            '<text x="10" y="{y}" style="font: 4px sans-serif;">{name}={value}</text>'.format(
                y=10 + (i * 6), name=html.escape(name), value=html.escape(value)
            )
        )
    return Response(
        '<svg viewBox="0 0 400 80" xmlns="http://www.w3.org/2000/svg">{}</svg>'.format(
            "\n".join(lines)
        ),
        media_type="image/svg+xml;charset=utf-8",
    )


async def cookies_json(request):
    return JSONResponse(request.cookies)


async def favicon_ico(request):
    return Response("")


app = Starlette(
    routes=[
        Route("/", homepage, methods=["GET", "POST"]),
        Route("/favicon.ico", favicon_ico, methods=["GET"]),
        Route("/set-all", set_all, methods=["POST"]),
        Route("/set-lax", set_cookie, methods=["POST"]),
        Route("/set-none", set_none, methods=["POST"]),
        Route("/set-strict", set_strict, methods=["POST"]),
        Route("/set-missing", set_missing, methods=["POST"]),
        Route("/delete-all-cookies", delete_all_cookies, methods=["POST"]),
        Route("/cookies.svg", cookies_svg, methods=["GET"]),
        Route("/cookies.json", cookies_json, methods=["GET", "POST"]),
    ],
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=["https://simonw.github.io"],
            allow_methods=["*"],
            allow_credentials=True,
        )
    ],
)
