import threading
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from funcs import *

app = Ursina()
textures = {
    'sky': load_texture('assets/mid_day.tiff'),
}
sounds = {
    'punch': Audio('assets/punch_sound', loop=False, autoplay=False),
}
block_pick = 1

window.fps_counter.enabled = True
window.exit_button.visible = False


NPC_Talk = Text(text="", enabled=False, background=True, origin=(
    0, -1), position=(0, 0), color=color.white, background_color=color.white)
agree = Button(text="ok!", parent=NPC_Talk,  enabled=False, size=(.3, .1))
disagree = Button(text="no", parent=NPC_Talk, enabled=False, size=(.3, .1))
agree.text_entity.size = 1
disagree.text_entity.size = 1
in_task = False


def update():
 
	global block_pick
    
	if held_keys['left mouse'] or held_keys['right mouse']:
		hand.active()
	else:
		hand.passive()

    
	if NPC_Talk.enabled == True:

		#lock player movement
		player.set_position((10, .25, 13))
		player.rotation = (0, 0, 0)

		if mouse.visible == False:
			current_position_player = player.position
			player.set_position((current_position_player.x,
			                    current_position_player.y, current_position_player.z))

			mouse.visible = True
			mouse.locked = False
	else:

		if mouse.visible == True:
			mouse.visible = False
			mouse.locked = True
	inventory.update()


class Voxel(Button):
    def __init__(self, position=(0, 0, 0)):
        super().__init__(
            parent=scene,
            position=position,
            model='assets/block',
            origin_y=0.5,
            color=color.color(0, 0, random.uniform(0.9, 1)),
            scale=0.5)

    def input(self, key):
        if self.hovered:
            if key == 'left mouse down':
                sounds['punch'].play()
                #if block_pick == 1:
                #   voxel = Voxel(position=self.position +
                #                mouse.normal, texture=textures['g'])

            if key == 'right mouse down':
                sounds['punch'].play()
                destroy(self)


class Sky(Entity):
    def __init__(self):
        super().__init__(
            parent=scene,
            model='sphere',
            texture=textures['sky'],
            scale=1000,
            double_sided=True)


class Holding_Object:
    def __init__(self):
        self.current_object = None

    def set_object(self, new_object):
        self.current_object = new_object

    def get_object(self):
        return self.current_object


class Hand(Entity):
    def __init__(self):
        super().__init__(
            parent=camera.ui,
            model='assets/arm',
            scale=0.2,
            rotation=Vec3(150, -10, 0),
            position=Vec2(0.4, -0.6))

    def active(self):
        self.position = Vec2(0.3, -0.5)

    def passive(self):
        self.position = Vec2(0.4, -0.6)


class Inventory:
    def __init__(self):
        self.inventory = ["KOH", "H2O2"]
        self.holding = None
        self.text = Text(text="", origin=(
            0, 0), position=(0,0), scale=2)

    def pick_up(self, item):
        if len(self.inventory) < 10:  # limit inventory size to 10 items
            self.inventory.append(item)
            print(f"Picked up {item}")
        else:
            print("Inventory is full")

    def drop(self, item):
        if item in self.inventory:
            self.inventory.remove(item)
            print(f"Dropped {item}")
        else:
            print(f"{item} not found in inventory")

    def store(self):
        print("Inventory:", self.inventory)

    def switch(self, item):
        if item in self.inventory:
            self.holding = item
            holding.set_object(item)
            print(f"Switched to holding {item}")
        else:
            print(f"{item} not found in inventory")

    def update(self):
        self.text.text = f"Holding: {self.holding}\nPress 'Tab' to switch"


def npc_action():
    global in_task
    global task, reward, chemical, hint
    NPC_Talk.enabled = False
    text_size = NPC_Talk.world_scale
    button1_pos = ((NPC_Talk.position.x - text_size.x / 2 + .25)
                   * 0.03, (NPC_Talk.position.y - text_size.y / 2 - .05)*0.01)
    button2_pos = ((NPC_Talk.position.x + text_size.x / 2 - .25)
                   * 0.03, (NPC_Talk.position.y - text_size.y / 2 - .05)*0.01)

    agree.text = "Ok!"
    agree.scale = (.3, .1)
    agree.position = button1_pos
    agree.text_entity.size = 1

    def set_in_task():
        global in_task
        in_task = not in_task

    def disable_talk():
        setattr(NPC_Talk, 'enabled', False)
        set_in_task()

    agree.on_click = Func(disable_talk)

    disagree.text = "No"
    disagree.scale = (.3, .1)
    disagree.position = button2_pos
    disagree.text_entity.size = 1
    disagree.on_click = Func(setattr, NPC_Talk, 'enabled', False)

    if player.position.x >= npc.position.x - 4 and player.position.x <= npc.position.x + 4 and player.position.z >= npc.position.z - 4 and player.position.z <= npc.position.z + 4:
        print("Currently: " + holding.get_object() + " We need: " + chemical)
        if in_task == False:
            NPC_Talk.enabled = True
            agree.enabled = True
            disagree.enabled = True

            thread = threading.Thread(target=speak_text, args=(NPC_Talk.text,))
            thread.start()
            NPC_Talk.background = True
        elif in_task == True and holding.get_object() != chemical:
            NPC_Talk.text = "hmm, doesnt look like you have the thing i need in your hand right now, come back when you have it!"
            NPC_Talk.enabled = True

            invoke(setattr, NPC_Talk, 'enabled', False, delay=5)
        elif in_task == True and holding.get_object() == chemical:
            NPC_Talk.text = "Oh, you have the thing i need! Thank you so much! Here is your money!"
            NPC_Talk.enabled = True
            invoke(setattr, NPC_Talk, 'enabled', False, delay=5)

        else:
            print("elsed")
            pass



# Define the objective text and money text
hint_popup = Text(text="Press H for a hint with the quest!", position=(
	-0.3, .45), origin=(0, 0), color=color.white, scale=1, background=True)
objective_text = Text(text="Objective: Get Potassium hydrochloride", position=(
	0.3, .45), origin=(0, 0), color=color.white, scale=1, background=True)
money_text = Text(text="Money: 0₫", position=(0.7, .45), origin=(
	0, 0), color=color.yellow, scale=1,  background=True)


npc_model = load_model("npc.glb")
npc = Entity(
    model=npc_model,
    position=(10, .25, 15),
    scale=1.75,
    rotation=(0, 0, 0),
    collider='box',
    on_click=npc_action)


for z in range(30):
    for x in range(30):
        voxel = Voxel(position=(x, 0, z))

task, reward, chemical, hint = str, str,str,str

def inisialise():
    global task, reward, chemical, hint
    task, reward, chemical, hint = set_quest(money_text, objective_text, 2, NPC_Talk)
    holding.set_object("none")
    play_loop_music()


player = FirstPersonController()
player.set_position((10, 0, 10))

sky = Sky()
hand = Hand()
holding = Holding_Object()
inventory = Inventory()


def input(key):
    if key == 'tab':
        inventory.switch(inventory.inventory[0] if inventory.holding !=
                         inventory.inventory[0] else inventory.inventory[1])


inisialise()
app.run()
