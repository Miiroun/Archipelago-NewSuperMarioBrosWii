from BaseClasses import CollectionState
from collections import defaultdict, Counter
from typing import Callable, TYPE_CHECKING, Any
import logging
from MultiServer import mark_raw

from worlds.tracker_addons import register_function
if TYPE_CHECKING:
    from tracker.TrackerClient import TrackerCommandProcessor

logger = logging.getLogger("Client")

peek_stack:list[Any] = []

def peek_reset(self: "TrackerCommandProcessor"):
    """Reset the peek to the tracked world"""
    global peek_stack
    if self.ctx.tracker_core.player_id is None:
        logger.error("World not loaded, please connect")
        return
    world = self.ctx.tracker_core.get_current_world()
    peek_stack = [world]

@mark_raw
def peek_get_region(self: "TrackerCommandProcessor", argument:str=""):
    """Shortcut to go to a region directly"""
    global peek_stack
    peek_reset(self)
    if len(peek_stack) < 1:
        return #Already sent the error message
    world = peek_stack[0] #there should always be one item here
    assert world
    if argument in world.multiworld.regions.region_cache[world.player]:
        peek_stack.append(world.get_region(argument))

@mark_raw
def peek_get_location(self: "TrackerCommandProcessor", argument:str=""):
    """Shortcut to go to a region directly"""
    global peek_stack
    peek_reset(self)
    if len(peek_stack) < 1:
        return #Already sent the error message
    world = peek_stack[0] #there should always be one item here
    assert world
    if argument in world.multiworld.regions.location_cache[world.player]:
        peek_stack.append(world.get_location(argument))

@mark_raw
def peek_get_entrance(self: "TrackerCommandProcessor", argument:str=""):
    """Shortcut to go to a region directly"""
    global peek_stack
    peek_reset(self)
    if len(peek_stack) < 1:
        return #Already sent the error message
    world = peek_stack[0] #there should always be one item here
    assert world
    if argument in world.multiworld.regions.entrance_cache[world.player]:
        peek_stack.append(world.get_entrance(argument))


def peek_up(self: "TrackerCommandProcessor"):
    """Go up the peek stack"""
    global peek_stack
    if len(peek_stack) < 2:
        logger.error("Unable to peek up")
    else:
        peek_stack.pop() #yeet the bottom of the stack

@mark_raw
def peek_down(self: "TrackerCommandProcessor", argument:str=""):
    """Peek down into an atribute on the current object"""
    global peek_stack
    if len(peek_stack) < 1:
        logger.error("Debug tools not initalized, please run peek_reset to start debug tools")
        return
    down = getattr(peek_stack[-1],argument,None)
    if down is None:
        logger.error(f"Argument '{argument}' not found")
    else:
        peek_stack.append(down)
        logger.info(str(down))

def peek(self: "TrackerCommandProcessor"):
    """Print the current object"""
    global peek_stack
    if len(peek_stack) < 1:
        logger.error("Debug tools not initalized, please run peek_reset to start debug tools")
        return
    logger.info(str(peek_stack[-1]))

@mark_raw
def peek_key(self: "TrackerCommandProcessor", argument:str=""):
    """Subscript a mapping"""
    global peek_stack
    if len(peek_stack) < 1:
        logger.error("Debug tools not initalized, please run peek_reset to start debug tools")
        return
    current = peek_stack[-1]
    get_item = getattr(current, "__getitem__",None)
    if get_item is None:
        logger.error("Current doesn't appear to be subscriptable")
        return
    contains = getattr(current, "__contains__",None)
    down = None
    try:
        if contains is None or contains(argument):
            down = get_item(argument)
    except Exception as e:
        logger.error(str(e))
    if down is not None:
        peek_stack.append(down)
        logger.info(str(down))

@mark_raw
def peek_index(self: "TrackerCommandProcessor", argument:str=""):
    """Subscript a sequence"""
    global peek_stack
    if len(peek_stack) < 1:
        logger.error("Debug tools not initalized, please run peek_reset to start debug tools")
        return
    current = peek_stack[-1]
    get_item = getattr(current, "__getitem__",None)
    if get_item is None:
        logger.error("Current doesn't appear to be subscriptable")
        return
    if not argument.isdecimal():
        logger.error("Index must be numeric (i guess)")
        return
    new_argument = int(argument)
    try:
        down = get_item(new_argument)
        if down:
            peek_stack.append(down)
            logger.info(str(down))
    except Exception as e:
        logger.error(str(e))

def peek_pp(self: "TrackerCommandProcessor"):
    """Pretty print the current object (don't be crass)"""
    from pprint import pformat
    global peek_stack
    if len(peek_stack) < 1:
        logger.error("Debug tools not initalized, please run peek_reset to start debug tools")
        return
    current = peek_stack[-1]
    logger.info(pformat(current))

def peek_len(self: "TrackerCommandProcessor"):
    """Get length of current object"""
    global peek_stack
    if len(peek_stack) < 1:
        logger.error("Debug tools not initalized, please run peek_reset to start debug tools")
        return
    current = peek_stack[-1]
    temp_len = getattr(current,"__len__",None)
    if temp_len is None:
        logger.error("Cannot be len'd")
        return
    logger.info(temp_len())

def peek_keys(self: "TrackerCommandProcessor"):
    """Get the keys of the current object (by turning it into a list)"""
    global peek_stack
    if len(peek_stack) < 1:
        logger.error("Debug tools not initalized, please run peek_reset to start debug tools")
        return
    current = peek_stack[-1]
    temp_iter = getattr(current,"__iter__",None)
    if temp_iter is None:
        logger.error("Cannot get keys")
        return
    logger.info(str(list(temp_iter())))

def peek_dir(self: "TrackerCommandProcessor"):
    """Get the attributes of the current object (by using dir)"""
    global peek_stack
    if len(peek_stack) < 1:
        logger.error("Debug tools not initalized, please run peek_reset to start debug tools")
        return
    current = peek_stack[-1]
    logger.info(str(dir(current)))

def peek_rule(self: "TrackerCommandProcessor"):
    """Check the `access_rule` attribute of the current object"""
    global peek_stack
    if len(peek_stack) < 1:
        logger.error("Debug tools not initalized, please run peek_reset to start debug tools")
        return
    current = peek_stack[-1]
    assert current
    if hasattr(current, "access_rule"):
        state = self.ctx.updateTracker().state
        if state:
            logger.info(f"access_rule returns : {str(current.access_rule(state))}")
            if hasattr(current.access_rule,"explain_json"):
                self.ctx.print_json(current.access_rule.explain_json(state))

def peek_grule(self: "TrackerCommandProcessor"):
    """Check the `access_rule` attribute of the current object, but with the glitched state"""
    global peek_stack
    if len(peek_stack) < 1:
        logger.error("Debug tools not initalized, please run peek_reset to start debug tools")
        return
    current = peek_stack[-1]
    assert current
    if hasattr(current, "access_rule"):
        state = self.ctx.updateTracker().glitches_state
        if state:
            logger.info(f"access_rule returns : {str(current.access_rule(state))}")
            if hasattr(current.access_rule,"explain_json"):
                self.ctx.print_json(current.access_rule.explain_json(state))




register_function("peek_reset", peek_reset)
register_function("peek_get_region", peek_get_region)
register_function("peek_get_location", peek_get_location)
register_function("peek_get_entrance", peek_get_entrance)
register_function("peek_down", peek_down)
register_function("peek_up", peek_up)
register_function("peek", peek)
register_function("peek_index", peek_index)
register_function("peek_key", peek_key)
register_function("peek_pp",peek_pp)
register_function("peek_len", peek_len)
register_function("peek_keys", peek_keys)
register_function("peek_dir", peek_dir)
register_function("peek_rule", peek_rule)
register_function("peek_grule", peek_grule)