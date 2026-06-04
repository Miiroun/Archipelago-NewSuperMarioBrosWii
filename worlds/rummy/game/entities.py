from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, ClassVar

from .graphics import Graphic
from .items import ITEM_TO_GRAPHIC, Item
from .locations import Location


class Entity:
    solid: bool
    graphic: Graphic





class Empty(Entity):
    solid = False
    graphic = Graphic.EMPTY




class Door(Entity):
    solid = True

    is_open: bool = False

    closed_graphic: ClassVar[Graphic]

    def open(self) -> None:
        self.is_open = True
        self.solid = False

    @property
    def graphic(self) -> Graphic:
        if self.is_open:
            return Graphic.EMPTY
        return self.closed_graphic


#class KeyDoor(Door, InteractableMixin):
#   auto_move_attempt_passing_through = True
#
#   closed_graphic = Graphic.KEY_DOOR
#
   # def interact(self, player: Player) -> bool:
  #      if self.is_open:
 #           return False
#
 #       if not player.has_item(Item.KEY):
#            return False

#        player.remove_item(Item.KEY)
#
#        self.open()
#
#        return True

