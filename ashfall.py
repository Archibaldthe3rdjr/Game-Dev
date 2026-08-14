import json, os, random, textwrap, time

# ASHFALL: REQUIEM OF THE HOLLOW KING
# A single-file, terminal RPG. Python 3 only - no external packages.

SAVE = 'ashfall_save.json'
random.seed()

WEAPONS = {
    'Rusty Blade': {'power': 8, 'speed': 2, 'crit': 3, 'value': 20, 'tag': 'balanced'},
    'Iron Sabre': {'power': 14, 'speed': 3, 'crit': 5, 'value': 100, 'tag': 'fast'},
    'Ranger Bow': {'power': 19, 'speed': 2, 'crit': 10, 'value': 180, 'tag': 'precise'},
    'Storm Rifle': {'power': 27, 'speed': 2, 'crit': 8, 'value': 360, 'tag': 'reliable'},
    'Void Carbine': {'power': 36, 'speed': 3, 'crit': 14, 'value': 700, 'tag': 'rare'},
    'Sunforged': {'power': 48, 'speed': 2, 'crit': 18, 'value': 1400, 'tag': 'legendary'},
}
ARMOUR = {
    'Cloth Coat': {'def': 2, 'hp': 0, 'value': 20},
    'Scrap Vest': {'def': 6, 'hp': 10, 'value': 80},
    'Ranger Mail': {'def': 11, 'hp': 25, 'value': 240},
    'Aegis Plate': {'def': 19, 'hp': 50, 'value': 650},
    'Void Mantle': {'def': 27, 'hp': 85, 'value': 1200},
}
ENEMIES = {
    'Ash Rat': (28, 7, 12, 20), 'Scavenger': (48, 10, 20, 30),
    'Mutant': (85, 15, 35, 55), 'Ravager': (130, 20, 55, 90),
    'Ash Knight': (210, 28, 90, 150), 'Void Hound': (300, 34, 130, 210),
    'Ash Witch': (240, 40, 150, 240), 'Crater Spawn': (430, 48, 230, 380),
}
BOSSES = {
    'The Warden': (900, 35, 650, 700),
    'Mother of Ash': (1500, 48, 1200, 1200),
    'Hollow King': (2400, 65, 3000, 2500),
}
REGIONS = ['Haven', 'Deadwood', 'Salt Flats', 'Blackwater', 'The Crater']

QUESTS = [
    ('A Rat in the Walls', 'Kill 5 Ash Rats', 'kill', 'Ash Rat', 5, 80),
    ('The Missing Scout', 'Search Deadwood for a missing scout', 'event', 'scout', 1, 120),
    ('Old Roots', 'Collect 5 Ember Roots', 'item', 'Ember Root', 5, 130),
    ('Scrap Economy', 'Collect 8 Iron Scrap', 'item', 'Iron Scrap', 8, 150),
    ('Crystal Fever', 'Collect 4 Ash Crystals', 'item', 'Ash Crystal', 4, 200),
    ('The Old Road', 'Reach the Salt Flats', 'region', 'Salt Flats', 1, 250),
    ('Broken Relay', 'Repair 3 ancient relays', 'relay', 'relay', 3, 300),
    ('A Voice Below', 'Complete a procedural ruin', 'dungeon', 'ruin', 1, 350),
    ('Blackwater', 'Reach Blackwater', 'region', 'Blackwater', 1, 350),
    ('The Warden', 'Defeat The Warden', 'boss', 'The Warden', 1, 700),
    ('Warden Core', 'Recover the Warden Core', 'item', 'Warden Core', 1, 600),
    ('Three Keys', 'Collect 3 Moon Shards', 'item', 'Moon Shard', 3, 800),
    ('The Crater Gate', 'Find the hidden gate', 'event', 'gate', 1, 700),
    ('Mother of Ash', 'Defeat Mother of Ash', 'boss', 'Mother of Ash', 1, 1200),
    ('The Last Archive', 'Complete an ancient archive dungeon', 'dungeon', 'archive', 1, 900),
    ('Forge of Ash', 'Craft an improved weapon', 'craft', 'weapon', 1, 600),
    ('Living Armour', 'Craft improved armour', 'craft', 'armour', 1, 600),
    ('The Obsidian Choice', 'Make a choice at the shrine', 'choice', 'shrine', 1, 900),
    ('The Final Vault', 'Reach the Hollow King', 'event', 'king', 1, 1200),
    ('The Hollow King', 'Defeat the Hollow King', 'boss', 'Hollow King', 1, 3000),
    ('A New Dawn', 'Choose the fate of Eldoria', 'ending', 'ending', 1, 0),
    ('The Historian', 'Learn the truth from Finch', 'choice', 'history', 1, 300),
    ('Debt Collector', 'Earn 1000 gold', 'gold', 'gold', 1000, 500),
    ('Master Explorer', 'Visit every region', 'explore', 'regions', 5, 1000),
]

class Player:
    def __init__(self, data=None):
        d = data or {}
        self.name = d.get('name', 'Wanderer')
        self.level = d.get('level', 1); self.xp = d.get('xp', 0); self.need = d.get('need', 100)
        self.hp = d.get('hp', 100); self.max_hp = d.get('max_hp', 100)
        self.stamina = d.get('stamina', 100); self.gold = d.get('gold', 80)
        self.weapon = d.get('weapon', 'Rusty Blade'); self.armour = d.get('armour', 'Cloth Coat')
        self.inv = d.get('inv', {'Iron Scrap': 3, 'Ember Root': 0, 'Ash Crystal': 0, 'Ancient Gear': 0, 'Moon Shard': 0, 'Void Dust': 0, 'Warden Core': 0, 'Medkit': 3})
        self.skills = d.get('skills', {'Might': 0, 'Survival': 0, 'Insight': 0})
        self.kills = d.get('kills', 0); self.crafted = d.get('crafted', 0)
        self.regions = d.get('regions', []); self.flags = d.get('flags', {})

    def pack(self): return self.__dict__.copy()
    @property
    def power(self): return WEAPONS[self.weapon]['power'] + self.level * 2 + self.skills['Might'] * 5
    @property
    def defence(self): return ARMOUR[self.armour]['def'] + self.skills['Survival'] * 3
    @property
    def crit(self): return WEAPONS[self.weapon]['crit'] + self.skills['Insight'] * 3

    def gain_xp(self, amount):
        self.xp += amount
        while self.xp >= self.need:
            self.xp -= self.need; self.level += 1; self.need = int(self.need * 1.32)
            self.max_hp += 12; self.hp = self.max_hp
            print('\n*** LEVEL UP! You are now level', self.level, '***')

class Game:
    def __init__(self):
        self.p = Player(); self.day = 1; self.hour = 8; self.running = True
        self.quests = {q[0]: {'done': False, 'progress': 0} for q in QUESTS}
        self.relations = {'Mara': 0, 'Dax': 0, 'Sera': 0, 'Rook': 0, 'Finch': 0}
        self.flags = {}; self.event_cooldown = 0; self.dungeon = None

    def save(self):
        data = {'player': self.p.pack(), 'day': self.day, 'hour': self.hour, 'quests': self.quests, 'relations': self.relations, 'flags': self.flags}
        with open(SAVE, 'w') as f: json.dump(data, f, indent=2)
        print('Game saved.')

    def load(self):
        if not os.path.exists(SAVE): print('No save exists.'); return
        try:
            with open(SAVE) as f: d = json.load(f)
            self.p = Player(d['player']); self.day = d['day']; self.hour = d['hour']; self.quests = d['quests']; self.relations = d['relations']; self.flags = d['flags']
            print('Save loaded.')
        except Exception as e: print('Save is damaged:', e)

    def advance(self, hours=1):
        self.hour += hours
        while self.hour >= 24: self.hour -= 24; self.day += 1
        self.event_cooldown -= hours
        if self.hour >= 21 or self.hour < 6: self.night_event()

    def header(self):
        print('\n' + '=' * 78)
        print(f'ASHFALL | Day {self.day} {int(self.hour):02d}:00 | LV {self.p.level} | HP {self.p.hp}/{self.p.max_hp} | GOLD {self.p.gold}')
        print(f'{self.p.weapon}  POW {self.p.power}  |  {self.p.armour}  DEF {self.p.defence}  |  Region: {self.region()}')
        print('=' * 78)

    def region(self):
        return self.flags.get('region', 'Haven')

    def say(self, who, text):
        print(f'\n{who}: "{text}"')

    def choose(self, prompt, options):
        print('\n' + prompt)
        for i, option in enumerate(options, 1): print(f'  [{i}] {option}')
        while True:
            a = input('> ').strip()
            if a.isdigit() and 1 <= int(a) <= len(options): return int(a)
            print('Choose a number from the list.')

    def start(self):
        print('\n' + '#' * 78)
        print('#' + ' ASHFALL: REQUIEM OF THE HOLLOW KING '.center(76) + '#')
        print('#' * 78)
        print('\nThe sky has been broken for seventy years.')
        print('Eldoria survives beneath a permanent storm of silver ash.')
        print('You wake outside Haven carrying a rusted blade and a message:')
        print('\n  "The machines are waking. Find the Hollow King before he finds you."')
        while True:
            a = self.choose('What do you do?', ['Begin the journey', 'Load a save', 'Quit'])
            if a == 1: self.p.name = input('Your name: ').strip() or 'Wanderer'; break
            if a == 2: self.load(); break
            return
        self.flags['region'] = 'Haven'
        self.main_loop()

    def main_loop(self):
        while self.running:
            self.header()
            print('[1] Explore  [2] Town  [3] Quests  [4] Character')
            print('[5] Skills   [6] Craft [7] Map    [8] Save')
            print('[9] Rest     [0] Quit')
            a = input('> ').strip()
            actions = {'1': self.explore, '2': self.town, '3': self.quest_menu, '4': self.character, '5': self.skill_menu, '6': self.craft_menu, '7': self.map_menu, '8': self.save, '9': self.rest, '0': self.quit}
            if a in actions:
                try: actions[a]()
                except (KeyboardInterrupt, EOFError): self.quit()
            else: print('Unknown command.')

    def explore(self):
        region = self.region()
        print(f'\nYou travel through {region}. The ash moves like snow around your boots.')
        self.advance(random.choice([1, 1, 2]))
        roll = random.random()
        if roll < .34: self.combat()
        elif roll < .52: self.random_event()
        elif roll < .66: self.find_loot()
        elif roll < .76: self.dungeon_menu()
        elif roll < .86: self.discover()
        else: print('The road is quiet. Too quiet.')

    def combat(self, forced=None):
        name = forced or random.choices(list(ENEMIES), weights=[25,20,14,10,6,4,3,2])[0]
        base = ENEMIES[name]; scale = 1 + (self.p.level - 1) * .12 + self.day * .025
        hp, dmg, xp, gold = [int(x * scale) for x in base]
        print(f'\n!!! {name.upper()} !!!  HP {hp}  DMG {dmg}')
        while hp > 0 and self.p.hp > 0:
            print(f'\nYour HP {self.p.hp}/{self.p.max_hp} | Enemy HP {hp}')
            a = self.choose('Your move:', ['Attack', 'Defend', 'Use Medkit', 'Flee'])
            if a == 1:
                power = self.p.power + random.randint(-3, 5)
                if random.randint(1, 100) <= self.p.crit: power *= 2; print('CRITICAL HIT!')
                hp -= max(1, power); print(f'You deal {max(1,power)} damage.')
            elif a == 2:
                dmg = max(1, dmg // 3); print('You brace for impact.')
            elif a == 3:
                if self.p.inv.get('Medkit', 0): self.p.inv['Medkit'] -= 1; self.p.hp = min(self.p.max_hp, self.p.hp + 45); print('You recover 45 HP.')
                else: print('No medkits.') ; continue
            else:
                if random.random() < .55: print('You escape.'); return
                print('You failed to escape!')
            if hp > 0:
                incoming = max(1, dmg - self.p.defence // 2)
                self.p.hp -= incoming; print(f'{name} hits you for {incoming}.')
        if self.p.hp <= 0:
            self.p.hp = max(1, self.p.max_hp // 2); self.p.gold = max(0, self.p.gold - 50); self.flags['region'] = 'Haven'
            print('You collapse and wake in Haven. You lost 50 gold.')
            return
        self.p.kills += 1; self.p.gold += gold; self.p.gain_xp(xp)
        print(f'Victory! +{gold} gold, +{xp} XP.')
        self.progress('kill', name)
        drops = random.sample(['Iron Scrap','Ember Root','Ash Crystal','Ancient Gear','Void Dust'], k=random.randint(0,2))
        for item in drops: self.add_item(item); print('Found:', item)

    def random_event(self):
        events = [self.event_traveller, self.event_cache, self.event_medic, self.event_mirror, self.event_ambush]
        random.choice(events)()

    def event_traveller(self):
        self.say('Stranger', 'The road ahead is dangerous. I can tell you what I know, for a price.')
        a = self.choose('Offer 20 gold?', ['Pay', 'Refuse', 'Threaten him'])
        if a == 1 and self.p.gold >= 20:
            self.p.gold -= 20; self.p.gain_xp(50); self.say('Stranger','Blackwater has started hearing voices beneath the water.')
        elif a == 3:
            print('He disappears into the ash. You feel watched.')
        else: print('The stranger shrugs and leaves.')

    def event_cache(self):
        print('You discover a sealed military cache.')
        a = self.choose('What do you do?', ['Force it open', 'Leave it', 'Search for a key'])
        if a == 1:
            self.add_item('Iron Scrap', 3); self.add_item('Ash Crystal'); print('You pry it open and find useful materials.')
        elif a == 3:
            self.advance(1); self.add_item('Ancient Gear', 2); print('A hidden key opens the cache.')
        else: print('You leave it untouched.')

    def event_medic(self):
        self.say('Wounded Ranger','Please... I need medicine.')
        a = self.choose('Help?', ['Give a Medkit', 'Give 15 gold', 'Walk away'])
        if a == 1 and self.p.inv.get('Medkit',0): self.p.inv['Medkit'] -= 1; self.relations['Sera'] += 2; self.p.gain_xp(60); print('The ranger survives.')
        elif a == 2 and self.p.gold >= 15: self.p.gold -= 15; self.relations['Sera'] += 1; print('She thanks you.')
        else: print('You continue alone.')

    def event_mirror(self):
        self.say('The Mirror','You have walked this road before. You simply do not remember.')
        a = self.choose('The mirror asks for a memory.', ['Touch it', 'Break it', 'Walk away'])
        if a == 1: self.p.flags['mirror'] = True; self.p.gain_xp(100); print('You see a flash of the old world.')
        elif a == 2: self.add_item('Void Dust',2); print('The mirror cracks and releases dark dust.')

    def event_ambush(self):
        print('A pack of scavengers surrounds you!')
        self.combat('Scavenger')
        if self.p.hp > 0 and random.random() < .5: self.combat('Scavenger')

    def find_loot(self):
        items = random.choices(['Iron Scrap','Ember Root','Ash Crystal','Ancient Gear','Moon Shard'], [35,25,20,15,5], k=random.randint(1,3))
        for item in items: self.add_item(item); print('You found', item)

    def discover(self):
        undiscovered = [r for r in REGIONS if r not in self.p.regions]
        if undiscovered:
            r = random.choice(undiscovered); self.flags['region'] = r; self.p.regions.append(r); self.progress('region', r); print('DISCOVERED:', r)
        else: print('You discover an abandoned camp. Nothing remains.')

    def dungeon_menu(self):
        print('\nA staircase descends beneath the ruins. Symbols glow on the walls.')
        self.procedural_dungeon(random.randint(3,7))

    def procedural_dungeon(self, rooms):
        names = ['Flooded Hall','Machine Chapel','Collapsed Archive','Ash Garden','Forgotten Barracks','Glass Corridor','Engine Vault']
        print(f'\n=== PROCEDURAL DUNGEON: {rooms} ROOMS ===')
        for i in range(1, rooms+1):
            print(f'\nRoom {i}/{rooms}: {random.choice(names)}')
            roll = random.random()
            if roll < .4: self.combat()
            elif roll < .7: self.find_loot()
            else:
                a = self.choose('A strange mechanism blocks the path.', ['Solve it', 'Force it', 'Search nearby'])
                if a == 1: self.p.gain_xp(80); self.add_item('Ancient Gear'); print('Puzzle solved.')
                elif a == 2: self.p.hp -= random.randint(5,20); print('The mechanism shocks you.')
                else: self.add_item(random.choice(['Iron Scrap','Ash Crystal']))
            if self.p.hp <= 0: break
        if self.p.hp > 0:
            print('\nYou reach the dungeon heart. An ancient machine speaks your name.')
            self.p.gain_xp(200); self.add_item('Moon Shard'); self.progress('dungeon', 'ruin')

    def town(self):
        while True:
            print('\n=== HAVEN ===')
            print('Mara watches the gates. Dax sorts equipment. Sera treats the wounded. Rook studies maps. Finch sits beside a dead machine.')
            a = self.choose('Who do you visit?', ['Mara - quests', 'Dax - shop', 'Sera - healing', 'Rook - rumours', 'Finch - history', 'Leave'])
            if a == 1: self.mara()
            elif a == 2: self.shop()
            elif a == 3: self.heal()
            elif a == 4: self.rook()
            elif a == 5: self.finch()
            else: return

    def mara(self):
        self.say('Mara','Eldoria is dying. The Hollow King is not a monster. He is what is left of our first king.')
        pending = [q for q in QUESTS if not self.quests[q[0]]['done']]
        if pending:
            q = pending[0]; self.say('Mara', f'Quest: {q[0]} — {q[1]}')
            if self.choose('Accept?', ['Accept', 'Not now']) == 1: self.quests[q[0]]['accepted'] = True; print('Quest tracked.')
        else: print('Mara: You have completed every known quest.')

    def shop(self):
        stock = list(WEAPONS.keys())[1:] + list(ARMOUR.keys())[1:] + ['Medkit']
        while True:
            print('\n=== DAX\'S SHOP ===')
            for i,n in enumerate(stock,1):
                price = WEAPONS[n]['value'] if n in WEAPONS else ARMOUR[n]['value'] if n in ARMOUR else 25
                print(f'[{i}] {n:<18} {price}g')
            print('[0] Leave')
            a=input('> ').strip()
            if a=='0': return
            if a.isdigit() and 1<=int(a)<=len(stock):
                n=stock[int(a)-1]; price=WEAPONS[n]['value'] if n in WEAPONS else ARMOUR[n]['value'] if n in ARMOUR else 25
                if self.p.gold < price: print('Not enough gold.'); continue
                self.p.gold -= price
                if n in WEAPONS: self.p.weapon=n
                elif n in ARMOUR: self.p.armour=n; self.p.max_hp=max(self.p.max_hp,100+ARMOUR[n]['hp'])
                else: self.add_item('Medkit')
                print('Purchased',n)

    def heal(self):
        cost=15
        if self.p.gold>=cost: self.p.gold-=cost; self.p.hp=self.p.max_hp; print('Sera restores you to full health.')
        else: print('You need 15 gold.')

    def rook(self):
        self.say('Rook','The Crater is a door. The Warden keeps the first key. Mother of Ash keeps the second.')
        a=self.choose('Ask about the Hollow King?', ['Yes','No'])
        if a==1: self.say('Rook','The King wants the world restored. The problem is that restoration means everyone remembers the Ashfall.')
        self.relations['Rook'] += 1

    def finch(self):
        self.say('Finch','Before the Ashfall, Eldoria built a machine called the Dawn Engine.')
        a=self.choose('Ask how it failed?', ['Tell me everything','Another time'])
        if a==1:
            self.say('Finch','The engine was built to rewrite reality. The first king used it once. The sky never recovered.')
            self.progress('choice','history')

    def quest_menu(self):
        print('\n=== QUEST LOG ===')
        for i,q in enumerate(QUESTS,1):
            st=self.quests[q[0]]; mark='DONE' if st['done'] else 'ACTIVE' if st.get('accepted') else 'LOCKED'
            print(f'{i:02}. [{mark:<6}] {q[0]} — {q[1]}')
        input('Press Enter...')

    def character(self):
        print('\n=== CHARACTER ===')
        print('Name:',self.p.name,' Level:',self.p.level,' XP:',self.p.xp,'/',self.p.need)
        print('Weapon:',self.p.weapon,WEAPONS[self.p.weapon]); print('Armour:',self.p.armour,ARMOUR[self.p.armour])
        print('Skills:',self.p.skills); print('Inventory:',self.p.inv)
        print('Kills:',self.p.kills,' Crafted:',self.p.crafted,' Regions:',', '.join(self.p.regions) or 'None')
        input('Press Enter...')

    def skill_menu(self):
        print('\n=== SKILL TREE ===')
        print('Every level grants 1 skill point. Current levels:',self.p.skills)
        print('[1] Might    +5 power per rank')
        print('[2] Survival +3 defence per rank')
        print('[3] Insight  +3% critical chance per rank')
        a=input('Spend point (1-3, or Enter to leave): ').strip()
        if a in ('1','2','3'):
            key=['Might','Survival','Insight'][int(a)-1]
            spent=sum(self.p.skills.values())
            if spent < self.p.level-1: self.p.skills[key]+=1; print(key,'increased!')
            else: print('You have no unspent skill points.')

    def craft_menu(self):
        recipes = [
            ('Hardened Blade','weapon',{'Iron Scrap':6,'Ancient Gear':2,'Ash Crystal':2}),
            ('Ranger Bow','weapon',{'Iron Scrap':8,'Ember Root':3,'Ash Crystal':2}),
            ('Storm Rifle','weapon',{'Iron Scrap':12,'Ancient Gear':5,'Void Dust':2}),
            ('Void Carbine','weapon',{'Ancient Gear':10,'Moon Shard':4,'Void Dust':6}),
            ('Ranger Mail','armour',{'Iron Scrap':10,'Ember Root':5}),
            ('Aegis Plate','armour',{'Iron Scrap':15,'Ancient Gear':8,'Ash Crystal':5}),
            ('Void Mantle','armour',{'Moon Shard':6,'Void Dust':10,'Ancient Gear':10}),
        ]
        print('\n=== CRAFTING ===')
        for i,(n,k,cost) in enumerate(recipes,1): print(i,n,'|',', '.join(f'{x} x{y}' for x,y in cost.items()))
        a=input('Recipe number (Enter leaves): ').strip()
        if not a.isdigit() or not 1<=int(a)<=len(recipes): return
        n,k,cost=recipes[int(a)-1]
        if any(self.p.inv.get(x,0)<y for x,y in cost.items()): print('Not enough materials.'); return
        for x,y in cost.items(): self.p.inv[x]-=y
        if k=='weapon':
            if n=='Hardened Blade':
                WEAPONS['Hardened Blade']={'power':22,'speed':3,'crit':7,'value':500,'tag':'crafted'}
            self.p.weapon=n
        else: self.p.armour=n
        self.p.crafted+=1; self.p.gain_xp(180); print('Crafted',n)
        self.progress('craft',k)

    def map_menu(self):
        print('\n=== MAP ===')
        print('Haven       [safe]')
        print('Deadwood    [forests and ruins]')
        print('Salt Flats  [old military roads]')
        print('Blackwater  [flooded industrial zone]')
        print('The Crater  [endgame zone]')
        print('Visited:', ', '.join(self.p.regions) or 'Haven only')

    def rest(self):
        print('You rest behind Haven\'s walls.')
        self.p.hp=self.p.max_hp; self.advance(8); self.random_event() if random.random()<.3 else print('You sleep peacefully.')

    def add_item(self,item,n=1): self.p.inv[item]=self.p.inv.get(item,0)+n

    def progress(self, kind, target, amount=1):
        for q in QUESTS:
            name,desc,k,t,need,reward=q
            if k!=kind or t!=target: continue
            st=self.quests[name]
            if st['done']: continue
            if k=='item': st['progress']=min(need,self.p.inv.get(t,0))
            elif k=='gold': st['progress']=min(need,self.p.gold)
            elif k=='explore': st['progress']=len(self.p.regions)
            else: st['progress']=min(need,st['progress']+amount)
            if st['progress']>=need:
                st['done']=True; self.p.gold+=reward; self.p.gain_xp(reward//2); print(f'QUEST COMPLETE: {name} (+{reward}g)')

    def night_event(self):
        if self.event_cooldown>0 or self.region()=='Haven': return
        self.event_cooldown=3
        print('\nThe ash becomes luminous. Something moves beyond the firelight.')
        if random.random()<.35: self.combat(random.choice(['Ash Witch','Void Hound','Scavenger']))

    def boss(self,name):
        hp,dmg,xp,gold=BOSSES[name]
        hp=int(hp*(1+self.p.level*.08))
        print(f'\n=== BOSS: {name.upper()} ===')
        print('HP:',hp,'Damage:',dmg)
        while hp>0 and self.p.hp>0:
            a=self.choose('Boss phase:', ['Attack','Defend','Medkit','Special action'])
            if a==1:
                dam=self.p.power+random.randint(0,8); hp-=dam; print('You strike for',dam)
            elif a==2: dmg=max(1,dmg//3); print('You brace.')
            elif a==3 and self.p.inv.get('Medkit',0): self.p.inv['Medkit']-=1; self.p.hp=min(self.p.max_hp,self.p.hp+50); print('Recovered 50 HP.')
            else:
                if self.p.skills['Insight']>=2: hp-=self.p.power*2; print('You exploit a weakness!')
                else: print('You have no special action available.')
            if hp>0:
                incoming=max(1,dmg-self.p.defence//2); self.p.hp-=incoming; print(name,'deals',incoming)
        if self.p.hp<=0: print('You were defeated.'); self.p.hp=self.p.max_hp//2; self.flags['region']='Haven'; return
        self.p.gold+=gold; self.p.gain_xp(xp); self.add_item('Moon Shard',2); print('BOSS DEFEATED!')
        self.progress('boss',name)
        if name=='The Warden': self.add_item('Warden Core'); self.flags['warden']=True
        if name=='Mother of Ash': self.flags['mother']=True
        if name=='Hollow King': self.final_choice()

    def final_choice(self):
        self.progress('event','king')
        print('\nThe Hollow King falls. The Dawn Engine wakes beneath the vault.')
        self.say('Hollow King','You can destroy it, rule it, or finish what I started.')
        a=self.choose('The fate of Eldoria is yours.', ['Destroy the Dawn Engine', 'Use it to restore the world', 'Bind it to yourself', 'Walk away'])
        endings=['FREEDOM','RESTORATION','ASCENSION','EXILE']
        self.flags['ending']=endings[a-1]
        self.progress('ending','ending')
        print('\n' + '='*60); print('ENDING:',self.flags['ending']); print('='*60)
        if a==1: print('You destroy the machine. The ash begins to fall normally for the first time in seventy years.')
        elif a==2: print('The sky clears. Eldoria remembers everything it lost, and begins rebuilding.')
        elif a==3: print('You become the new keeper of the Dawn Engine. The world survives, but your humanity changes.')
        else: print('You leave the machine untouched. Eldoria remains dangerous, but its future belongs to ordinary people.')
        print('\nYou completed the main story. You can continue exploring, finish side quests, or quit.')

    def quit(self):
        a=self.choose('Save before quitting?', ['Save and quit','Quit without saving','Cancel'])
        if a==1: self.save(); self.running=False
        elif a==2: self.running=False

if __name__ == '__main__':
    Game().start()
