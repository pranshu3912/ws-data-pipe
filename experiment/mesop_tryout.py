import mesop as me


def on_click(e: me.ClickEvent):
    state = me.state(State)
    state.count += 1
    me.navigate("/multi_page_nav/page_2")


@me.page(path="/multi_page_nav")
def main_page():
    me.button("Navigate to Page 2", on_click=on_click)


@me.page(path="/multi_page_nav/page_2")
def page_2():
    state = me.state(State)
    me.text(f"Page 2 - count: {state.count}")


@me.stateclass
class State:
    toggled: bool = False
    count:int=0


def on_change(event: me.SlideToggleChangeEvent):
    s = me.state(State)
    s.toggled = not s.toggled


@me.page(
    security_policy=me.SecurityPolicy(
        allowed_iframe_parents=["https://google.github.io"]
    ),
    path="/slide_toggle",
)
def app():
    me.slide_toggle(label="Slide toggle", on_change=on_change)
    s = me.state(State)
    me.text(text=f"Toggled: {s.toggled}")
