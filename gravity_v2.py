import pygame, math

pygame.init()

WIDTH, HEIGHT = 1000, 600

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Planets")
CLOCK = pygame.time.Clock()

G = G = 6.67430e-11
TIME_SCALE = 10
planets = []

class Planet:
    def __init__(self, mass, size, x, y, z, color=(255, 255, 255)):
        self.mass = mass / 1e18
        self.color = color
        self.size = max(5, int(size / 2e6))
        self.x = x
        self.y = y
        self.z = z
        self.vx = 0
        self.vy = 0
        self.vz = 0
        self.net_fx = 0.0
        self.net_fy = 0.0
        self.net_fz = 0.0
        self.gravitational_area = self.size * 2
        self.rect = pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)
    
    def get_gravitational_force(self, m1, m2, d):
        self.gravitational_force = ((G * m1 * m2) / d) // 100_000
    
    def attract(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        dz = other.z - self.z
        distance = math.sqrt(dx**2 + dy**2 + dz**2)

        if distance == 0:
            return

        epsilon_sq = 1e-6
        distance_sq = distance**2 + epsilon_sq

        F = (G * self.mass * other.mass) / distance_sq

        Fx = F * (dx / distance)
        Fy = F * (dy / distance)
        Fz = F * (dz / distance)

        self.net_fx += Fx
        self.net_fy += Fy
        self.net_fz += Fz

    def update_position(self):
        ax = self.net_fx / self.mass
        ay = self.net_fy / self.mass
        az = self.net_fz / self.mass

        self.vx += ax * TIME_SCALE
        self.vy += ay * TIME_SCALE
        self.vz += az * TIME_SCALE
        
        self.x += self.vx
        self.y += self.vy
        self.z += self.vz

        self.net_fx = 0.0
        self.net_fy = 0.0
        self.net_fz = 0.0

        self.rect.center = (int(self.x), int(self.y))

    def get_screen_coords(self, camera):
        x_view = self.x - camera.x
        y_view = self.y - camera.y
        z_view = self.z - camera.z

        x_view, y_view, z_view = self.rotate(x_view, y_view, z_view, camera.pitch, camera.yaw)
        
        if z_view >= 0:
            return None, None, None

        f = camera.focal_length
        
        screen_x = (x_view * f) / z_view + (WIDTH / 2)
        screen_y = (y_view * f) / z_view + (HEIGHT / 2)
        
        projected_size = abs((self.size * f) / z_view)
        
        return int(screen_x), int(screen_y), int(projected_size)
    
    def draw(self, camera):
        center_x, center_y, current_size = self.get_screen_coords(camera)

        if center_x is not None:
            if 0 < center_x < WIDTH and 0 < center_y < HEIGHT:
                final_size = max(1, min(100, current_size))
                
                self.rect = pygame.draw.aacircle(
                    WINDOW, 
                    self.color, 
                    (center_x, center_y), 
                    final_size
                )

    def rotate(self, x, y, z, pitch, yaw):
        return rotate_point(x, y, z, pitch, yaw)

    def check_collision(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        dz = other.z - self.z

        distance = math.sqrt(dx**2 + dy**2 + dz**2)
        
        if distance < self.size + other.size:
            return True
        return False
    
    def __str__(self):
        return f"[\nx={round(self.x, 1)}, \n y={round(self.x, 1)}, \n size={self.size}, \n mass={self.mass} \n]"
    
def rotate_point(x, y, z, pitch, yaw):
    rotated_x = x * math.cos(yaw) - z * math.sin(yaw)
    rotated_z = x * math.sin(yaw) + z * math.cos(yaw)
    
    final_y = y * math.cos(pitch) - rotated_z * math.sin(pitch)
    final_z = y * math.sin(pitch) + rotated_z * math.cos(pitch)
    
    return rotated_x, final_y, final_z
    
def draw_grid(window, camera, color, spacing, grid_range, y_plane=0):

    min_x = -grid_range
    max_x = grid_range
    min_z = -grid_range
    max_z = grid_range

    for x in range(min_x, max_x + 1, spacing):

        prev_point = None
        for z in range(min_z, max_z + 1, spacing):
            world_x = x
            world_y = y_plane
            world_z = z

            x_v = world_x - camera.x
            y_v = world_y - camera.y
            z_v = world_z - camera.z

            x_v, y_v, z_v = rotate_point(x_v, y_v, z_v, camera.pitch, camera.yaw)

            if z_v >= 0:
                prev_point = None
                continue

            f = camera.focal_length
            screen_x = (x_v * f) / z_v + WIDTH / 2
            screen_y = (y_v * f) / z_v + HEIGHT / 2

            if prev_point:
                pygame.draw.line(
                    window, (255, 0, 0),
                    prev_point,
                    (screen_x, screen_y), 1
                )

            prev_point = (screen_x, screen_y)

    for z in range(min_z, max_z + 1, spacing):

        prev_point = None
        for x in range(min_x, max_x + 1, spacing):
            world_x = x
            world_y = y_plane
            world_z = z

            x_v = world_x - camera.x
            y_v = world_y - camera.y
            z_v = world_z - camera.z

            x_v, y_v, z_v = rotate_point(x_v, y_v, z_v, camera.pitch, camera.yaw)

            if z_v >= 0:
                prev_point = None
                continue

            f = camera.focal_length
            screen_x = (x_v * f) / z_v + WIDTH / 2
            screen_y = (y_v * f) / z_v + HEIGHT / 2

            if prev_point:
                pygame.draw.line(window, color, prev_point, (screen_x, screen_y), 1)

            prev_point = (screen_x, screen_y)


earth = Planet(
    mass=5.972e24, 
    size=6371000, 
    x=WIDTH // 4+200, 
    y=0,
    z=0, 
    color=(0, 255, 255)
)
earth.vy = 1.9
earth.vz = 0.5

sun = Planet(
    mass=1.989e30,
    size=695700000//10, 
    x=HEIGHT//2, 
    y=0,
    z=0,
    color=(255, 255, 0)
)

mars = Planet(
    mass=6.39e23, 
    size=3389500, 
    x=WIDTH * 3 // 4+200, 
    y=0,
    z=0,
    color=(255, 0, 0)
)
mars.vy = -1.9
mars.vz = -0.2

jupiter = Planet(
    mass=1.899e27,
    size=69911000//2, 
    x=WIDTH // 4+200,
    y=300,
    z=0,
    color=(176, 157, 95)
)
jupiter.vx = 1.09
jupiter.vy = 1.5
jupiter.vz = 0.0

black_hole = Planet(
    mass=8.54e36//1_000_000,
    size= 2.47e10//100_000,
    x =WIDTH // 2,
    y=0,
    z=-1000,
    color=(0, 0, 0)
)

black_hole.vx = -0.09
black_hole.vz = 0.8

planets.append(earth)
planets.append(sun)
planets.append(mars)
planets.append(jupiter)
planets.append(black_hole)

FPS = 60
running = True

class Camera:
    def __init__(self, x=0, y=0, z=-1000, pitch=0, yaw=0, focal_length=500):
        self.x = x
        self.y = y
        self.z = z
        
        self.pitch = pitch
        self.yaw = yaw     
        
        self.focal_length = focal_length

CAMERA = Camera(x=WIDTH // 2, y=HEIGHT // 2, z=-1000, yaw=-98)

rotating = False

while running:
    CLOCK.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 2:
                old_mouse_pos = pygame.mouse.get_pos()
                rotating = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 2:
                rotating = False
        elif event.type == pygame.MOUSEMOTION and rotating:
            new_mouse_pos = pygame.mouse.get_pos()

            dx = new_mouse_pos[0] - old_mouse_pos[0]
            dy = new_mouse_pos[1] - old_mouse_pos[1]

            sensitivity = 0.005
            CAMERA.yaw += dx * sensitivity
            CAMERA.pitch += dy * sensitivity

            max_pitch = math.pi / 2 - 0.01
            CAMERA.pitch = max(-max_pitch, min(max_pitch, CAMERA.pitch))

            old_mouse_pos = new_mouse_pos
            
            print(dx, dy)

    keys = pygame.key.get_pressed()
    camera_speed = 10
    
    forward_x = math.sin(CAMERA.yaw) * math.cos(CAMERA.pitch) * camera_speed
    forward_y = -math.sin(CAMERA.pitch) * camera_speed
    forward_z = math.cos(CAMERA.yaw) * math.cos(CAMERA.pitch) * camera_speed
    
    strafe_x = math.cos(CAMERA.yaw) * camera_speed
    strafe_z = -math.sin(CAMERA.yaw) * camera_speed
    
    if keys[pygame.K_w]:
        CAMERA.x -= forward_x
        CAMERA.y += forward_y
        CAMERA.z -= forward_z
    if keys[pygame.K_s]:
        CAMERA.x += forward_x
        CAMERA.y -= forward_y
        CAMERA.z += forward_z

    if keys[pygame.K_a]:
        CAMERA.x += strafe_x
        CAMERA.z += strafe_z
    if keys[pygame.K_d]:
        CAMERA.x -= strafe_x
        CAMERA.z -= strafe_z

    if keys[pygame.K_e]:
        CAMERA.y -= camera_speed
    if keys[pygame.K_q]:
        CAMERA.y += camera_speed

    for p1 in planets:
        for p2 in planets:

            if p1 is p2:
                continue
            
            p1.attract(p2)

    planets_to_keep = []
    i = 0
    while i < len(planets):
        p1 = planets[i]
        p1.update_position()

        merged = False

        j = i + 1
        while j < len(planets):
            p2 = planets[j]
            if p1.check_collision(p2):

                if p1.mass >= p2.mass:
                    survivor = p1
                    removed = p2
                    removed_index = j
                else:
                    survivor = p2
                    removed = p1
                    removed_index = i
                
                new_vx = (p1.mass * p1.vx + p2.mass * p2.vx) / (p1.mass + p2.mass)
                new_vy = (p1.mass * p1.vy + p2.mass * p2.vy) / (p1.mass + p2.mass)
                total_mass = p1.mass + p2.mass
                new_vz = (p1.mass * p1.vz + p2.mass * p2.vz) / (p1.mass + p2.mass)
                total_mass = p1.mass + p2.mass
                
                survivor.mass = total_mass 
                survivor.vx = new_vx
                survivor.vy = new_vy
                survivor.vz = new_vz
                survivor.size = max(5, int(p1.mass**0.33) * 0.5)

                planets.pop(removed_index)
                
                if removed_index == i:
                    i -= 1
                    
                merged = True
                break
                
            else:
                j += 1
        
        i += 1

    WINDOW.fill((50, 50, 50))

    draw_grid(
        window=WINDOW, 
        camera=CAMERA, 
        color=(100, 100, 100), 
        spacing=100, 
        grid_range=1000
    )

    planets.sort(key=lambda p: p.z, reverse=True)

    for planet in planets:
        planet.draw(CAMERA)

    pygame.display.flip()

pygame.quit()