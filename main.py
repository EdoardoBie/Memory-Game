import pygame
import random
import os
import webbrowser

pygame.init()

WIDTH, HEIGHT = 1200, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Memory - Rivoluzione Americana")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

def load_images(image_folder):
    images = []
    for filename in os.listdir(image_folder):
        if filename.endswith(".png") or filename.endswith(".jpg"):
            img = pygame.image.load(os.path.join(image_folder, filename))
            img = pygame.transform.scale(img, (CARD_WIDTH - 20, CARD_HEIGHT - 20))
            images.append(img)
    return images

CARD_WIDTH, CARD_HEIGHT = 150, 200

class Card:
    def __init__(self, image, pos):
        self.image = image
        self.rect = pygame.Rect(pos[0], pos[1], CARD_WIDTH, CARD_HEIGHT)
        self.face_up = False
        self.matched = False
        self.angle = 0

    def draw(self, win):
        if self.matched:
            pygame.draw.rect(win, GOLD, self.rect, border_radius=10)
            win.blit(self.image, (self.rect.x + 10, self.rect.y + 10))
        elif self.face_up:
            pygame.draw.rect(win, WHITE, self.rect, border_radius=10)
            win.blit(self.image, (self.rect.x + 10, self.rect.y + 10))
        else:
            pygame.draw.rect(win, WHITE, self.rect, border_radius=10)
            pygame.draw.rect(win, BLACK, self.rect, 3, border_radius=10)
            font = pygame.font.SysFont("comicsans", 40)
            text = font.render("?", True, BLACK)
            win.blit(text, (self.rect.centerx - text.get_width() // 2, self.rect.centery - text.get_height() // 2))

    def flip(self):
        self.face_up = not self.face_up

    def animate(self):
        if self.face_up and self.angle < 180:
            self.angle += 10
        elif not self.face_up and self.angle > 0:
            self.angle -= 10

def create_deck(images):
    deck = []
    for img in images:
        deck.append(Card(img, (0, 0)))
        deck.append(Card(img, (0, 0)))
    random.shuffle(deck)
    return deck

def draw_deck(win, deck):
    for i, card in enumerate(deck):
        row = i // 6
        col = i % 6
        card.rect.topleft = (col * (CARD_WIDTH + 20) + 100, row * (CARD_HEIGHT + 20) + 100)
        card.draw(win)

def show_intro_screen():
    intro = True
    video_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)
    play_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)
    show_play_button = False

    while intro:
        WIN.fill(WHITE)
        
        font = pygame.font.SysFont("comicsans", 40)
        text = font.render("Prima di accedere al gioco,", True, BLACK)
        WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 100))

        text2 = font.render("è necessario visualizzare il seguente video:", True, BLACK)
        WIN.blit(text2, (WIDTH // 2 - text2.get_width() // 2, HEIGHT // 2 - 50))

        if not show_play_button:
            pygame.draw.rect(WIN, BLUE, video_button_rect, border_radius=10)
            button_font = pygame.font.SysFont("comicsans", 30)
            button_text = button_font.render("Guarda Video", True, WHITE)
            WIN.blit(button_text, (video_button_rect.centerx - button_text.get_width() // 2, video_button_rect.centery - button_text.get_height() // 2))

        if show_play_button:
            pygame.draw.rect(WIN, GREEN, play_button_rect, border_radius=10)
            button_font = pygame.font.SysFont("comicsans", 30)
            button_text = button_font.render("Accedi al Gioco", True, WHITE)
            WIN.blit(button_text, (play_button_rect.centerx - button_text.get_width() // 2, play_button_rect.centery - button_text.get_height() // 2))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if not show_play_button and video_button_rect.collidepoint(pos):
                    webbrowser.open("https://drive.google.com/file/d/1Yc1x8sgbpbMnLYEHkrq0UCXtQvxk-n_z/view?usp=sharingt")
                    show_play_button = True
                elif show_play_button and play_button_rect.collidepoint(pos):
                    return True

def main():
    if not show_intro_screen():
        return

    run = True
    clock = pygame.time.Clock()
    FPS = 60

    images = load_images("assets")[:9]
    deck = create_deck(images)

    selected_cards = []
    matched_pairs = 0
    waiting_to_flip_back = False
    flip_back_time = 0

    pygame.mixer.music.load("assets/background_music.mp3")
    pygame.mixer.music.play(-1)

    flip_sound = pygame.mixer.Sound("assets/click.mp3")
    match_sound = pygame.mixer.Sound("assets/applause.mp3")

    while run:
        clock.tick(FPS)
        WIN.fill(BLACK)

        background = pygame.image.load("assets/background.jpg")
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
        WIN.blit(background, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN and not waiting_to_flip_back:
                pos = pygame.mouse.get_pos()
                for card in deck:
                    if card.rect.collidepoint(pos) and not card.matched and not card.face_up:
                        card.flip()
                        flip_sound.play()
                        selected_cards.append(card)
                        if len(selected_cards) == 2:
                            if selected_cards[0].image == selected_cards[1].image:
                                selected_cards[0].matched = True
                                selected_cards[1].matched = True
                                match_sound.play()
                                matched_pairs += 1
                                selected_cards = []
                            else:
                                waiting_to_flip_back = True
                                flip_back_time = pygame.time.get_ticks() + 1000

        if waiting_to_flip_back and pygame.time.get_ticks() > flip_back_time:
            for card in selected_cards:
                card.flip()
            selected_cards = []
            waiting_to_flip_back = False

        draw_deck(WIN, deck)

        if matched_pairs == len(deck) // 2:
            font = pygame.font.SysFont("comicsans", 80)
            text = font.render("Hai Vinto!", True, BLUE)
            WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()