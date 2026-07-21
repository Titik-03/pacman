import arcade
import arcade.gui
from views import Game, HighScore, Instuctions

#main menu view.
class MainMenu(arcade.View):

    def __init__(self):

        super().__init__()

        #setting background color.
        arcade.set_background_color(arcade.color.BLACK)

        # Create the manager brain.
        self.manager = arcade.gui.UIManager()

        self.x_center = self.width / 2
        self.y_center = self.height / 2

        #init the game view
        self.game_view = Game()
        self.high_score_view = HighScore()
        self.instuctions_view = Instuctions()

        


    #update when ever resizing the screen. 
    def on_resize(self, width: int, height: int):
        # Call the parent resize handler to update the internal viewport matrix
        super().on_resize(width, height)

    #what will happen if the view is showed.
    def on_show_view(self):  
        #enabling the gui manager (if not it will just draw the buttons without intuctions).
        self.manager.enable()

        arcade.load_font("src/assets/fonts/MickeyMouse_PERSONAL_USE_ONLY.otf")

        #init the gui box to make all the buttons in one group layout.
        menu_elements = arcade.gui.UIBoxLayout(space_between=40)

        #button style.
        button_style = {
            "normal": arcade.gui.UIFlatButton.UIStyle(
                font_size=30,
                font_name="Mickey Mouse PERSONAL USE",
                font_color=(234, 236, 250),
                bg=(20, 12, 48),
                border=(90, 72, 160),
                border_width=2,
            ),
            "hover": arcade.gui.UIFlatButton.UIStyle(
                font_size=30,
                font_name="Mickey Mouse PERSONAL USE",
                font_color=(250, 250, 255),
                bg=(64, 32, 120),
                border=(180, 170, 255),
                border_width=2,
            ),
            "press": arcade.gui.UIFlatButton.UIStyle(
                font_size=30,
                font_name="Mickey Mouse PERSONAL USE",
                font_color=(252, 244, 255),
                bg=(8, 6, 26),
                border=(110, 78, 190),
                border_width=3,
            ),
            "disabled": arcade.gui.UIFlatButton.UIStyle(
                font_size=30,
                font_name="Mickey Mouse PERSONAL USE",
                font_color=(120, 118, 136),
                bg=(18, 18, 36),
                border=(56, 64, 96),
                border_width=1,
            )
        }

        #init the buttons.
        start_game = arcade.gui.UIFlatButton(text=" S T A R T G A M E", width=400, height=100, style=button_style)
        high_score = arcade.gui.UIFlatButton(text=" H I G H S C O R E", width=400, height=100, style=button_style)
        instructions = arcade.gui.UIFlatButton(text=" I N S T R U C T I O N S ", width=400, height=100, style=button_style)
        quit_game = arcade.gui.UIFlatButton(text=" Q U I T G A M E", width=400, height=100, style=button_style)

        #nested function to do things if the buttons was clicked.
        @start_game.event("on_click")
        def on_click_start(event):
            #This is the action! Swap from current menu view to game view.
            self.window.show_view(self.game_view)
        
        @high_score.event("on_click")
        def on_click_high_score(event):
            #This is the action! Swap from current menu view to game view.
            self.window.show_view(self.high_score_view)
        
        @instructions.event("on_click")
        def on_click_instuctions(event):
            #This is the action! Swap from current menu view to game view.
            self.window.show_view(self.instuctions_view)
        
        @quit_game.event("on_click")
        def on_click_quit(event):
            arcade.exit()

        #adding buttons to one group layout.
        menu_elements.add(start_game)
        menu_elements.add(high_score)
        menu_elements.add(instructions)
        menu_elements.add(quit_game)


        #give the group to the manager.
        self.manager.add(
            arcade.gui.UIAnchorLayout(
                anchor_x="center_x",
                anchor_y="center_y",
                children=[menu_elements]
            )
        )

    #when the view is hided.
    def on_hide_view(self):
        self.manager.disable()

    # what will draw.
    def on_draw(self):

        self.clear()

        # self.title_text.draw()

        
        arcade.draw_text(
            text="p  a  c  -  m  a  n",
            x = self.width / 2,
            y = self.height - 200,
            color=arcade.color.WHITE,
            font_size=180,
            font_name="Mickey Mouse PERSONAL USE",
            # bold=True,
            anchor_x="center"
        )

        self.manager.draw()

        # arcade.draw_text("Pac-Man",
        #          self.width / 2 + 4,
        #          self.height - 84,
        #          (6, 8, 30),
        #          font_size=180,
        #          anchor_x="center",
        #          anchor_y="center")

        
        # arcade.draw_text("Pac-Man",
        #                  self.width / 2,
        #                  self.height - 360,
        #                  arcade.color.RED,
        #                  font_size=100,
        #                  anchor_x="center",
        #                  anchor_y="center")

    
    # def on_mouse_press(self, x, y, button, modifiers):
    #     self.window.show_view(Game())
    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            arcade.exit()

window = arcade.Window(1920, 1080, "Pac-man", resizable=True)

main_menu = MainMenu()

window.show_view(main_menu)

arcade.run()

