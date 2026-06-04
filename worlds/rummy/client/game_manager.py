from __future__ import annotations

import random


# isort: off
from kvui import GameManager, MDNavigationItemBase

# isort: on
from typing import TYPE_CHECKING, Any

from kivy._clock import ClockEvent
from kivy.clock import Clock
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.layout import Layout
from kivymd.uix.recycleview import MDRecycleView
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout


from ..Common import *
from ..game.game import Game
from ..game.graphics import Graphic
from .custom_views import (
    RummyControlsView,
    RummyGameView,
    RummyGrid,
    ConfettiView,
    TapIfConfettiCannonImage,
    TapImage,
    VolumeSliderView, RummyCardWidget,
)
from kivy.uix.relativelayout import RelativeLayout
from kivy.graphics import Rectangle

from .graphics import PlayerSprite, get_texture, get_rummy_texture, Texture
from .sounds import SoundManager

if TYPE_CHECKING:
    from .rummy_client import RummyContext


class RummyManager(GameManager):
    base_title = "Rummy for AP version"
    ctx: RummyContext

    lower_game_grid: Layout
    upper_game_grid: GridLayout

    game_view: MDRecycleView | None = None
    game_view_tab: MDNavigationItemBase

    sound_manager: SoundManager

    bottom_image_grid: list[list[Image]]
    top_image_grid: list[list[TapImage]]
    confetti_view: ConfettiView

    move_event: ClockEvent | None

    bottom_grid_is_grass: bool

    active_cards_widgets : list[Widget]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.sound_manager = SoundManager()
        self.sound_manager.allow_intro_to_play = not self.ctx.delay_intro_song
        self.top_image_grid = []
        self.bottom_image_grid = []
        self.move_event = None
        self.bottom_grid_is_grass = False

        self.active_cards_widgets = []

    def allow_intro_song(self) -> None:
        self.sound_manager.allow_intro_to_play = True

    def add_confetti(self, position: tuple[float, float], amount: int) -> None:
        self.confetti_view.add_confetti(position, amount)

    def play_jingle(self, audio_filename: str) -> None:
        self.sound_manager.play_jingle(audio_filename)

    def switch_to_tab(self, desired_tab: MDNavigationItemBase) -> None:
        if self.screens.current_tab == desired_tab:
            return
        self.screens.current_tab.active = False
        self.screens.switch_screens(desired_tab)
        desired_tab.active = True

    def switch_to_game_tab(self) -> None:
        self.switch_to_tab(self.game_view_tab)

    def switch_to_regular_tab(self) -> None:
        self.switch_to_tab(self.tabs.children[-1])

    def game_started(self) -> None:
        self.switch_to_game_tab()
        if self.game_view is not None:
            self.game_view.force_focus()
        self.sound_manager.game_started = True

    def render(self, game: Game) -> None:
        pass

        # render bricks



        # render brick groups
        from pathlib import Path
        #self.lower_game_grid.add_widget(Image(source=r"C:\Users\Anton\Projekt\Programering\AP-development\Archipelago-NewSuperMarioBrosWii\worlds\rummy\game\graphics\cards\Cards Pixel Art - Pack (64x96)\black_blue.png"))
        #self.lower_game_grid.add_widget(Image(source=str(Path().absolute() / r"graphics\cards\Cards Pixel Art - Pack (64x96)\black_red.png")))

        if not self.active_cards_widgets:
            self.active_cards_widgets = []

            for card in game.gameboard.active_cards:
                img = RummyCardWidget(get_rummy_texture(card)) #RummyCard(choice(COLORS), choice(SYMBOLS)))
                img.pos = (random.gauss() * 500, random.gauss() * 500)
                self.lower_game_grid.add_widget(img)
                self.active_cards_widgets.append(img)

            #source=r"graphics/cards/Cards Pixel Art - Pack (64x96)/black_blue.png"))

        #self.setup_game_grid_if_not_setup(game)

        # This calls game.render(), which needs to happen to update the state of math traps
        #self.render_gameboard(game)
        # Only now can we check whether a math problem is active
        #self.render_background_game_grid((10,15), False)

        #self.render_item_column(game)

    def render_gameboard(self, game: Game) -> None:
        rendered_gameboard = game.render()

        for i in range(len(game.gameboard.active_cards) - game.allowed_cards):
            card = game.all_cards[len(game.gameboard.active_cards) - game.allowed_cards+i]
            img = RummyCardWidget(get_rummy_texture(card))  # RummyCard(choice(COLORS), choice(SYMBOLS)))
            img.pos = (random.gauss() * 500, random.gauss() * 500)
            self.lower_game_grid.add_widget(img)
            self.active_cards_widgets.append(img)



    def render_background_game_grid(self, size: tuple[int, int], grass: bool) -> None:
        if grass == self.bottom_grid_is_grass:
            return

        for row in range(size[1]):
            for column in range(size[0]):
                image = self.bottom_image_grid[row][column]

                if not grass:
                    image.color = (0.3, 0.3, 0.3)
                    image.texture = None
                    continue

                boss_room = (row in (0, 1, 2) and (size[1] - column) in (1, 2, 3)) or (row, column) == (3, size[1] - 2)
                if boss_room:
                    image.color = (0.45, 0.35, 0.1)
                    image.texture = None
                    continue
                image.texture = get_texture("Grass")
                image.color = (1.0, 1.0, 1.0)

        self.bottom_grid_is_grass = grass

    def setup_game_grid_if_not_setup(self, game: Game) -> None:
        if self.upper_game_grid.children:
            return


        return
        self.top_image_grid = []
        self.bottom_image_grid = []

        size =  (50,50)

        for row in range(size[1]):
            self.top_image_grid.append([])
            self.bottom_image_grid.append([])

            for column in range(size[0]):
                bottom_image = Image(fit_mode="fill", color=(0.3, 0.3, 0.3))
                self.lower_game_grid.add_widget(bottom_image)
                self.bottom_image_grid[-1].append(bottom_image)

                top_image = TapImage(lambda y=row, x=column: self.ctx.queue_auto_move(x, y), fit_mode="fill")
                self.upper_game_grid.add_widget(top_image)
                self.top_image_grid[-1].append(top_image)

            # Right side: Inventory
            image = Image(fit_mode="fill", color=(0.3, 0.3, 0.3))
            self.lower_game_grid.add_widget(image)

            image2 = TapIfConfettiCannonImage(lambda: self.ctx.confetti_and_rerender(), fit_mode="fill", opacity=0)
            self.upper_game_grid.add_widget(image2)

            self.top_image_grid[-1].append(image2)

    def start_auto_move(self) -> None:
        if self.move_event is not None:
            self.move_event.cancel()

        self.ctx.do_auto_move_and_rerender()

        self.move_event = Clock.schedule_interval(lambda _: self.ctx.do_auto_move_and_rerender(), 0.10)

    def build(self) -> Layout:
        container = super().build()

        self.game_view = RummyGameView(self.ctx.input_and_rerender)

        self.game_view_tab = self.add_client_tab(RUMMY_NAME, self.game_view)

        controls = RummyControlsView()

        self.add_client_tab("Controls", controls)

        game_container = self.game_view.ids["game_container"]
        self.lower_game_grid = FloatLayout()#RelativeLayout()
        self.upper_game_grid = RummyGrid()
        self.confetti_view = ConfettiView()
        game_container.add_widget(self.lower_game_grid)
        game_container.add_widget(self.upper_game_grid)
        game_container.add_widget(self.confetti_view)

        from kivy.uix.button import Button

        #self.lower_game_grid.add_widget(Button(text='World 2'))
        #self.upper_game_grid.add_widget(Button(text='World 3'))


        #game_container.bind(size=self.lower_game_grid.check_resize)
        #game_container.bind(size=self.upper_game_grid.check_resize)
        #game_container.bind(size=self.confetti_view.check_resize)

        volume_slider_container = VolumeSliderView()
        volume_slider = volume_slider_container.ids["volume_slider"]
        volume_slider.value = self.sound_manager.volume_percentage
        volume_slider.bind(value=lambda _, new_volume: self.sound_manager.set_volume_percentage(new_volume))

        self.grid.add_widget(volume_slider_container, index=3)

        Clock.schedule_interval(lambda dt: self.confetti_view.redraw_confetti(dt), 1 / 60)

        return container
