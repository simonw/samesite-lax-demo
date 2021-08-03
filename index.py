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
    <form action="/set" method="POST">
      <p>Set "demo" cookie: <input type="text" name="demo">
      <input type="submit" value="Set cookie">
      </p>
    </form>
    """
        % repr(request.cookies)
    )


async def set_demo_cookie(request):
    form_vars = await request.form()
    demo = form_vars.get("demo") or ""
    response = RedirectResponse("/", status_code=302)
    response.set_cookie("demo", demo, samesite="lax")
    return response


app = Starlette(
    routes=[
        Route("/", homepage, methods=["GET", "POST"]),
        Route("/set", set_demo_cookie, methods=["POST"]),
    ]
)
