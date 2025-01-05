from functools import partial
from typing import (
    Callable,
    Any,
)

from flet import (
    Card,
    Column,
    Container,
    ControlEvent,
    Page,
    TextButton,
    TextField,
)


async def action(e: ft.ControlEvent, *, form: List[ft.TextField]):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=url,
            data={
                "username": form[0].value,
                "password": form[1].value,
            },
        )
    e.page.session.set("token", response)


def Form(
    action: Callable[[Any], Any],
    target: Session | None = None,
    method: str = "post",
):
    def build(*args, **kwargs):
        return Card(
            expand=False,
            content=Container(
                content=Column(
                    controls=[
                        TextField(),
                        TextField(),
                        TextButton("Submit", onclick=partial(action, target)),
                    ]
                )
            ),
        )

    return build
