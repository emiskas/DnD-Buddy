class InitiativeTracker:
    def __init__(self):
        self.initiative_list = []

    def sort_initiative(self):
        """Sort the list by initiative roll (descending)."""
        self.initiative_list.sort(key=lambda x: x["initiative"], reverse=True)

    def add_player(self, player_name, initiative_roll):
        """Add a player and their initiative roll to the list."""
        self.initiative_list.append(
            {"name": player_name, "initiative": initiative_roll}
        )

    def display_order(self):
        """Display the current initiative order."""
        if not self.initiative_list:
            return "No one has rolled initiative yet."
        
        return "\n".join(
            f"[{player['name']} - {player['initiative']}]" 
            for player in self.initiative_list
        )

    def reset(self):
        """Reset the initiative order."""
        self.initiative_list.clear()
