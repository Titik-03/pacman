import arcade

class SoundManager:

    _instance = None

    def __init__(self):
        self.sfx = {
            "coin":        arcade.load_sound("src/assets/sfx/coin.wav"),
            "power_pellet": arcade.load_sound("src/assets/sfx/power_pellet.wav"),
            "ghost_eaten": arcade.load_sound("src/assets/sfx/ghost_eaten.wav"),
            "death":       arcade.load_sound("src/assets/sfx/death.wav"),
            "menu_select": arcade.load_sound("src/assets/sfx/menu_select.wav"),
            "level_clear": arcade.load_sound("src/assets/sfx/level_clear.wav"),
            "game_over":   arcade.load_sound("src/assets/sfx/game_over.wav"),
        }

        self.music = {
            "menu":       arcade.load_sound("src/assets/music/menu_theme.wav", streaming=True),
            "gameplay":   arcade.load_sound("src/assets/music/gameplay_theme.wav", streaming=True),
            "power_up":   arcade.load_sound("src/assets/music/power_up_theme.wav", streaming=True),
        }

        self.sfx_volume = 0.8
        self.music_volume = 0.5
        self._current_music_name = None
        self._current_music_player = None

    @classmethod
    def get(cls) -> "SoundManager":
        if cls._instance is None:
            cls._instance = SoundManager()
        return cls._instance

    def play_sfx(self, name: str):
        sound = self.sfx.get(name)
        if sound:
            arcade.play_sound(sound, volume=self.sfx_volume)

    def play_music(self, name: str, loop: bool = True):
        if self._current_music_name == name:
            return
        self.stop_music()
        sound = self.music.get(name)
        if sound:
            self._current_music_player = arcade.play_sound(
                sound, volume=self.music_volume, looping=loop
            )
            self._current_music_name = name

    def stop_music(self):
        if self._current_music_player:
            arcade.stop_sound(self._current_music_player)
        self._current_music_player = None
        self._current_music_name = None
