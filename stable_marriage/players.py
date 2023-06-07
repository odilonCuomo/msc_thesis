"""Player class for use in the GS algorithm. Mainly inspired from the Matching library (https://github.com/daffidwilde/matching) """

class Player():
    """A class to represent a player within the matching game.

    Parameters
    ----------
    id : int
        An identifier. This should be unique.

    Attributes
    ----------
    prefs : list of int
        The player's preferences, i.e. a ranking of the other group's ids. Defaults to ``None`` and is updated using the
        ``set_prefs`` method.
    pref_names : list
        A list of the names in ``prefs``. Updates with ``prefs`` via
        ``set_prefs`` method.
    matching : Player or None
        The current match of the player. ``None`` if not currently matched.
    considering : int or None
        The index of the next player to propose to in the preference list. ``None`` if all have been seen.
    """

    def __init__(self, id):

        self.id = id
        self.prefs = []
        self.matching = None
        self.considering = 1

    def set_prefs(self, players_id):
        """Set the player's preferences to be a list of players."""

        self.prefs = players_id


    def _match(self, other):
        """Assign the player to be matched to some other player."""

        self.matching = other

    def _unmatch(self):
        """Set the player to be unmatched."""

        self.matching = None

    def get_favourite(self):
        """Get the player's favourite player."""

        return self.prefs[0]
    
    def get_next_favourite(self):
        """Get the player to propose to"""
        next_p = self.prefs[self.considering]
        self.considering += 1
        if self.considering == len(self.prefers):
            self.considering = None
        return next_p
    
    def prefers(self, player_id, other_id):
        """Determines whether the player prefers a player over some other
        player."""

        prefs = self.prefs
        return prefs.index(player_id) < prefs.index(other_id)