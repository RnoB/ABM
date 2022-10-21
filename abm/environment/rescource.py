"""
rescource.py : including the main classes to create a rescource entity that can be exploited by agents.
"""
import pygame
import numpy as np

from abm.agent import supcalc
from abm.contrib import colors


class Rescource(pygame.sprite.Sprite):
    """
        Rescource class that includes all private parameters of the rescource patch and all methods necessary to exploit
        the rescource and change the patch size/appearance accordingly
        """

    def __init__(self, id, radius, position, env_size, color, window_pad, resc_units=None, quality=1, des_velocity=1.5,
        res_theta_abs=0.2):
        """
        Initalization method of main agent class of the simulations

        :param id: ID of rescource (int)
        :param radius: radius of the patch in pixels. This also refelcts the rescource units in the patch.
        :param position: position of the patch in env as (x, y)
        :param env_size: environment size available for agents as (width, height)
        :param color: color of the patch as (R, G, B)
        :param window_pad: padding of the environment in simulation window in pixels
        :param resc_units: rescource units hidden in the given patch. If not initialized the number of units is equal to
                            the radius of the patch
        :param quality: quality of the patch in possibly exploitable units per timestep (per agent)
        :param des_velocity: desired velocity of resource patch in pixel per timestep
        :param res_theta_abs: change in orientation will be pulled from uniform -res_theta_abs to res_theta_abs
        """
        # Initializing supercalss (Pygame Sprite)
        super().__init__()

        # Deciding how much resc. is in patch
        if resc_units is None:
            self.resc_units = radius
        else:
            self.resc_units = resc_units

        # Initializing agents with init parameters
        self.id = id
        self.radius = radius  # saved
        self.resc_left = self.resc_units  # saved
        self.position = np.array(position, dtype=np.float64)  # saved
        self.center = (self.position[0] + self.radius, self.position[1] + self.radius)
        self.color = color
        self.resc_left_color = colors.DARK_GREY
        self.unit_per_timestep = quality  # saved
        self.is_clicked = False
        self.show_stats = False
        self.des_velocity = des_velocity  # 1.5
        self.res_theta_abs = res_theta_abs  # 0.2

        # Environment related parameters
        self.WIDTH = env_size[0]  # env width
        self.HEIGHT = env_size[1]  # env height
        self.window_pad = window_pad
        self.boundaries_x = [self.window_pad, self.window_pad + self.WIDTH]
        self.boundaries_y = [self.window_pad, self.window_pad + self.HEIGHT]

        # State variables
        self.velocity = 0
        self.orientation = 0

        # Initial Visualization of rescource
        self.image = pygame.Surface([self.radius * 2, self.radius * 2])
        self.image.fill(colors.BACKGROUND)
        self.image.set_colorkey(colors.BACKGROUND)
        pygame.draw.circle(
            self.image, self.color, (radius, radius), radius
        )
        # visualizing left rescources
        small_radius = int((self.resc_left / self.resc_units) * self.radius)
        pygame.draw.circle(
            self.image, self.resc_left_color, (self.radius, self.radius), small_radius
        )
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.center[0]
        self.rect.centery = self.center[1]
        if self.is_clicked:
            font = pygame.font.Font(None, 25)
            text = font.render(f"{self.radius}", True, colors.BLACK)
            self.image.blit(text, (0, 0))

    def update_clicked_status(self, mouse):
        """Checking if the resource patch was clicked on a mouse event"""
        if self.rect.collidepoint(mouse):
            self.is_clicked = True
            self.position[0] = mouse[0] - self.radius
            self.position[1] = mouse[1] - self.radius
            self.center = (self.position[0] + self.radius, self.position[1] + self.radius)
        else:
            self.is_clicked = False
        self.draw_update()

    def prove_orientation(self):
        """Restricting orientation angle between 0 and 2 pi"""
        if self.orientation < 0:
            self.orientation = 2 * np.pi + self.orientation
        if self.orientation > np.pi * 2:
            self.orientation = self.orientation - 2 * np.pi

    def reflect_from_walls(self):
        """reflecting agent from environment boundaries according to a desired x, y coordinate. If this is over any
        boundaries of the environment, the agents position and orientation will be changed such that the agent is
         reflected from these boundaries."""

        # Boundary conditions according to center of agent (simple)
        x = self.position[0] + self.radius
        y = self.position[1] + self.radius

        # Reflection from left wall
        if x < self.boundaries_x[0]:
            self.position[0] = self.boundaries_x[0] - self.radius

            if np.pi / 2 <= self.orientation < np.pi:
                self.orientation -= np.pi / 2
            elif np.pi <= self.orientation <= 3 * np.pi / 2:
                self.orientation += np.pi / 2
            self.prove_orientation()  # bounding orientation into 0 and 2pi

        # Reflection from right wall
        if x > self.boundaries_x[1]:

            self.position[0] = self.boundaries_x[1] - self.radius - 1

            if 3 * np.pi / 2 <= self.orientation < 2 * np.pi:
                self.orientation -= np.pi / 2
            elif 0 <= self.orientation <= np.pi / 2:
                self.orientation += np.pi / 2
            self.prove_orientation()  # bounding orientation into 0 and 2pi

        # Reflection from upper wall
        if y < self.boundaries_y[0]:
            self.position[1] = self.boundaries_y[0] - self.radius

            if np.pi / 2 <= self.orientation <= np.pi:
                self.orientation += np.pi / 2
            elif 0 <= self.orientation < np.pi / 2:
                self.orientation -= np.pi / 2
            self.prove_orientation()  # bounding orientation into 0 and 2pi

        # Reflection from lower wall
        if y > self.boundaries_y[1]:
            self.position[1] = self.boundaries_y[1] - self.radius - 1
            if 3 * np.pi / 2 <= self.orientation <= 2 * np.pi:
                self.orientation += np.pi / 2
            elif np.pi <= self.orientation < 3 * np.pi / 2:
                self.orientation -= np.pi / 2
            self.prove_orientation()  # bounding orientation into 0 and 2pi

        self.center = (self.position[0] + self.radius, self.position[1] + self.radius)

    def update(self):

        # applying random movement on resource patch
        _, theta = supcalc.random_walk(exp_theta_min=-self.res_theta_abs, exp_theta_max=self.res_theta_abs)
        self.orientation += theta
        self.prove_orientation()  # bounding orientation into 0 and 2pi
        self.velocity += (self.des_velocity - self.velocity)

        # updating agent's position
        self.position[0] += self.velocity * np.cos(self.orientation)
        self.position[1] -= self.velocity * np.sin(self.orientation)
        self.center = (self.position[0] + self.radius, self.position[1] + self.radius)

        self.reflect_from_walls()
        self.draw_update()

    def draw_update(self):
        # Initial Visualization of rescource
        self.image = pygame.Surface([self.radius * 2, self.radius * 2])
        self.image.fill(colors.BACKGROUND)
        self.image.set_colorkey(colors.BACKGROUND)
        pygame.draw.circle(
            self.image, self.color, (self.radius, self.radius), self.radius
        )
        small_radius = int((self.resc_left / self.resc_units) * self.radius)
        pygame.draw.circle(
            self.image, self.resc_left_color, (self.radius, self.radius), small_radius
        )
        self.rect = self.image.get_rect()
        self.rect.centerx = self.center[0]
        self.rect.centery = self.center[1]
        self.mask = pygame.mask.from_surface(self.image)
        if self.is_clicked or self.show_stats:
            font = pygame.font.Font(None, 18)
            text = font.render(f"{self.resc_left:.2f}, Q{self.unit_per_timestep:.2f}", True, colors.BLACK)
            self.image.blit(text, (0, 0))
            text_rect = text.get_rect(center=self.rect.center)

    def deplete(self, rescource_units):
        """depeting the given patch with given rescource units"""
        # Not allowing faster depletion than what the patch can provide (per agent)
        if rescource_units > self.unit_per_timestep:
            rescource_units = self.unit_per_timestep

        if self.resc_left >= rescource_units:
            self.resc_left -= rescource_units
            depleted_units = rescource_units
        else:  # can not deplete more than what is left
            depleted_units = self.resc_left
            self.resc_left = 0
        if self.resc_left > 0:
            return depleted_units, False
        else:
            return depleted_units, True
