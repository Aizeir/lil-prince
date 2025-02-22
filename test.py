import pygame
import random
import math

pygame.init()

# Fenêtre
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Couleurs
WHITE = (255, 255, 255)
PLANET_COLOR = (0, 100, 255)

# Constantes
G = 0.5  # Constante gravitationnelle simulée
PLANET_SPAWN_RATE = 50  # Fréquence d'apparition des planètes

# Liste des planètes (x, y, vx, vy, rayon, masse)
planets = []

def create_planet():
    """Ajoute une nouvelle planète avec des propriétés aléatoires."""
    x = random.randint(100, WIDTH - 100)
    y = random.randint(100, HEIGHT - 100)
    radius = random.randint(10, 30)
    mass = radius * 10
    vx, vy = random.uniform(-1, 1), random.uniform(-1, 1)  # Mouvement initial

    planets.append([x, y, vx, vy, radius, mass])

def apply_gravity():
    """Applique la gravité entre les planètes."""
    for i in range(len(planets)):
        for j in range(i + 1, len(planets)):
            x1, y1, vx1, vy1, r1, m1 = planets[i]
            x2, y2, vx2, vy2, r2, m2 = planets[j]

            dx, dy = x2 - x1, y2 - y1
            distance = math.sqrt(dx**2 + dy**2) + 0.1  # Évite la division par 0

            # Gravité : F = G * (m1 * m2) / distance²
            force = G * (m1 * m2) / (distance**2)
            angle = math.atan2(dy, dx)
            fx, fy = force * math.cos(angle), force * math.sin(angle)

            # Appliquer la force gravitationnelle (accélération)
            planets[i][2] += fx / m1
            planets[i][3] += fy / m1
            planets[j][2] -= fx / m2
            planets[j][3] -= fy / m2

def move_planets():
    """Déplace les planètes selon leur vitesse."""
    for planet in planets:
        planet[0] += planet[2]  # x += vx
        planet[1] += planet[3]  # y += vy

def check_collisions():
    """Fusionne les planètes qui entrent en collision."""
    global planets
    new_planets = []
    merged = set()

    for i in range(len(planets)):
        if i in merged:
            continue

        x1, y1, vx1, vy1, r1, m1 = planets[i]
        merged_with = None

        for j in range(i + 1, len(planets)):
            if j in merged:
                continue

            x2, y2, vx2, vy2, r2, m2 = planets[j]
            dx, dy = x2 - x1, y2 - y1
            distance = math.sqrt(dx**2 + dy**2)

            if distance < r1 + r2:  # Collision détectée
                new_mass = m1 + m2
                new_radius = math.sqrt(r1**2 + r2**2)  # Approximation d'un volume conservé
                new_x, new_y = (x1 * m1 + x2 * m2) / new_mass, (y1 * m1 + y2 * m2) / new_mass
                new_vx, new_vy = (vx1 * m1 + vx2 * m2) / new_mass, (vy1 * m1 + vy2 * m2) / new_mass

                new_planets.append([new_x, new_y, new_vx, new_vy, new_radius, new_mass])
                merged.add(j)
                merged_with = True
                break

        if not merged_with:
            new_planets.append(planets[i])

    planets = new_planets

# Boucle de jeu
running = True
frame_count = 0
while running:
    screen.fill((0, 0, 0))

    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Création de nouvelles planètes aléatoirement
    if frame_count % PLANET_SPAWN_RATE == 0 and len(planets) < 20:
        create_planet()

    apply_gravity()
    move_planets()
    check_collisions()

    # Dessiner les planètes
    for x, y, _, _, radius, _ in planets:
        pygame.draw.circle(screen, PLANET_COLOR, (int(x), int(y)), int(radius))

    pygame.display.flip()
    clock.tick(60)
    frame_count += 1

pygame.quit()
