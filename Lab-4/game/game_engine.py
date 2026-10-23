
import random
import math
from array import array

import pygame

from game.color_button import ColorButton


class GameEngine:
    # Different sound frequencies for the four colors.
    SOUND_FREQUENCIES = [330, 440, 550, 660]

    def __init__(self, width, height):
        self.width = width
        self.height = height

        pad_size = 130
        gap = 24
        start_x = width // 2 - pad_size - (gap // 2)
        start_y = 150

        self.buttons = [
            ColorButton(
                0,
                pygame.Rect(start_x, start_y, pad_size, pad_size),
                (110, 20, 20), (255, 50, 50)
            ),
            ColorButton(
                1,
                pygame.Rect(
                    start_x + pad_size + gap,
                    start_y, pad_size, pad_size
                ),
                (15, 60, 150), (40, 170, 255)
            ),
            ColorButton(
                2,
                pygame.Rect(
                    start_x, start_y + pad_size + gap,
                    pad_size, pad_size
                ),
                (15, 100, 30), (50, 255, 90)
            ),
            ColorButton(
                3,
                pygame.Rect(
                    start_x + pad_size + gap,
                    start_y + pad_size + gap,
                    pad_size, pad_size
                ),
                (140, 110, 10), (255, 235, 40)
            ),
        ]

        self.sequence = []
        self.player_input = []
        self.score = 0

        self.state = "WATCH"
        self.showing_step = 0
        self.step_start_time = 0

        # Playback timing gets faster as the sequence grows.
        self.flash_duration = 450
        self.pause_duration = 200
        self.is_flashing = False

        # Player button flash.
        self.player_lit_button = None
        self.player_lit_start = 0
        self.player_flash_duration = 150

        # Player-turn countdown.
        self.turn_time_limit = 10000  # 10 seconds
        self.turn_start_time = 0

        # Sound setup. The game can still run if audio is unavailable.
        self.sounds = self.create_sounds()

        self.font_title = pygame.font.SysFont(None, 40)
        self.font_medium = pygame.font.SysFont(None, 28)
        self.font_small = pygame.font.SysFont(None, 22)

        self.start_next_round()

    def create_sounds(self):
        sounds = []

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(
                    frequency=44100,
                    size=-16,
                    channels=1,
                    buffer=512
                )

            sample_rate = 44100
            duration = 0.18
            volume = 0.35

            for frequency in self.SOUND_FREQUENCIES:
                samples = array("h")
                total_samples = int(sample_rate * duration)

                for i in range(total_samples):
                    fade = min(1.0, i / 300)
                    fade *= min(1.0, (total_samples - i) / 1000)

                    sample = int(
                        32767
                        * volume
                        * fade
                        * math.sin(
                            2 * math.pi * frequency * i / sample_rate
                        )
                    )
                    samples.append(sample)

                sounds.append(
                    pygame.mixer.Sound(buffer=samples.tobytes())
                )

        except (pygame.error, OSError):
            # Continue without sound if the system has no usable audio.
            return []

        return sounds

    def play_color_sound(self, color_id):
        if self.sounds and 0 <= color_id < len(self.sounds):
            try:
                self.sounds[color_id].play()
            except pygame.error:
                pass

    def start_next_round(self):
        # FIX: append exactly one color instead of duplicating the sequence.
        new_color = random.randint(0, 3)
        self.sequence.append(new_color)

        # Increase speed as the sequence gets longer.
        self.flash_duration = max(160, 450 - (len(self.sequence) - 1) * 20)
        self.pause_duration = max(70, 200 - (len(self.sequence) - 1) * 8)

        self.player_input.clear()
        self.state = "WATCH"
        self.showing_step = 0
        self.step_start_time = pygame.time.get_ticks()
        self.is_flashing = True

        for button in self.buttons:
            button.is_lit = False

        first_button = self.buttons[self.sequence[0]]
        first_button.is_lit = True
        self.play_color_sound(self.sequence[0])

        self.player_lit_button = None

    def update(self):
        now = pygame.time.get_ticks()

        # Turn off a button briefly lit by player input.
        if self.player_lit_button is not None:
            if now - self.player_lit_start >= self.player_flash_duration:
                self.player_lit_button.is_lit = False
                self.player_lit_button = None

        if self.state == "WATCH":
            current_btn_id = self.sequence[self.showing_step]

            if self.is_flashing:
                if now - self.step_start_time >= self.flash_duration:
                    self.buttons[current_btn_id].is_lit = False
                    self.is_flashing = False
                    self.step_start_time = now
            else:
                if now - self.step_start_time >= self.pause_duration:
                    self.showing_step += 1

                    if self.showing_step < len(self.sequence):
                        next_id = self.sequence[self.showing_step]
                        self.buttons[next_id].is_lit = True
                        self.play_color_sound(next_id)

                        self.is_flashing = True
                        self.step_start_time = now
                    else:
                        self.state = "PLAYER_TURN"
                        self.turn_start_time = now

        elif self.state == "PLAYER_TURN":
            # If the player runs out of time, end the game.
            if now - self.turn_start_time >= self.turn_time_limit:
                self.state = "GAME_OVER"

    def handle_event(self, event):
        if self.state == "GAME_OVER":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()
            return

        if (
            self.state == "PLAYER_TURN"
            and event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
        ):
            for btn in self.buttons:
                if btn.contains(event.pos):
                    btn.is_lit = True
                    self.player_lit_button = btn
                    self.player_lit_start = pygame.time.get_ticks()

                    self.play_color_sound(btn.color_id)
                    self.register_player_click(btn.color_id)
                    break

    def register_player_click(self, color_id):
        if self.state != "PLAYER_TURN":
            return

        current_idx = len(self.player_input)
        self.player_input.append(color_id)

        if self.player_input[current_idx] != self.sequence[current_idx]:
            self.state = "GAME_OVER"
            return

        if len(self.player_input) == len(self.sequence):
            self.score += 1
            self.start_next_round()

    def reset(self):
        self.sequence.clear()
        self.player_input.clear()
        self.score = 0

        for btn in self.buttons:
            btn.is_lit = False

        self.player_lit_button = None
        self.start_next_round()

    def render(self, screen):
        screen.fill((22, 24, 30))

        title_surf = self.font_title.render(
            "Memory Pattern Arena", True, (245, 245, 245)
        )
        screen.blit(
            title_surf,
            (self.width // 2 - title_surf.get_width() // 2, 20)
        )

        score_surf = self.font_medium.render(
            f"Score: {self.score}", True, (255, 220, 80)
        )
        screen.blit(
            score_surf,
            (self.width // 2 - score_surf.get_width() // 2, 60)
        )

        if self.state == "WATCH":
            status_text = "Watch the pattern..."
            status_color = (190, 195, 205)
        elif self.state == "PLAYER_TURN":
            status_text = "Your turn: Click the pattern!"
            status_color = (80, 240, 130)
        else:
            status_text = "Game over!"
            status_color = (240, 70, 70)

        status_surf = self.font_medium.render(
            status_text, True, status_color
        )
        screen.blit(
            status_surf,
            (self.width // 2 - status_surf.get_width() // 2, 95)
        )

        for btn in self.buttons:
            btn.render(screen)

        # Display the countdown bar during the player's turn.
        if self.state == "PLAYER_TURN":
            elapsed = pygame.time.get_ticks() - self.turn_start_time
            remaining = max(0, self.turn_time_limit - elapsed)
            fraction = remaining / self.turn_time_limit

            bar_width = 300
            bar_height = 16
            bar_x = self.width // 2 - bar_width // 2
            bar_y = 445

            pygame.draw.rect(
                screen, (65, 65, 75),
                (bar_x, bar_y, bar_width, bar_height),
                border_radius=7
            )

            fill_color = (
                (70, 220, 120) if fraction > 0.3
                else (245, 80, 70)
            )

            pygame.draw.rect(
                screen, fill_color,
                (
                    bar_x, bar_y,
                    int(bar_width * fraction), bar_height
                ),
                border_radius=7
            )

            seconds_left = math.ceil(remaining / 1000)
            timer_text = self.font_small.render(
                f"Time left: {seconds_left}s",
                True, (240, 240, 240)
            )
            screen.blit(
                timer_text,
                (
                    self.width // 2 - timer_text.get_width() // 2,
                    bar_y + 22
                )
            )

        if self.state == "GAME_OVER":
            overlay = pygame.Surface(
                (self.width, self.height), pygame.SRCALPHA
            )
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))

            over_surf = self.font_title.render(
                "GAME OVER", True, (240, 70, 70)
            )
            screen.blit(
                over_surf,
                (
                    self.width // 2 - over_surf.get_width() // 2,
                    self.height // 2 - 40
                )
            )

            final_score_surf = self.font_medium.render(
                f"Final Score: {self.score}",
                True, (255, 255, 255)
            )
            screen.blit(
                final_score_surf,
                (
                    self.width // 2 - final_score_surf.get_width() // 2,
                    self.height // 2 + 10
                )
            )

            restart_surf = self.font_medium.render(
                "Press [R] to Play Again",
                True, (200, 200, 200)
            )
            screen.blit(
                restart_surf,
                (
                    self.width // 2 - restart_surf.get_width() // 2,
                    self.height // 2 + 50
                )
            )
