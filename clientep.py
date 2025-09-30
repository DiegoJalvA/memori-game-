# =================== JUEGO DE MEMORIA EDUCATIVO - VERSIÓN SOLO UN JUGADOR ===================
import pygame
import sys
import random
import pickle
import time
import string
import os
import json
from pygame import mixer

# ---------------- CONSTANTES ----------------
WIDTH, HEIGHT = 1000, 700
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHTGRAY = (230, 230, 230)
RED = (220, 0, 0)
GREEN = (0, 180, 0)
BLUE = (0, 120, 255)
LIGHTBLUE = (173, 216, 230)
YELLOW = (255, 225, 0)
PURPLE = (180, 0, 255)
ORANGE = (255, 165, 0)
CARD_COLOR = (255, 215, 0)  # Oro
CARD_FLIPPED_COLOR = (255, 255, 224)  # Beige
CARD_MATCHED_COLOR = (50, 205, 50)  # Verde lima
BUTTON_COLOR = (70, 130, 180)  # Azul acero
BUTTON_HOVER_COLOR = (100, 149, 237)  # Azul real
BUTTON_ALT_COLOR = (244, 164, 96)  # Naranja arenoso
BUTTON_ALT_HOVER = (255, 165, 0)  # Naranja
BUTTON_TEXT_COLOR = WHITE
SCREEN_BG = (25, 25, 112)  # Azul marino
DIALOG_BG = (72, 61, 139)  # Púrpura oscuro
FONT_NAME = "Arial"

# Constantes de validación
MAX_NAME_LENGTH = 15
MAX_CARD_TEXT_LENGTH = 20
VALID_MODES = ["País-Capital", "Matemáticas", "Español-Inglés"]
VALID_DIFFICULTIES = ["Fácil", "Medio", "Difícil"]

# Configuración manual de cartas y layout por dificultad
DIFICULTAD_CONFIG = {
    "Fácil": {
        "total_cartas": 12,     # 4 pares (8 cartas)
        "cols": 4,             # 4 columnas
        "rows": 3              # 2 filas
    },
    "Medio": {
        "total_cartas": 16,    # 6 pares (12 cartas)
        "cols": 4,             # 4 columnas
        "rows": 4              # 3 filas
    },
    "Difícil": {
        "total_cartas": 36,    # 9 pares (18 cartas)
        "cols": 6,             # 6 columnas
        "rows": 6              # 3 filas
    }
}

# ---------------- INICIALIZACIÓN PYGAME ----------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("MEMORI GAME")
clock = pygame.time.Clock()

# ---------------- INICIALIZACIÓN DE SONIDO ----------------
flip_sound = None
match_sound = None
win_sound = None
click_sound = None
try:
    mixer.init()
    if os.path.exists("flip.wav"):
        flip_sound = mixer.Sound("flip.wav")
    if os.path.exists("match.wav"):
        match_sound = mixer.Sound("match.wav")
    if os.path.exists("win.wav"):
        win_sound = mixer.Sound("win.wav")
    if os.path.exists("click.wav"):
        click_sound = mixer.Sound("click.wav")
except Exception as e:
    print(f"Advertencia: No se pudieron cargar los sonidos: {e}")

# ---------------- FUNCIONES DE VALIDACIÓN ----------------
def validar_nombre(nombre):
    if not nombre or not nombre.strip():
        return "Jugador"
    nombre = ''.join(c for c in nombre if c.isalnum() or c in " _-")
    return nombre.strip()[:MAX_NAME_LENGTH]

def validar_texto_carta(texto):
    if not texto:
        return " "
    texto = str(texto)
    if len(texto) > MAX_CARD_TEXT_LENGTH:
        return texto[:MAX_CARD_TEXT_LENGTH-3] + "..."
    return texto

def validar_modo(modo):
    return modo if modo in VALID_MODES else VALID_MODES[0]

def validar_dificultad(dificultad):
    return dificultad if dificultad in VALID_DIFFICULTIES else VALID_DIFFICULTIES[0]

# ---------------- CARGAR/CREAR RÉCORDS ----------------
def load_highscores():
    try:
        if os.path.exists("highscores.json"):
            with open("highscores.json", "r", encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return {"País-Capital": 0, "Matemáticas": 0, "Español-Inglés": 0}

def save_highscore(mode, score):
    highscores = load_highscores()
    if score > highscores.get(mode, 0):
        highscores[mode] = score
        try:
            with open("highscores.json", "w", encoding='utf-8') as f:
                json.dump(highscores, f, ensure_ascii=False)
            return True
        except:
            pass
    return False

# ---------------- GENERAR CARTAS ----------------
def generar_cartas(modo, dificultad):
    cartas = []
    total_cartas = DIFICULTAD_CONFIG[dificultad]["total_cartas"]
    total_pares = total_cartas // 2  # Número de pares
    
    if modo == "País-Capital":
        paises = {
            "Quito": "Ecuador", "Lima": "Perú", "Bogotá": "Colombia",
            "Santiago": "Chile", "Buenos Aires": "Argentina", "Brasilia": "Brasil",
            "Caracas": "Venezuela", "Montevideo": "Uruguay", "Asunción": "Paraguay",
            "La Paz": "Bolivia", "Ciudad de México": "México", "San José": "Costa Rica",
            "Panamá": "Panamá", "Havana": "Cuba", "Madrid": "España", "Lisboa": "Portugal",
            "París": "Francia", "Roma": "Italia", "Berlín": "Alemania", "Tokio": "Japón"
        }
        items = random.sample(list(paises.items()), total_pares)
        for p, c in items:
            cartas.append({"front": p, "back": c, "flipped": False, "matched": False})
            cartas.append({"front": c, "back": p, "flipped": False, "matched": False})
    
    elif modo == "Matemáticas":
        operaciones = []
        for _ in range(total_pares):
            a = random.randint(1, 10)
            b = random.randint(1, 10)
            op = random.choice(["+", "-", "*"])
            if op == "+": res = a + b
            elif op == "-":
                res = a - b
                if res < 0: a, b = b, a; res = a - b
            elif op == "*": res = a * b
            operaciones.append((f"{a} {op} {b}", str(res)))
        for op, res in operaciones:
            cartas.append({"front": op, "back": res, "flipped": False, "matched": False})
            cartas.append({"front": res, "back": op, "flipped": False, "matched": False})
    
    elif modo == "Español-Inglés":
        palabras = {
            "Casa": "House", "Perro": "Dog", "Gato": "Cat", "Agua": "Water",
            "Sol": "Sun", "Luna": "Moon", "Cielo": "Sky", "Fuego": "Fire",
            "Libro": "Book", "Escuela": "School", "Amigo": "Friend",
            "Familia": "Family", "Comida": "Food", "Ciudad": "City",
            "País": "Country", "Música": "Music", "Auto": "Car", "Avión": "Plane"
        }
        items = random.sample(list(palabras.items()), total_pares)
        for e, i in items:
            cartas.append({"front": e, "back": i, "flipped": False, "matched": False})
            cartas.append({"front": i, "back": e, "flipped": False, "matched": False})
    
    random.shuffle(cartas)
    return cartas

# ---------------- FUNCIONES DE INTERFAZ ----------------
def draw_text(text, font_size, color, x, y, align="left"):
    font = pygame.font.SysFont(FONT_NAME, font_size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if align == "center":
        text_rect.center = (x, y)
    elif align == "right":
        text_rect.right = x
        text_rect.top = y
    else:
        text_rect.left = x
        text_rect.top = y
    screen.blit(text_surface, text_rect)
    return text_rect

def draw_button(text, x, y, width, height, color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR, text_color=WHITE):
    mouse_pos = pygame.mouse.get_pos()
    button_rect = pygame.Rect(x, y, width, height)
    if button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, hover_color, button_rect, border_radius=15)
        pygame.draw.rect(screen, (255, 215, 0), button_rect, 3, border_radius=15)  # Borde dorado
    else:
        pygame.draw.rect(screen, color, button_rect, border_radius=15)
        pygame.draw.rect(screen, (255, 255, 0), button_rect, 2, border_radius=15)  # Borde amarillo
    font = pygame.font.SysFont(FONT_NAME, 24)
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=button_rect.center)
    screen.blit(text_surf, text_rect)
    return button_rect

def draw_card(card, x, y, width, height):
    if card["matched"]:
        pygame.draw.rect(screen, CARD_MATCHED_COLOR, (x, y, width, height), border_radius=15)
        pygame.draw.rect(screen, (0, 255, 0), (x, y, width, height), 4, border_radius=15)  # Borde verde brillante
    elif card["flipped"]:
        pygame.draw.rect(screen, CARD_FLIPPED_COLOR, (x, y, width, height), border_radius=15)
        pygame.draw.rect(screen, (255, 215, 0), (x, y, width, height), 3, border_radius=15)  # Borde dorado
    else:
        pygame.draw.rect(screen, CARD_COLOR, (x, y, width, height), border_radius=15)
        pygame.draw.rect(screen, (0, 0, 0), (x, y, width, height), 3, border_radius=15)  # Borde negro
    
    if card["flipped"] or card["matched"]:
        font_size = 20 if len(str(card["front"])) < 10 else 16
        font = pygame.font.SysFont(FONT_NAME, font_size)
        text = font.render(str(card["front"]), True, BLACK)
        text_rect = text.get_rect(center=(x + width//2, y + height//2))
        screen.blit(text, text_rect)

def play_sound(sound):
    if sound:
        try:
            sound.play()
        except:
            pass

# ---------------- CLIENTE PRINCIPAL ----------------
class Client:
    def __init__(self):
        self.running = True
        self.state = "inicio"
        self.name = "Jugador"
        self.modo = "País-Capital"
        self.dificultad = "Fácil"
        self.input_text = ""
        self.input_active = False
        self.cartas = []
        self.flipped = []
        self.scores = [0, 0] # scores[0] es el jugador, scores[1] no se usa
        self.highscores = load_highscores()
        self.timer = 0
        self.timer_active = False
        self.game_over = False
        self.winner = -1
        self.editing_name = False
        self.show_modes_dialog = False
        self.show_difficulty_dialog = False
        self.show_records_dialog = False
        
        # Nuevo estado para manejar el tiempo de espera
        self.checking_match = False
        self.check_timer = 0
        self.match_result = None  # True para match, False para no match

    def puede_voltear_carta(self, index):
        if not self.cartas or index < 0 or index >= len(self.cartas):
            return False
        if self.game_over or self.checking_match:
            return False
        carta = self.cartas[index]
        if carta["flipped"] or carta["matched"]:
            return False
        if len(self.flipped) >= 2:
            return False
        return True

    # ---------------- MÉTODOS DE JUEGO ----------------
    def start_game(self):
        self.state = "juego"
        self.timer = 0
        self.timer_active = True
        self.game_over = False
        self.winner = -1
        self.flipped = []
        self.cartas = generar_cartas(self.modo, self.dificultad)
        self.scores = [0, 0] # Reiniciar puntuación
        self.checking_match = False
        self.check_timer = 0
        self.match_result = None

    def click_juego(self, pos):
        if not self.cartas or self.game_over or self.checking_match:
            return

        # Obtener configuración de layout
        config = DIFICULTAD_CONFIG[self.dificultad]
        cols = config["cols"]
        rows = config["rows"]
        
        size = min(WIDTH // cols, (HEIGHT - 100) // rows)
        
        # Calcular posición central para las cartas
        grid_width = cols * size
        grid_height = rows * size
        start_x = (WIDTH - grid_width) // 2
        start_y = (HEIGHT - grid_height) // 2 + 50  # Ajustar para dejar espacio para la info superior
        
        mx, my = pos
        for i, card in enumerate(self.cartas):
            row = i // cols
            col = i % cols
            cx = start_x + col * size
            cy = start_y + row * size
            if cx <= mx <= cx + size and cy <= my <= cy + size:
                if self.puede_voltear_carta(i):
                    card["flipped"] = True
                    self.flipped.append(i)
                    play_sound(flip_sound)
                    
                    # Si ya hay 2 cartas volteadas, iniciar verificación
                    if len(self.flipped) == 2:
                        self.checking_match = True
                        self.check_timer = 0
                        a, b = self.flipped
                        if (self.cartas[a]["back"] == self.cartas[b]["front"] or
                            self.cartas[a]["front"] == self.cartas[b]["back"]):
                            self.match_result = True
                        else:
                            self.match_result = False
                    break

    def update(self):
        if self.state == "juego" and not self.game_over and self.cartas:
            if self.checking_match:
                self.check_timer += 1/FPS
                if self.check_timer >= 0.3:
                    self.checking_match = False
                    a, b = self.flipped
                    if self.match_result:
                        self.cartas[a]["matched"] = True
                        self.cartas[b]["matched"] = True
                        self.scores[0] += 1 # Aumentar puntuación del jugador
                        play_sound(match_sound)
                    else:
                        self.cartas[a]["flipped"] = False
                        self.cartas[b]["flipped"] = False
                    self.flipped = []
                    self.match_result = None
                    
                    all_matched = all(card["matched"] for card in self.cartas)
                    if all_matched:
                        self.game_over = True
                        self.timer_active = False
                        play_sound(win_sound)

    def confirmar_salida(self):
        confirm = self.confirm_dialog("¿Seguro que desea salir del juego?")
        if confirm:
            self.state = "inicio"
            self.timer_active = False

    def alerta(self, mensaje):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        alert_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 50, 400, 100)
        pygame.draw.rect(screen, (255, 215, 0), alert_rect, border_radius=15)
        pygame.draw.rect(screen, (255, 0, 0), alert_rect, 3, border_radius=15)
        
        draw_text(mensaje, 28, BLACK, WIDTH//2, HEIGHT//2 - 15, "center")
        draw_text("Clic para continuar", 20, GRAY, WIDTH//2, HEIGHT//2 + 15, "center")
        
        pygame.display.flip()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False

    def confirm_dialog(self, mensaje):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        dialog_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 75, 400, 150)
        pygame.draw.rect(screen, (255, 255, 0), dialog_rect, border_radius=15)
        pygame.draw.rect(screen, (255, 165, 0), dialog_rect, 3, border_radius=15)
        
        draw_text(mensaje, 28, BLACK, WIDTH//2, HEIGHT//2 - 30, "center")
        draw_text("Presiona Y para Sí, N para No", 20, GRAY, WIDTH//2, HEIGHT//2, "center")
        
        pygame.display.flip()
        waiting = True
        result = False
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        result = True
                        waiting = False
                    elif event.key == pygame.K_n:
                        result = False
                        waiting = False
        return result

    # ---------------- MÉTODOS DE DIBUJO ----------------
    def draw(self):
        # Fondo con estrellas
        screen.fill(SCREEN_BG)
        for i in range(100):
            x = (i * 73) % WIDTH
            y = (i * 57) % HEIGHT
            pygame.draw.circle(screen, (255, 255, 200), (x, y), 1)
        
        if self.state == "inicio":
            self.draw_inicio()
        elif self.state == "juego":
            self.draw_juego()
        pygame.display.flip()

    def draw_inicio(self):
        # Título principal con efecto de sombra y brillo
        draw_text("MEMORI GAME", 48, (255, 215, 0), WIDTH//2, 50, "center")
        draw_text("MEMORI GAME", 48, (255, 0, 0), WIDTH//2 + 2, 52, "center")  # Sombra
        #draw_text(" SOLO UN JUGADOR", 36, (0, 255, 255), WIDTH//2, 100, "center")
        #draw_text(" SOLO UN JUGADOR", 36, (0, 0, 255), WIDTH//2 + 2, 102, "center")  # Sombra
        
        draw_button("Nombre: " + self.name, WIDTH//2 - 150, 150, 300, 50, BUTTON_ALT_COLOR, BUTTON_ALT_HOVER)
        draw_button("Modo: " + self.modo, WIDTH//2 - 150, 220, 300, 50, BUTTON_ALT_COLOR, BUTTON_ALT_HOVER)
        draw_button("Dificultad: " + self.dificultad, WIDTH//2 - 150, 290, 300, 50, BUTTON_ALT_COLOR, BUTTON_ALT_HOVER)
        draw_button("Jugar Solo", WIDTH//2 - 150, 360, 300, 50)
        
        # Botón multijugador deshabilitado
        draw_button("(1vs1) - Proximamente", WIDTH//2 - 150, 430, 300, 50, GRAY, GRAY)
        draw_button("Ver Records", WIDTH//2 - 150, 500, 300, 50, PURPLE)
        
        if self.show_modes_dialog:
            self.draw_modes_dialog()
        if self.show_difficulty_dialog:
            self.draw_difficulty_dialog()
        if self.show_records_dialog:
            self.draw_records_dialog()
        if self.editing_name:
            self.draw_name_dialog()

    def draw_modes_dialog(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        dialog_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 150, 400, 300)
        pygame.draw.rect(screen, DIALOG_BG, dialog_rect, border_radius=15)
        pygame.draw.rect(screen, (255, 215, 0), dialog_rect, 3, border_radius=15)
        
        draw_text("SELECCIONAR MODO", 32, (255, 255, 0), WIDTH//2, HEIGHT//2 - 120, "center")
        
        draw_button("País-Capital", WIDTH//2 - 150, HEIGHT//2 - 100, 300, 50,
                   (0, 255, 255) if self.modo == "País-Capital" else BUTTON_ALT_COLOR)
        draw_button("Matemáticas", WIDTH//2 - 150, HEIGHT//2 - 30, 300, 50,
                   (0, 255, 255) if self.modo == "Matemáticas" else BUTTON_ALT_COLOR)
        draw_button("Español-Inglés", WIDTH//2 - 150, HEIGHT//2 + 40, 300, 50,
                   (0, 255, 255) if self.modo == "Español-Inglés" else BUTTON_ALT_COLOR)
        draw_button("Cerrar", WIDTH//2 - 50, HEIGHT//2 + 110, 100, 40, RED)

    def draw_difficulty_dialog(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        dialog_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 150, 400, 300)
        pygame.draw.rect(screen, DIALOG_BG, dialog_rect, border_radius=15)
        pygame.draw.rect(screen, (255, 215, 0), dialog_rect, 3, border_radius=15)
        
        draw_text("SELECCIONAR DIFICULTAD", 32, (255, 255, 0), WIDTH//2, HEIGHT//2 - 120, "center")
        
        draw_button("Fácil", WIDTH//2 - 150, HEIGHT//2 - 100, 300, 50,
                   (0, 255, 255) if self.dificultad == "Fácil" else BUTTON_ALT_COLOR)
        draw_button("Medio", WIDTH//2 - 150, HEIGHT//2 - 30, 300, 50,
                   (0, 255, 255) if self.dificultad == "Medio" else BUTTON_ALT_COLOR)
        draw_button("Difícil", WIDTH//2 - 150, HEIGHT//2 + 40, 300, 50,
                   (0, 255, 255) if self.dificultad == "Difícil" else BUTTON_ALT_COLOR)
        draw_button("Cerrar", WIDTH//2 - 50, HEIGHT//2 + 110, 100, 40, RED)

    def draw_records_dialog(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        dialog_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 150, 400, 350)
        pygame.draw.rect(screen, DIALOG_BG, dialog_rect, border_radius=15)
        pygame.draw.rect(screen, (255, 215, 0), dialog_rect, 3, border_radius=15)
        
        draw_text("RÉCORDS", 36, (255, 255, 0), WIDTH//2, HEIGHT//2 - 120, "center")
        draw_text(f"País-Capital: {self.highscores.get('País-Capital', 0)}", 28, (255, 255, 0), WIDTH//2, HEIGHT//2 - 60, "center")
        draw_text(f"Matemáticas: {self.highscores.get('Matemáticas', 0)}", 28, (255, 255, 0), WIDTH//2, HEIGHT//2 - 20, "center")
        draw_text(f"Español-Inglés: {self.highscores.get('Español-Inglés', 0)}", 28, (255, 255, 0), WIDTH//2, HEIGHT//2 + 20, "center")
        draw_text("Puntuaciones más altas en modo individual", 20, (173, 216, 230), WIDTH//2, HEIGHT//2 + 70, "center")
        draw_button("Cerrar", WIDTH//2 - 50, HEIGHT//2 + 140, 100, 40, RED)

    def draw_name_dialog(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        dialog_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 100, 400, 200)
        pygame.draw.rect(screen, DIALOG_BG, dialog_rect, border_radius=15)
        pygame.draw.rect(screen, (255, 215, 0), dialog_rect, 3, border_radius=15)
        
        draw_text("NOMBRE DE JUGADOR", 32, (255, 255, 0), WIDTH//2, HEIGHT//2 - 70, "center")
        
        input_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 20, 300, 40)
        pygame.draw.rect(screen, (255, 255, 224), input_rect, border_radius=10)
        pygame.draw.rect(screen, (255, 215, 0), input_rect, 2, border_radius=10)
        draw_text(self.input_text, 28, BLACK, WIDTH//2, HEIGHT//2 - 15, "center")
        draw_text("Presiona ENTER para confirmar", 18, (173, 216, 230), WIDTH//2, HEIGHT//2 + 30, "center")
        draw_text("ESC para cancelar", 18, (173, 216, 230), WIDTH//2, HEIGHT//2 + 55, "center")

    def draw_juego(self):
        # Fondo del juego con estrellas
        for i in range(50):
            x = (i * 89) % WIDTH
            y = (i * 101) % HEIGHT
            pygame.draw.circle(screen, (255, 255, 100), (x, y), 1)
        
        draw_text(f"Modo: {self.modo} - {self.dificultad}", 24, (255, 215, 0), 20, 20)
        draw_text(f"Puntos: {self.scores[0]}", 24, (0, 255, 255), WIDTH//2, 20, "center")
        draw_text(f"Tiempo: {int(self.timer)}s", 24, (255, 215, 0), WIDTH-20, 20, "right")

        # Dibujar cartas centradas
        config = DIFICULTAD_CONFIG[self.dificultad]
        cols = config["cols"]
        rows = config["rows"]
        
        size = min(WIDTH // cols, (HEIGHT - 150) // rows)
        
        # Calcular dimensiones del grid
        grid_width = cols * size
        grid_height = rows * size
        start_x = (WIDTH - grid_width) // 2
        start_y = (HEIGHT - grid_height) // 2 + 20  # Ajustar para dejar espacio para la info superior
        
        for i, card in enumerate(self.cartas):
            row = i // cols
            col = i % cols
            cx = start_x + col * size
            cy = start_y + row * size
            draw_card(card, cx, cy, size - 5, size - 5)
        
        draw_button("Salir", 50, HEIGHT-50, 150, 40, color=RED)

        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 215, 0, 150))  # Dorado con transparencia
            screen.blit(overlay, (0, 0))
            
            draw_text("¡Juego Terminado!", 48, (255, 0, 0), WIDTH//2, HEIGHT//2 - 50, "center")
            draw_text("¡Juego Terminado!", 48, (255, 255, 0), WIDTH//2 + 2, HEIGHT//2 - 48, "center")  # Sombra
            draw_text(f"Puntos: {self.scores[0]}", 36, (0, 255, 0), WIDTH//2, HEIGHT//2, "center")
            draw_text(f"Puntos: {self.scores[0]}", 36, (0, 0, 0), WIDTH//2 + 2, HEIGHT//2 + 2, "center")  # Sombra
            draw_text(f"Tiempo: {int(self.timer)} segundos", 36, (0, 255, 255), WIDTH//2, HEIGHT//2 + 40, "center")
            draw_text(f"Tiempo: {int(self.timer)} segundos", 36, (0, 0, 255), WIDTH//2 + 2, HEIGHT//2 + 42, "center")  # Sombra
            
            if save_highscore(self.modo, self.scores[0]):
                draw_text("¡Nuevo Récord!", 36, (255, 215, 0), WIDTH//2, HEIGHT//2 + 80, "center")
                draw_text("¡Nuevo Récord!", 36, (255, 0, 0), WIDTH//2 + 2, HEIGHT//2 + 82, "center")  # Sombra
            
            volver_btn = draw_button("Volver al Menú", WIDTH//2 - 100, HEIGHT//2 + 130, 200, 40)
            if volver_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                self.state = "inicio"
                self.game_over = False
                self.cartas = []
                self.flipped = []
                self.scores = [0, 0]
                self.winner = -1
                self.timer = 0
                self.timer_active = False

    # ---------------- MANEJO DE EVENTOS ----------------
    def handle_click(self, pos):
        try:
            x, y = pos
            if self.state == "inicio":
                self.handle_inicio_click(pos)
            elif self.state == "juego":
                self.handle_juego_click(pos)
        except Exception as e:
            print(f"Error manejando click: {e}")

    def handle_inicio_click(self, pos):
        # Si hay un diálogo abierto, manejar solo clics dentro del diálogo
        if self.editing_name:
            self.handle_name_dialog_click(pos)
            return
        elif self.show_modes_dialog:
            self.handle_modes_dialog_click(pos)
            return
        elif self.show_difficulty_dialog:
            self.handle_difficulty_dialog_click(pos)
            return
        elif self.show_records_dialog:
            self.handle_records_dialog_click(pos)
            return
        
        x, y = pos
        if WIDTH//2 - 150 <= x <= WIDTH//2 + 150:
            if 150 <= y <= 200:
                self.editing_name = True
                self.input_text = self.name
                play_sound(click_sound)
            elif 220 <= y <= 270:
                self.show_modes_dialog = True
                play_sound(click_sound)
            elif 290 <= y <= 340:
                self.show_difficulty_dialog = True
                play_sound(click_sound)
            elif 360 <= y <= 410:
                self.start_game()
                play_sound(click_sound)
            elif 430 <= y <= 480:
                # Botón multijugador clickeado - mostrar alerta
                self.alerta("Modo multijugador no disponible en esta versión.")
            elif 500 <= y <= 550:
                self.show_records_dialog = True
                play_sound(click_sound)

    def handle_juego_click(self, pos):
        x, y = pos
        if 50 <= x <= 200 and HEIGHT-50 <= y <= HEIGHT-10:
            self.confirmar_salida()
            play_sound(click_sound)
        elif not self.game_over:
            self.click_juego(pos)

    def handle_name_dialog_click(self, pos):
        # Calcular el rectángulo del diálogo
        dialog_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 100, 400, 200)
        if not dialog_rect.collidepoint(pos):
            # Si se clickea fuera del diálogo, cerrarlo
            self.editing_name = False
            self.input_text = ""
            return
        
        # Calcular el rectángulo del input
        input_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 20, 300, 40)
        if input_rect.collidepoint(pos):
            # El input ya está activo por defecto, no necesitamos más acción
            pass

    def handle_modes_dialog_click(self, pos):
        # Calcular el rectángulo del diálogo
        dialog_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 150, 400, 300)
        if not dialog_rect.collidepoint(pos):
            # Si se clickea fuera del diálogo, cerrarlo
            self.show_modes_dialog = False
            play_sound(click_sound)
            return
        
        x, y = pos
        if WIDTH//2 - 150 <= x <= WIDTH//2 + 150:
            if HEIGHT//2 - 100 <= y <= HEIGHT//2 - 50:
                self.modo = "País-Capital"
                self.show_modes_dialog = False
                play_sound(click_sound)
            elif HEIGHT//2 - 30 <= y <= HEIGHT//2 + 20:
                self.modo = "Matemáticas"
                self.show_modes_dialog = False
                play_sound(click_sound)
            elif HEIGHT//2 + 40 <= y <= HEIGHT//2 + 90:
                self.modo = "Español-Inglés"
                self.show_modes_dialog = False
                play_sound(click_sound)
        
        if WIDTH//2 - 50 <= x <= WIDTH//2 + 50 and HEIGHT//2 + 110 <= y <= HEIGHT//2 + 150:
            self.show_modes_dialog = False
            play_sound(click_sound)

    def handle_difficulty_dialog_click(self, pos):
        # Calcular el rectángulo del diálogo
        dialog_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 150, 400, 300)
        if not dialog_rect.collidepoint(pos):
            # Si se clickea fuera del diálogo, cerrarlo
            self.show_difficulty_dialog = False
            play_sound(click_sound)
            return
        
        x, y = pos
        if WIDTH//2 - 150 <= x <= WIDTH//2 + 150:
            if HEIGHT//2 - 100 <= y <= HEIGHT//2 - 50:
                self.dificultad = "Fácil"
                self.show_difficulty_dialog = False
                play_sound(click_sound)
            elif HEIGHT//2 - 30 <= y <= HEIGHT//2 + 20:
                self.dificultad = "Medio"
                self.show_difficulty_dialog = False
                play_sound(click_sound)
            elif HEIGHT//2 + 40 <= y <= HEIGHT//2 + 90:
                self.dificultad = "Difícil"
                self.show_difficulty_dialog = False
                play_sound(click_sound)
        
        if WIDTH//2 - 50 <= x <= WIDTH//2 + 50 and HEIGHT//2 + 110 <= y <= HEIGHT//2 + 150:
            self.show_difficulty_dialog = False
            play_sound(click_sound)

    def handle_records_dialog_click(self, pos):
        # Calcular el rectángulo del diálogo
        dialog_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 150, 400, 350)
        if not dialog_rect.collidepoint(pos):
            # Si se clickea fuera del diálogo, cerrarlo
            self.show_records_dialog = False
            play_sound(click_sound)
            return
        
        x, y = pos
        if WIDTH//2 - 50 <= x <= WIDTH//2 + 50 and HEIGHT//2 + 140 <= y <= HEIGHT//2 + 180:
            self.show_records_dialog = False
            play_sound(click_sound)

    # ---------------- BUCLE PRINCIPAL ----------------
    def main_loop(self):
        while self.running:
            clock.tick(FPS)
            if self.timer_active and self.state == "juego" and not self.game_over:
                self.timer += 1/60
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Solo procesar clics si no hay un diálogo activo
                    if not (self.editing_name or self.show_modes_dialog or self.show_difficulty_dialog or self.show_records_dialog):
                        self.handle_click(event.pos)
                    else:
                        # Si hay un diálogo abierto, solo procesar clics en ese diálogo
                        if self.editing_name:
                            self.handle_name_dialog_click(event.pos)
                        elif self.show_modes_dialog:
                            self.handle_modes_dialog_click(event.pos)
                        elif self.show_difficulty_dialog:
                            self.handle_difficulty_dialog_click(event.pos)
                        elif self.show_records_dialog:
                            self.handle_records_dialog_click(event.pos)
                
                if event.type == pygame.KEYDOWN:
                    if self.editing_name:
                        if event.key == pygame.K_RETURN:
                            self.editing_name = False
                            if self.input_text.strip() != "":
                                self.name = validar_nombre(self.input_text)
                            self.input_text = ""
                        elif event.key == pygame.K_ESCAPE:
                            self.editing_name = False
                            self.input_text = ""
                        elif event.key == pygame.K_BACKSPACE:
                            self.input_text = self.input_text[:-1]
                        else:
                            if len(self.input_text) < MAX_NAME_LENGTH:
                                self.input_text += event.unicode
                    elif event.key == pygame.K_ESCAPE:
                        if self.state == "juego":
                            self.confirmar_salida()
                        else:
                            self.show_modes_dialog = False
                            self.show_difficulty_dialog = False
                            self.show_records_dialog = False

            self.update()
            self.draw()

        pygame.quit()
        sys.exit()

# ---------------- EJECUCIÓN PRINCIPAL ----------------
if __name__ == "__main__":
    try:
        client = Client()
        client.main_loop()
    except Exception as e:
        print(f"Error crítico: {e}")
        import traceback
        traceback.print_exc()
        try:
            pygame.quit()
        except:
            pass