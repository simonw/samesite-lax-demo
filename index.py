from starlette.applications import Starlette
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.routing import Route
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
      <p>Set "lax-demo" cookie: <input type="text" name="demo">
      <input type="submit" value="Set SameSite=Lax cookie">
      </p>
    </form>
    <form action="/set-none" method="POST">
      <p>Set "none-demo" cookie: <input type="text" name="demo">
      <input type="submit" value="Set SameSite=None cookie">
      </p>
    </form>
    <form action="/set-strict" method="POST">
      <p>Set "strict-demo" cookie: <input type="text" name="demo">
      <input type="submit" value="Set SameSite=Strict cookie">
      </p>
    </form>
"""
        % repr(request.cookies)
    )


async def set_cookie(request, samesite="lax"):
    form_vars = await request.form()
    demo = form_vars.get("demo") or ""
    response = RedirectResponse("/", status_code=302)
    response.set_cookie("{}-demo".format(samesite), demo, samesite=samesite)
    return response


async def set_none(request):
    return await set_cookie(request, samesite="none")


async def set_strict(request):
    return await set_cookie(request, samesite="strict")


app = Starlette(
    routes=[
        Route("/", homepage, methods=["GET", "POST"]),
        Route("/set-lax", set_cookie, methods=["POST"]),
        Route("/set-none", set_none, methods=["POST"]),
        Route("/set-strict", set_strict, methods=["POST"]),
    ]
)
