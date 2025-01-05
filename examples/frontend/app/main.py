import httpx
import flet as ft
from typing import List
from functools import partial

from app.components import Form


async def onClick(e: ft.ControlEvent, *, form: List[ft.TextField]):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url="http://127.0.0.1:80/api/authorization-service/v1/sign-up",
            data={
                "username": form[0].value,
                "password": form[1].value,
            },
        )
    e.page.session.set("token", response)


class App:
    def __init__(self, page: ft.Page | None = None):
        self.page = page
        self.username = ft.Ref[ft.TextField]()
        self.password = ft.Ref[ft.TextField]()
        self.form = Form()

    def __call__(self, *args, **kwds):
        for arg in args:
            if isinstance(arg, (ft.Page)):
                self.page = arg
                break
        if self.page is not None:
            self.build()
        else:
            raise RuntimeError("Expected Page, got None")

    def build(self):
        self.page.add(
            ft.Column(
                controls=[
                    self.form(),
                    #                     ft.TextField(
                    #                         ref=self.username,
                    #                         hint_text="email",
                    #                     ),
                    #                     ft.TextField(
                    #                         ref=self.password,
                    #                         hint_text="password",
                    #                     ),
                    #                     ft.TextButton(
                    #                         content=ft.Text("Log in"),
                    #                         on_click=partial(
                    #                             onClick, form=[self.username.current, self.password.current]
                    #                         ),
                    #                     ),
                    #                     ft.TextButton(
                    #                         content=ft.Text("Refresh"),
                    #                         on_click=lambda e: print(self.page.session.get("token")),
                    #                     ),
                ]
            )
        )
