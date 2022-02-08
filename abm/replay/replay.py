import sys

from abm.loader.data_loader import ExperimentLoader
from abm.contrib import colors
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
import pygame_widgets
import pygame
import numpy as np

class ExperimentReplay:
    def __init__(self, data_folder_path):
        """Initialization method to replay recorded simulations from their summary folder. If a summary is not yet
        available for the experiment it will be summarized first"""
        self.experiment = ExperimentLoader(data_folder_path, enforce_summary=False, with_plotting=False)
        # todo: this initialization will fail when we systematically change width and height in experiment
        self.WIDTH = int(float(self.experiment.env["ENV_WIDTH"]))
        self.HEIGHT = int(float(self.experiment.env["ENV_HEIGHT"]))
        self.T = int(float(self.experiment.env["T"]))
        self.window_pad = 30
        self.vis_area_end_width = 2 * self.window_pad + self.WIDTH
        self.action_area_width = 400
        self.action_area_height = 800
        self.full_width = self.WIDTH + self.action_area_width + 2 * self.window_pad
        self.full_height = self.action_area_height

        self.posx = self.experiment.agent_summary['posx']
        self.posy = self.experiment.agent_summary['posy']
        self.orientation = self.experiment.agent_summary['orientation']

        self.res_pos_x = self.experiment.res_summary['posx']
        self.res_pos_y = self.experiment.res_summary['posy']

        self.t = 0
        self.framerate = 25
        self.num_batches = self.experiment.num_batches
        self.batch_id = 0


        # Initializing pygame
        self.quit_term = False
        pygame.init()
        self.screen = pygame.display.set_mode([self.full_width, self.full_height])
        self.clock = pygame.time.Clock()

        # pygame widgets
        self.slider_height = 20
        self.action_area_pad = 30
        self.textbox_width = 100
        self.slider_width = self.action_area_width - 2 * self.action_area_pad - self.textbox_width -15
        self.slider_start_x = self.vis_area_end_width + self.action_area_pad
        self.textbox_start_x = self.slider_start_x + self.slider_width + 15

        slider_i = 1
        slider_start_y = slider_i * (self.slider_height + self.action_area_pad)
        self.framerate_slider = Slider(self.screen, self.slider_start_x, slider_start_y, self.slider_width, self.slider_height, min=5, max=60, step=1, initial=self.framerate)
        self.framerate_textbox = TextBox(self.screen, self.textbox_start_x, slider_start_y, self.textbox_width,
                                         self.slider_height, fontSize=self.slider_height-2, borderThickness=1)
        slider_i = 2
        slider_start_y = slider_i * (self.slider_height + self.action_area_pad)
        self.time_slider = Slider(self.screen, self.slider_start_x, slider_start_y, self.slider_width, self.slider_height, min=0, max=self.T-1, step=1, initial=0)
        self.time_textbox = TextBox(self.screen, self.textbox_start_x, slider_start_y, self.textbox_width,
                                         self.slider_height, fontSize=self.slider_height-2, borderThickness=1)
        slider_i = 3
        slider_start_y = slider_i * (self.slider_height + self.action_area_pad)
        self.batch_slider = Slider(self.screen, self.slider_start_x, slider_start_y, self.slider_width,
                                  self.slider_height, min=0, max=self.num_batches-1, step=1, initial=0)
        self.batch_textbox = TextBox(self.screen, self.textbox_start_x, slider_start_y, self.textbox_width,
                                    self.slider_height, fontSize=self.slider_height - 2, borderThickness=1)

    def draw_walls(self):
        """Drwaing walls on the arena according to initialization, i.e. width, height and padding"""
        pygame.draw.line(self.screen, colors.RED,
                         [self.window_pad, self.window_pad],
                         [self.window_pad, self.window_pad + self.HEIGHT])
        pygame.draw.line(self.screen, colors.BLACK,
                         [self.window_pad, self.window_pad],
                         [self.window_pad + self.WIDTH, self.window_pad])
        pygame.draw.line(self.screen, colors.BLACK,
                         [self.window_pad + self.WIDTH, self.window_pad],
                         [self.window_pad + self.WIDTH, self.window_pad + self.HEIGHT])
        pygame.draw.line(self.screen, colors.BLACK,
                         [self.window_pad, self.window_pad + self.HEIGHT],
                         [self.window_pad + self.WIDTH, self.window_pad + self.HEIGHT])

    def draw_separator(self):
        """Drawing separation line between action area and visualization"""
        pygame.draw.line(self.screen, colors.BLACK,
                         [self.vis_area_end_width, 0],
                         [self.vis_area_end_width, self.full_height])

    def draw_frame(self, events):
        """Drawing environment, agents and every other visualization in each timestep"""
        self.screen.fill(colors.BACKGROUND)
        self.draw_walls()
        self.draw_separator()
        pygame_widgets.update(events)
        self.framerate = self.framerate_slider.getValue()
        self.framerate_textbox.setText(f"framerate: {self.framerate}")
        self.framerate_textbox.draw()
        self.t = self.time_slider.getValue()
        self.time_textbox.setText(f"time: {self.t}")
        self.time_textbox.draw()
        self.batch_id = self.batch_slider.getValue()
        self.batch_textbox.setText(f"batch: {self.batch_id}")
        self.batch_textbox.draw()
        self.update_frame_data()
        pygame.display.flip()

    def update_frame_data(self):
        """updating the data that needs to be visualized"""
        posx = self.posx[self.batch_id, 0, 0, :, self.t]
        posy = self.posy[self.batch_id, 0, 0, :, self.t]
        orientation = self.orientation[self.batch_id, 0, 0, :, self.t]
        radius = self.experiment.env["RADIUS_AGENT"]

        res_posx = self.res_pos_x[self.batch_id, 0, 0, :, self.t]
        res_posy = self.res_pos_y[self.batch_id, 0, 0, :, self.t]
        res_radius = self.experiment.env["RADIUS_RESOURCE"]
        self.draw_resources(res_posx, res_posy, res_radius)
        self.draw_agents(posx, posy, orientation, radius)

    def draw_resources(self, posx, posy, radius):
        """Drawing agents in arena according to data"""
        num_resources = len(posx)
        for ri in range(num_resources):
            if posx[ri]!=-1 and posy[ri]!=-1:
                self.draw_res_patch(posx[ri], posy[ri], radius)

    def draw_res_patch(self, posx, posy, radius):
        """Drawing a single resource patch"""
        image = pygame.Surface([radius * 2, radius * 2])
        image.fill(colors.BACKGROUND)
        image.set_colorkey(colors.BACKGROUND)
        pygame.draw.circle(
            image, colors.GREY, (radius, radius), radius
        )

        self.screen.blit(image, (posx, posy))

    def draw_agents(self, posx, posy, orientation, radius):
        """Drawing agents in arena according to data"""
        num_agents = len(posx)
        for ai in range(num_agents):
            self.draw_agent(posx[ai], posy[ai], orientation[ai], radius)

    def draw_agent(self, posx, posy, orientation, radius):
        """Drawing a single agent according to position and orientation"""
        image = pygame.Surface([radius * 2, radius * 2])
        image.fill(colors.BACKGROUND)
        image.set_colorkey(colors.BACKGROUND)
        pygame.draw.circle(
            image, colors.LIGHT_BLUE, (radius, radius), radius
        )

        # Showing agent orientation with a line towards agent orientation
        pygame.draw.line(image, colors.BACKGROUND, (radius, radius),
                         ((1 + np.cos(orientation)) * radius, (1 - np.sin(orientation)) * radius), 3)
        self.screen.blit(image, (posx, posy))


    def interact_with_event(self, event):
        """Carry out functionality according to user's interaction"""
        # Exit if requested
        if event.type == pygame.QUIT:
            sys.exit()
        #
        # # Change orientation with mouse wheel
        # if event.type == pygame.MOUSEWHEEL:
        #     if event.y == -1:
        #         event.y = 0
        #     for ag in self.agents:
        #         ag.move_with_mouse(pygame.mouse.get_pos(), event.y, 1 - event.y)
        #
        # # Pause on Space
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            print("Space pressed, quitting!")
            self.quit_term = True
        #
        # # Speed up on s and down on f. reset default framerate with d
        # if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
        #     self.framerate -= 1
        #     if self.framerate < 1:
        #         self.framerate = 1
        # if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
        #     self.framerate += 1
        #     if self.framerate > 35:
        #         self.framerate = 35
        # if event.type == pygame.KEYDOWN and event.key == pygame.K_d:
        #     self.framerate = self.framerate_orig
        #
        # # Continuous mouse events (move with cursor)
        # if pygame.mouse.get_pressed()[0]:
        #     try:
        #         for ag in self.agents:
        #             ag.move_with_mouse(event.pos, 0, 0)
        #     except AttributeError:
        #         for ag in self.agents:
        #             ag.move_with_mouse(pygame.mouse.get_pos(), 0, 0)
        # else:
        #     for ag in self.agents:
        #         ag.is_moved_with_cursor = False

    def start(self):

        while not self.quit_term:
            events = pygame.event.get()
            for event in events:
                # Carry out interaction according to user activity
                self.interact_with_event(event)

            self.draw_frame(events)
            self.clock.tick(self.framerate)

        pygame.quit()
