from starlette.applications import Starlette
from starlette.responses import Response, HTMLResponse, RedirectResponse
from starlette.routing import Route
from pprint import pformat
import html


async def homepage(request):
    return HTMLResponse(
        """
    <html>
    <head><title>SameSite=Lax demo</title>
    <style>body { font-family: verdana; margin: 1em 3em; }</style>
    </head>
    <body>
    <h1>SameSite=Lax demo</h1>
    <p>Current cookies: <code>%s</code></p>
    <form action="/set-lax" method="POST">
      <p>Set "lax-demo" cookie: <input type="text" name="demo" value="lax-demo">
      <input type="submit" value="Set SameSite=Lax cookie">
      </p>
    </form>
    <form action="/set-none" method="POST">
      <p>Set "none-demo" cookie: <input type="text" name="demo" value="none-demo">
      <input type="submit" value="Set SameSite=None cookie">
      </p>
    </form>
    <form action="/set-strict" method="POST">
      <p>Set "strict-demo" cookie: <input type="text" name="demo" value="strict-demo">
      <input type="submit" value="Set SameSite=Strict cookie">
      </p>
    </form>
    <form action="/set-missing" method="POST">
      <p>Set "missing-demo" cookie: <input type="text" name="demo" value="missing-demo">
      <input type="submit" value="Set cookie with no SameSite at all">
      </p>
    </form>
    <form action="/delete-all-cookies" method="POST">
      <input type="submit" value="Delete ALL cookies">
      </p>
    </form>
    <p>Once you have set some cookies visit <a href="https://simonw.github.io/samesite-lax-demo/">https://simonw.github.io/samesite-lax-demo/</a> to try navigating back to this page.</p>
    <p>More information in <a href="https://github.com/simonw/samesite-lax-demo/blob/main/README.md">this README</a>.</p>
    <p>Cookies as an SVG image:</p>
    <img style="border: 2px solid red" src="/cookies.svg">
"""
        % repr(request.cookies)
    )


async def set_cookie(request, samesite="lax", secure=False):
    form_vars = await request.form()
    demo = form_vars.get("demo") or ""
    response = RedirectResponse("/", status_code=302)
    response.set_cookie(
        "{}-demo".format(samesite or "missing"), demo, samesite=samesite, secure=secure
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


app = Starlette(
    routes=[
        Route("/", homepage, methods=["GET", "POST"]),
        Route("/set-lax", set_cookie, methods=["POST"]),
        Route("/set-none", set_none, methods=["POST"]),
        Route("/set-strict", set_strict, methods=["POST"]),
        Route("/set-missing", set_missing, methods=["POST"]),
        Route("/delete-all-cookies", delete_all_cookies, methods=["POST"]),
        Route("/cookies.svg", cookies_svg, methods=["GET"]),
    ]
)
