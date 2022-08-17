from kivy.lang import Builder
from kivy.utils import get_color_from_hex

from kivymd.app import MDApp
from kivymd.uix.toolbar import MDTopAppBar

KV = '''
MDScreen:

    MDBoxLayout:
        id: box
        orientation: "vertical"
        spacing: "12dp"
        pos_hint: {"top": 1}
        adaptive_height: True
'''


class TestNavigationDrawer(MDApp):
    def build(self):
        self.theme_cls.material_style = "M3"
        return Builder.load_string(KV)

    def on_start(self):
        for type_height in ["medium", "large", "small"]:
            self.root.ids.box.add_widget(
                MDTopAppBar(
                    type_height=type_height,
                    headline_text=f"Headline {type_height.lower()}",
                    md_bg_color=get_color_from_hex("#2d2734"),
                    left_action_items=[["arrow-left", lambda x: x]],
                    right_action_items=[
                        ["attachment", lambda x: x],
                        ["calendar", lambda x: x],
                        ["dots-vertical", lambda x: x],
                    ],
                    title="Title" if type_height == "small" else ""
                )
            )


TestNavigationDrawer().run()