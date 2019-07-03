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
        return pygame.display.get_surface()

    @property
    def parent(self):
        """
        The Interface object owning this interface.
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

    @property
    def current_resolution(self):
        return GuiUtilities.CURRENT_RESOLUTION

    @current_resolution.setter
    def current_resolution(self, resolution):
        GuiUtilities.CURRENT_RESOLUTION = resolution

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
        GuiUtilities.init_pygame()

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
        self.event_window_resize(GuiUtilities.CURRENT_RESOLUTION)
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
                GuiUtilities.toggle_fullscreen()
                self.event_window_resize(GuiUtilities.CURRENT_RESOLUTION)

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

    def event_window_resize(self, display_size):
        """
        Event handler for window resize event. This function will reinitialize the pygame display and
        create properly sized surfaces for the interface.
        :param display_size: (width, height)
        :return: None
        """
        if self.parent is None:
            GuiUtilities.set_display_size(display_size)
        else:
            self.parent.event_window_resize(display_size)
