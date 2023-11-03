from .events import Event

from ..exceptions import InvalidEvent

class EventManager:
    def __init__(self, bot):
        self.bot = bot
        self.events = {
            "on_message": [],
            "on_guild_channel_delete": [],
            "on_guild_channel_create": [],
            "on_guild_channel_update": [],
            "on_guild_channel_pins_update": [],
            "on_guild_update": [],
            "on_guild_emojis_update": [],
            "on_guild_stickers_update": [],
            "on_audit_log_entry_create": [],
            "on_invite_create": [],
            "on_invite_delete": [],
            "on_webhooks_update": [],
            "on_member_join": [],
            "on_member_remove": [],
            "on_raw_member_remove": [],
            "on_member_update": [],
            "on_user_update": [],
            "on_member_ban": [],
            "on_member_unban": [],
            "on_presence_update": [],
            
            "on_message": [],
            "on_message_edit": [],
            "on_raw_message_edit": [],
            "on_message_delete": [],
            "on_bulk_message_delete": [],
            "on_raw_message_delete": [],
            "on_raw_bulk_message_delete": [],
            
            "on_reaction_add": [],
            "on_reaction_remove": [],
            "on_reaction_clear": [],
            "on_reaction_clear_emoji": [],
            "on_raw_reaction_add": [],
        }
        
    async def fire_event(self, event: Event) -> None:
        if event.event_name in self.events:
            for _event in self.events[event.name]:
                await event.callback(event.args)
                
                
    async def register_event(self, event: Event) -> bool:
        """Registers event to the internal event handler. Must be a valid events.Event instance.

        Args:
            event (Event): The valid events.Event instance. 

        Raises:
            InvalidEvent: Raised if the event is invalid / not in the list.

        Returns:
            bool: Returns True on completetion.
        """        
        if event.event_name not in self.events:
            raise InvalidEvent("Event is not a valid event from the list.")
        self.events[event.event_name].append(event)