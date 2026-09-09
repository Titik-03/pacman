from typing import Dict, List
import os
import json
import arcade
import arcade.gui


class HighScore(arcade.View):

    # init with deafults.
    def __init__(self, main_menu: arcade.View, window: arcade.Window):
        super().__init__()

        self.x_center = self.width / 2
        self.y_center = self.height / 2

        self.high_score_text = arcade.Text(
            text="High_score.",
            x=self.width / 2,
            y=self.height - 200,
            color=arcade.color.WHITE,
            font_size=150,
            anchor_x="center"
        )

        self.main_menu = main_menu
        self.window = window

        self.score: List = []

        self.high_score_text = arcade.Text(
            "HIGH SCORES",
            self.window.width / 2,
            self.window.height - 140,
            arcade.color.WHITE,
            72,
            font_name="Handjet",
            bold=True,
            anchor_x="center"
        )

    # what will happen if the view is showed.

    def on_show_view(self) -> None:

        h = Score()
        self.score = h.load_score()

    def draw_background(self) -> None:

        arcade.set_background_color((8, 12, 28, 255))

        color = (0, 180, 255, 30)

        arcade.draw_line(300, 800, 700, 800, color, 6)
        arcade.draw_line(700, 550, 700, 800, color, 6)

        arcade.draw_line(1100, 600, 1500, 600, color, 6)
        arcade.draw_line(1100, 300, 1100, 600, color, 6)

    def draw_score_panel(self) -> None:

        x = self.window.width / 2 - 350
        y = self.window.height - 220

        width = 700
        height = 580

        arcade.draw_lrbt_rectangle_filled(
            x,
            x + width,
            y - height,
            y,
            (0, 0, 0, 100)
        )

        arcade.draw_lrbt_rectangle_outline(
            x,
            x + width,
            y - height,
            y,
            (0, 240, 255),
            border_width=2
        )

        arcade.draw_text(
            "#",
            x + 40,
            y - 50,
            arcade.color.YELLOW,
            24,
            bold=True,
        )

        arcade.draw_text(
            "PLAYER",
            x + 100,
            y - 50,
            arcade.color.YELLOW,
            24,
            bold=True,
        )

        arcade.draw_text(
            "SCORE",
            x + width - 40,
            y - 50,
            arcade.color.YELLOW,
            24,
            bold=True,
            anchor_x="right",
        )

        arcade.draw_line(
            x + 25,
            y - 85,
            x + width - 25,
            y - 85,
            arcade.color.CYAN,
            2
        )

        row_y = y - 140

        for i, item in enumerate(self.score[:10]):

            name = item.get("name", "???")
            score = item.get("score", 0)

            if i == 0:
                color: tuple[int, ...] = arcade.color.GOLD
            elif i == 1:
                color = (220, 220, 220)
            elif i == 2:
                color = (205, 127, 50)
            else:
                color = arcade.color.WHITE

            arcade.draw_text(
                str(i + 1),
                x + 40,
                row_y,
                color,
                24,
                bold=True,
            )

            arcade.draw_text(
                name,
                x + 100,
                row_y,
                arcade.color.WHITE,
                24,
            )

            arcade.draw_text(
                str(score),
                x + width - 40,
                row_y,
                arcade.color.CYAN,
                24,
                anchor_x="right",
            )

            row_y -= 45

    # what will draw.

    def on_draw(self) -> None:

        # clear the screen before drawing new things to prevent overdrawing
        # on last view.
        self.clear()

        self.draw_background()
        self.high_score_text.draw()
        self.draw_score_panel()

    def on_key_press(self, key: int, modifiers: int) -> None:
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.main_menu)


class Score:

    def __init__(self, filepath: str = "src/outputs/high_score.json") -> None:
        self.filepath = filepath
        self.scores: List[Dict] = []
        self.load_score()

    def load_score(self) -> List[Dict]:
        """Loads scores from the JSON file.

        Creates file if missing or corrupted.
        """
        if not os.path.exists(self.filepath):
            self.scores = []
            self._save_to_disk()
            return self.scores

        try:
            with open(self.filepath, "r") as fp:
                data = json.load(fp)

            # Filter out stray non-dict elements like empty lists [[]]
            if isinstance(data, list):
                self.scores = [
                    self._normalize_entry(item)
                    for item in data
                    if isinstance(item, dict)
                ]
            else:
                self.scores = []

        except (json.JSONDecodeError, Exception) as e:
            print(f"Error loading scores: {e}")
            self.scores = []

        return self.scores

    @staticmethod
    def _normalize_entry(item: Dict) -> Dict:
        """Converts legacy {'PlayerName': 220} entries to
        {'name': 'PlayerName', 'score': 220}.
        """
        if "name" in item and "score" in item:
            return item
        if len(item) == 1:
            legacy_name, legacy_score = next(iter(item.items()))
            return {"name": str(legacy_name), "score": legacy_score}
        return {"name": item.get("name", "???"), "score": item.get("score", 0)}

    def write_score(self, name: str, score: int) -> List[Dict]:
        """Adds a new score, sorts descending, clamps to top 10,
        and saves to file.
        """
        import re
        clean_name = re.sub(r"[^A-Za-z0-9 ]", "", name).strip()[:10]
        if not clean_name:
            clean_name = "PLAYER"
        clean_score = max(0, int(score))

        new_entry = {"name": clean_name, "score": clean_score}

        # Reload fresh data first to prevent overwriting parallel changes
        self.load_score()
        self.scores.append(new_entry)

        # Sort highest scores to the top and keep top 10
        self.scores.sort(key=lambda x: x.get("score", 0), reverse=True)
        self.scores = self.scores[:10]

        self._save_to_disk()
        return self.scores

    def _save_to_disk(self) -> None:
        """Helper method to handle JSON write operations."""
        # Ensure output directory exists before writing
        dirname = os.path.dirname(self.filepath)
        if dirname:
            os.makedirs(dirname, exist_ok=True)

        try:
            with open(self.filepath, "w") as fp:
                json.dump(self.scores, fp, indent=4)
        except Exception as e:
            print(f"Error saving scores: {e}")
