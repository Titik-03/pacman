from typing import Any
import arcade


class SoundManager:
    """Singleton audio manager for sound effects and background music."""

    _instance: "SoundManager | None" = None

    def __init__(self) -> None:
        """Initialize sound effects, music tracks, and volume levels."""
        self.sfx = {
            "coin":        arcade.load_sound("src/assets/coin.wav"),
            "power_pellet": arcade.load_sound("src/assets/powerup.wav"),
            "ghost_eaten": arcade.load_sound("src/assets/ghost_eaten.wav"),
            "death":       arcade.load_sound("src/assets/death.wav"),
            "menu_select": arcade.load_sound("src/assets/menu_select.wav"),
            "level_clear": arcade.load_sound("src/assets/level_clear.wav"),
            "game_over":   arcade.load_sound("src/assets/game_over.wav"),
            "menu_hover":  arcade.load_sound("src/assets/hover.wav")
        }

        self.music = {
            "menu": arcade.load_sound(
                "src/assets/menu_ost.wav", streaming=True
            ),
            "gameplay": arcade.load_sound(
                "src/assets/main_ost.wav", streaming=True
            ),
            "power_up": arcade.load_sound(
                "src/assets/powerup.wav", streaming=True
            ),
        }

        self.sfx_volume = 0.8
        self.music_volume = 0.5
        self._current_music_name: str | None = None
        self._current_music_player: Any = None

    @classmethod
    def get(cls) -> "SoundManager":
        """Return the singleton instance of SoundManager."""
        if cls._instance is None:
            cls._instance = SoundManager()
        return cls._instance

    def play_sfx(self, name: str) -> None:
        """Play a sound effect by name."""
        sound = self.sfx.get(name)
        if sound:
            arcade.play_sound(sound, volume=self.sfx_volume)

    def play_music(self, name: str, loop: bool = True) -> None:
        """Play a background music track by name, optionally looping."""
        if self._current_music_name == name:
            return
        self.stop_music()
        sound = self.music.get(name)
        if sound:
            self._current_music_player = arcade.play_sound(
                sound, volume=self.music_volume, loop=loop
            )
            self._current_music_name = name

    def stop_music(self) -> None:
        """Stop the currently playing background music."""
        if self._current_music_player:
            arcade.stop_sound(self._current_music_player)
        self._current_music_player = None
        self._current_music_name = None
