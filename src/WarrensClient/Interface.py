"""
This module contains the base Interface class.
"""
import pygame
import sys
import time
from WarrensClient.CONFIG import INTERFACE
from WarrensClient.GuiUtilities import init_pygame


class Interface(object):

    @property
    def surface_display(self):
        """
        Main PyGame surface, the actual surface of the window that is visible to the user.
        Found via the parent surface.
        """
        if self.parent is None:
            return pygame.display.get_surface()
        else:
            return self.parent.surface_display

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

    def __init__(self, parent):
        """
        :param parent: Parent interface on top of which this will be displayed.
        """
        self._parent = parent
        self._surface_background = None
        self._run = False
        self.clock = None
        self._frame_rate = 0
        self._frame_elapsed_time = 0

        # Initialize pygame
        init_pygame()

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

            # Update the screen
            self._update_screen()
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
        if event.type == pygame.QUIT:
            sys.exit()

    def _frame_processing(self):
        """
        Main processing function, this is called once for every frame in the main run loop.
        :return: None
        """
        raise NotImplementedError("This needs to be implemented in the subclasses.")

    def _finalize(self):
        """
        Finalization of the interface. This is called at the end of the main run loop.
        :return: None
        """
        pass