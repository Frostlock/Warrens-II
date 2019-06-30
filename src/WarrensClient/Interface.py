"""
This module contains the base Interface class.
"""
import pygame
from pygame.locals import *
import sys
import time
from WarrensClient.CONFIG import INTERFACE, COLORS
from WarrensClient import GuiUtilities


class Interface(object):

    @property
    def surface_display(self):
        """
        Main PyGame surface, the actual surface of the window that is visible to the user.
        Found via the parent surface.
        """
        # if self.parent is None:
        return pygame.display.get_surface()
        # else:
        #     return self.parent.surface_display

    @property
    def parent(self):
        """
        The Interace object owning this interface.
        :return: Interface
        """
        return self._parent

    @property
    def surface_background(self):
        """
        Background surface for this interface.
        :return: Surface
        """
        return self._surface_background

    def get_fullscreen(self):
        """
        Boolean indicating whether or not we are in fullscreen mode.
        :return: Boolean
        """
        return self.__class__._fullscreen

    def set_fullscreen(self, boolean):
        """
        Setter for fullscreen property.
        :param boolean: value indicating if application should run in fullscreen.
        :return: None
        """
        if boolean != self.__class__._fullscreen:
            self.__class__._fullscreen = boolean
            if self.__class__._fullscreen:
                self.__class__.event_window_resize(self, self.__class__.fullscreen_resolution)
            else:
                self.__class__.event_window_resize(self, self.__class__.window_resolution)

    @property
    def frame_rate(self):
        """
        Current frame rate of the main loop
        :return:
        """
        return self._frame_rate

    @property
    def frame_elapsed_time(self):
        """
        Time in milliseconds since the last frame
        :return:
        """
        return self._frame_elapsed_time

    def __init__(self, parent):
        """
        Constructor
        After construction the interface the run() method should be called.
        :param parent: Parent interface on top of which this will be displayed.
        """
        self._parent = parent
        self._surface_background = None
        self._run = False
        self.clock = None
        self._frame_rate = 0
        self._frame_elapsed_time = 0

        # Initialize pygame
        # TODO: Move this from GuiUtilities into Interface class?
        GuiUtilities.init_pygame()

        self.class_initialization()

    @classmethod
    def class_initialization(cls):
        # Initialize display surface
        display_info = pygame.display.Info()
        ratio = display_info.current_w / display_info.current_h
        # SDL will detect dual monitors as one big screen area.
        # Regular screen resolutions are either ratio 4:3 or ratio 16:9 so we attempt to predict
        # the number of screens based on the ratio between width and height.
        if 2.5 < ratio < 3.8:
            # Suspect 2 displays side by side
            cls.fullscreen_resolution = (int(display_info.current_w // 2), display_info.current_h)
        elif 3.8 <= ratio:
            # Suspect 3 displays side by side
            cls.fullscreen_resolution = (int(display_info.current_w // 3), display_info.current_h)
        elif ratio < 1:
            # Suspect 2 displays on top of each other
            cls.fullscreen_resolution = (display_info.current_w, int(display_info.current_h // 2))
        else:
            # Suspect single display
            cls.fullscreen_resolution = (display_info.current_w, display_info.current_h)

        cls.window_resolution = INTERFACE.WINDOW_SIZE
        cls._fullscreen = False
        cls.current_resolution = (0, 0)

    def event_window_resize(self, display_size):
        """
        Initialize the pygame display and creates properly sized surfaces for the interface
        :param display_size: (width, height)
        :return: None
        """
        # Pygame display initialization
        if self.get_fullscreen():
            self.__class__.current_resolution = self.__class__.fullscreen_resolution
            pygame.display.set_mode(self.__class__.fullscreen_resolution, NOFRAME)
        else:
            self.__class__.current_resolution = display_size
            pygame.display.set_mode(display_size, RESIZABLE)

    def run(self):
        """
        Hands over control to this interface. This interface will initialize and loop until it is finished.
        :return: None
        """
        self._initialize()
        start_time, render_time, event_time, game_time = 0, 0, 0, 0
        self._run = True
        while self._run:
            if INTERFACE.SHOW_PERFORMANCE_LOGGING:
                start_time = time.time()

            # Update the screen surface
            self._update_screen()
            # Show frame rate in top right hand corner
            blit_text = GuiUtilities.FONT_SMALL.render(str(self.frame_rate) + " fps", 1, COLORS.PANEL_FONT)
            self.surface_display.blit(blit_text, (self.current_resolution[0] - blit_text.get_width(), 2))
            # Refresh display
            pygame.display.flip()
            if INTERFACE.SHOW_PERFORMANCE_LOGGING:
                render_time = time.time() - start_time

            # Handle events
            events = pygame.event.get()
            for event in events:
                self._handle_event(event)
            if INTERFACE.SHOW_PERFORMANCE_LOGGING:
                event_time = time.time() - start_time - render_time

            # Frame processing
            self._frame_processing()
            if INTERFACE.SHOW_PERFORMANCE_LOGGING:
                game_time = time.time() - start_time - render_time - event_time

            # limit frame rate (kinda optimistic since with current rendering we don't achieve this frame rate :) )
            frame_rate_limit = 30
            self._frame_elapsed_time = self.clock.tick(frame_rate_limit)
            self._frame_rate = self.clock.get_fps()
            if INTERFACE.SHOW_PERFORMANCE_LOGGING:
                print("LOOP! FPS: " + str(self._frame_rate) +
                      " Rendering: " + str(render_time) + "s " +
                      str(len(events)) + " events: " + str(event_time) + "s" +
                      " Game: " + str(game_time) + "s ")

        self._finalize()

    def _initialize(self):
        """
        Initialization of the interface. This is called after construction at the start of the main run loop.
        It is used to prepare reusable interface assets like for example the background image.
        :return: None
        """
        self.event_window_resize(self.window_resolution)
        self.clock = pygame.time.Clock()

    def _update_screen(self):
        """
        Main render function, this is called once for every frame in the main run loop.
        :return: None
        """
        raise NotImplementedError("This needs to be implemented in the subclasses.")

    def _handle_event(self, event):
        """
        Main event handler, this is called once for every pending event during the main run loop.
        :param event: Pygame event
        :return: None
        """
        # Pygame quit event
        if event.type == pygame.QUIT:
            sys.exit()
        # Window resize event
        elif event.type == VIDEORESIZE:
            self.event_window_resize(event.dict['size'])
        # keyboard events
        elif event.type == pygame.KEYDOWN:
            # Toggle fullscreen mode
            if event.unicode == 'f':
                self.set_fullscreen(not self.get_fullscreen())

    def _frame_processing(self):
        """
        Main processing function, this is called once for every frame in the main run loop.
        :return: None
        """
        pass

    def _finalize(self):
        """
        Finalization of the interface. This is called at the end of the main run loop.
        :return: None
        """
        pass

    def event_quit(self):
        # Interrupt game loop
        self._run = False
