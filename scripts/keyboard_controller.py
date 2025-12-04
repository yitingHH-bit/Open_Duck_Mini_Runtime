#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygame
from collections import namedtuple

ButtonState = namedtuple("ButtonState", ["triggered", "is_pressed"])


class Buttons:
    def __init__(self):
        self.A = ButtonState(False, False)
        self.B = ButtonState(False, False)
        self.X = ButtonState(False, False)
        self.Y = ButtonState(False, False)
        self.LB = ButtonState(False, False)
        self.dpad_up = ButtonState(False, False)
        self.dpad_down = ButtonState(False, False)


class KeyboardController:
    """
    Use keyboard as a simple replacement for a game controller.

    Commands layout (you can tweak later):

      Movement:
        W / S : forward / backward  (vx)
        A / D : left / right        (vy)
        Q / E : rotate left / right (yaw)

      Head:
        Arrow UP / DOWN : pitch
        Arrow LEFT / RIGHT : yaw

      Buttons:
        SPACE  : A
        LSHIFT : B
        X      : X
        Y      : Y
        LCTRL  : LB

      Triggers:
        Z : left trigger  (0 or 1)
        X : right trigger (0 or 1)
    """

    def __init__(self, freq: int = 20):
        pygame.init()
        # We need a window so pygame can receive keyboard events.
        self.screen = pygame.display.set_mode((300, 200))
        pygame.display.set_caption("Duck Keyboard Controller")
        self.clock = pygame.time.Clock()
        self.freq = freq

        self.prev_keys = pygame.key.get_pressed()

        # RLWalk expects a list of 7 floats.
        self.last_commands = [0.0] * 7

    def _make_button(self, now_pressed: bool, prev_pressed: bool) -> ButtonState:
        triggered = (not prev_pressed) and now_pressed
        return ButtonState(triggered=triggered, is_pressed=now_pressed)

    def get_last_command(self):
        # Handle quit events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

        keys = pygame.key.get_pressed()

        # Base command values
        vx = 0.0  # forward / backward
        vy = 0.0  # left / right
        yaw = 0.0  # rotation

        # Movement: WASD + Q/E
        if keys[pygame.K_w]:
            vx += 1.0
        if keys[pygame.K_s]:
            vx -= 1.0
        if keys[pygame.K_a]:
            vy += 1.0
        if keys[pygame.K_d]:
            vy -= 1.0

        if keys[pygame.K_q]:
            yaw += 1.0
        if keys[pygame.K_e]:
            yaw -= 1.0

        # Head control with arrow keys
        head_pitch = 0.0
        head_yaw = 0.0
        if keys[pygame.K_UP]:
            head_pitch += 0.5
        if keys[pygame.K_DOWN]:
            head_pitch -= 0.5
        if keys[pygame.K_LEFT]:
            head_yaw += 0.5
        if keys[pygame.K_RIGHT]:
            head_yaw -= 0.5

        extra1 = 0.0
        extra2 = 0.0

        self.last_commands = [
            vx,
            vy,
            yaw,
            head_pitch,
            head_yaw,
            extra1,
            extra2,
        ]

        # Button states
        buttons = Buttons()
        buttons.A = self._make_button(
            keys[pygame.K_SPACE], self.prev_keys[pygame.K_SPACE]
        )
        buttons.B = self._make_button(
            keys[pygame.K_LSHIFT], self.prev_keys[pygame.K_LSHIFT]
        )
        buttons.X = self._make_button(keys[pygame.K_x], self.prev_keys[pygame.K_x])
        buttons.Y = self._make_button(keys[pygame.K_y], self.prev_keys[pygame.K_y])
        buttons.LB = self._make_button(
            keys[pygame.K_LCTRL], self.prev_keys[pygame.K_LCTRL]
        )

        buttons.dpad_up = self._make_button(keys[pygame.K_r], self.prev_keys[pygame.K_r])
        buttons.dpad_down = self._make_button(
            keys[pygame.K_f], self.prev_keys[pygame.K_f]
        )

        # Triggers
        left_trigger = 1.0 if keys[pygame.K_z] else 0.0
        right_trigger = 1.0 if keys[pygame.K_x] else 0.0

        self.prev_keys = keys

        # Keep a fixed update rate
        self.clock.tick(self.freq)

        return self.last_commands, buttons, left_trigger, right_trigger


if __name__ == "__main__":
    # Simple test: print commands and button states
    kc = KeyboardController(freq=20)
    while True:
        cmds, buttons, lt, rt = kc.get_last_command()
        print(
            "cmds:", [round(c, 2) for c in cmds],
            "| A:", buttons.A,
            "B:", buttons.B,
            "lt:", lt, "rt:", rt
        )
