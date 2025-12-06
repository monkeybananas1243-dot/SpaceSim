import pygame, math, random

class Ray():
    def __init__(self, size, speed, origin: tuple):
        self.size = size
        self.speed = speed
        self.origin = origin
        self.x = origin[0]
        self.y = origin[1]
        self.active = True
        self.vx = speed
        self.vy = 0
        self.affected = False
        self.dead_timer = 0
        self.DRAW_DURATION = 60 
    def update(self):
        if self.active:
            self.x += self.vx
            self.y += self.vy
        elif self.dead_timer > 0:
            self.dead_timer -= 1

        if self.x > WIDTH + 50 or self.x < -50 or self.y > HEIGHT + 50 or self.y < -50:
            self.active = False
    def draw(self, window):
        if self.active:
            if self.affected:
                color = (255, 255, 255)
                # Affected, turn red
                pygame.draw.circle(window, color, (int(self.x), int(self.y)), self.size)
            else:
                color = (100, 100, 100)
            
            pygame.draw.circle(window, color, (int(self.x), int(self.y)), self.size)

        elif self.dead_timer > 0:
            # You hit the black hole, turn white
            pygame.draw.circle(window, (255, 255, 255), (int(self.x), int(self.y)), self.size)       

    def set_dead(self):
        self.active = False
        self.dead_timer = self.DRAW_DURATION

    def attract(self, bh_center_x, bh_center_y, GRAVITY_STRENGTH):
        if not self.active:
            return
            
        dx = bh_center_x - self.x
        dy = bh_center_y - self.y
        
        distance = math.hypot(dx, dy)
        
        if distance > 1:
            ux = dx / distance
            uy = dy / distance
            
            self.affected = True

            self.vx += ux * GRAVITY_STRENGTH
            self.vy += uy * GRAVITY_STRENGTH

pygame.init()

def draw(window):
    window.fill((20, 20, 20))

WIDTH, HEIGHT = 1000, 600

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Black Hole")

Time = pygame.Clock()

BH_RADIUS = 100
GRAVITY_RADIUS = 250
GRAVITY_STRENGTH = 0.3
running = True
rays = []

RAY_FREQUENCY = 1
RAYS_PER_FRAME = 100
spawn_counter = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


    draw(WINDOW)

    gravity_zone = pygame.draw.circle(WINDOW, (255, 0, 0, 50), (500, 300), GRAVITY_RADIUS, 1) 
    blackhole = pygame.draw.circle(WINDOW, (0, 0, 0), (500, 300), BH_RADIUS)

    bh_center_x = blackhole.centerx
    bh_center_y = blackhole.centery

    spawn_counter += 1

    if spawn_counter >= RAY_FREQUENCY:
        spawn_counter = 0

        for _ in range(RAYS_PER_FRAME): 
            start_x = random.randint(0, WIDTH)
            start_y = random.randint(0, HEIGHT)

            new_ray = Ray(1, 1, (start_x, start_y))
            rays.append(new_ray)
        
        for _ in range(RAYS_PER_FRAME):

            start_x = random.randint(0, WIDTH)
            start_y = 0

            new_ray = Ray(1, 3.5, (start_x, start_y))

            new_ray.vx = 0
            new_ray.vy = new_ray.speed

            rays.append(new_ray)

    for ray in rays:
        
        distance_to_bh_center = math.hypot(ray.x - bh_center_x, ray.y - bh_center_y)
        
        if ray.active and distance_to_bh_center < GRAVITY_RADIUS:
            ray.attract(bh_center_x, bh_center_y, GRAVITY_STRENGTH)
        
        if ray.active and distance_to_bh_center < (ray.size+BH_RADIUS):
            ray.set_dead()
            

        ray.update()

    rays = [ray for ray in rays if ray.active or ray.dead_timer > 0]

    for ray in rays:
        ray.draw(WINDOW)

    pygame.display.flip()
    
    Time.tick(60)

pygame.quit()