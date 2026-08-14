import pygame, random, math, json, os
pygame.init(); W,H=1100,700; S=pygame.display.set_mode((W,H)); pygame.display.set_caption('ASHFALL: THE LAST OUTPOST'); C=pygame.time.Clock()
F=pygame.font.SysFont('consolas',18); SM=pygame.font.SysFont('consolas',14); B=pygame.font.SysFont('consolas',38,1); G=pygame.font.SysFont('consolas',58,1)
WHITE=(235,235,235); BLACK=(10,12,16); RED=(220,65,70); GREEN=(70,210,100); BLUE=(65,145,235); GOLD=(235,190,55); PURPLE=(165,80,220); CYAN=(60,205,210)
SAVE='ashfall_save.json'; random.seed()
ITEMS={'Rusty Blade':('weapon',8,25),'Iron Sabre':('weapon',20,160),'Storm Rifle':('weapon',32,420),'Sunforged':('weapon',50,950),'Cloth Coat':('armor',3,30),'Scrap Vest':('armor',7,90),'Ranger Mail':('armor',14,280),'Aegis Plate':('armor',24,750),'Medkit':('heal',40,25),'Strong Medkit':('heal',90,85),'Bomb':('bomb',70,65),'Ash Crystal':('mat',0,100),'Ancient Gear':('mat',0,160),'Moon Shard':('mat',0,350)}
EN={'Ash Rat':(50,8,100,18,20),'Scavenger':(90,14,125,22,35),'Mutant':(160,22,150,27,65),'Ravager':(250,31,180,31,110),'Ash Knight':(370,43,220,34,180),'Void Hound':(520,55,250,37,260)}
BOSSES={'The Warden':(1300,38,120,65,900),'Mother of Ash':(1900,54,145,78,1600),'Hollow King':(3000,70,165,95,3200)}
REG=[('Haven',(50,65,75)),('Deadwood',(43,72,48)),('Salt Flats',(112,98,64)),('Blackwater',(35,70,82)),('Crater',(76,43,70))]
class Player:
 def __init__(self,d=None):
  z=d or {}; self.x=z.get('x',850); self.y=z.get('y',550); self.hp=z.get('hp',120); self.maxhp=z.get('maxhp',120); self.st=z.get('st',100); self.lvl=z.get('lvl',1); self.xp=z.get('xp',0); self.need=z.get('need',100); self.gold=z.get('gold',100); self.weapon=z.get('weapon','Rusty Blade'); self.armor=z.get('armor','Cloth Coat'); self.inv=z.get('inv',{'Medkit':3,'Bomb':1,'Ash Crystal':0,'Ancient Gear':0,'Moon Shard':0}); self.kills=z.get('kills',0); self.cd=0; self.hurt=0
 def data(self): return self.__dict__
 @property
 def dmg(self): return ITEMS[self.weapon][1]+(self.lvl-1)*2
 @property
 def defense(self): return ITEMS[self.armor][1]+self.lvl//3
 def xpup(self,n,game):
  self.xp+=n
  while self.xp>=self.need:
   self.xp-=self.need; self.lvl+=1; self.need=int(self.need*1.27)+15; self.maxhp+=14; self.hp=self.maxhp; game.msg('LEVEL UP! Level '+str(self.lvl),GOLD,3)
 def hit(self,n,game):
  if self.hurt:return
  n=max(1,n-self.defense//3); self.hp-=n; self.hurt=.35
  if self.hp<=0:self.hp=self.maxhp//2; self.x,self.y=850,550; self.gold=max(0,self.gold-50); game.msg('You woke up in Haven. -50 gold.',RED,3)
class Enemy:
 def __init__(self,name,x,y,scale=1,boss=False,elite=False):
  self.name=name; self.x=x; self.y=y; self.boss=boss; self.elite=elite; self.cd=0
  hp,dam,spd,rad,xp=(BOSSES[name] if boss else EN[name]); scale*=1+(GAME.day-1)*.05+(GAME.p.lvl-1)*.035
  if elite:scale*=1.6
  self.hp=self.maxhp=int(hp*scale); self.dam=int(dam*scale); self.spd=spd; self.rad=rad; self.xp=int(xp*scale); self.gold=max(8,int(xp*.4))
 def update(self,dt):
  p=GAME.p; dx=p.x-self.x; dy=p.y-self.y; d=max(1,math.hypot(dx,dy)); self.cd=max(0,self.cd-dt)
  if d<620:self.x+=dx/d*self.spd*dt; self.y+=dy/d*self.spd*dt
  if d<self.rad+16 and self.cd<=0:p.hit(self.dam,GAME); self.cd=.55 if self.boss else .9
 def draw(self,cx,cy):
  x,y=int(self.x-cx),int(self.y-cy); col=PURPLE if self.boss else (GOLD if self.elite else RED); pygame.draw.circle(S,col,(x,y),self.rad); pygame.draw.circle(S,BLACK,(x,y),max(3,self.rad//3)); w=self.rad*2; pygame.draw.rect(S,BLACK,(x-w//2,y-self.rad-10,w,5)); pygame.draw.rect(S,GREEN,(x-w//2,y-self.rad-10,int(w*self.hp/self.maxhp),5))
class Game:
 def __init__(self):
  self.world=(3600,2600); self.p=Player(); self.en=[]; self.loot=[]; self.npcs=[('Mara',760,550,GOLD),('Dax',1000,420,BLUE),('Sera',1100,650,CYAN),('Rook',1210,520,GOLD),('Finch',620,700,GREEN)]; self.day=1; self.hour=8.; self.region='Haven'; self.state='menu'; self.inv=False; self.map=False; self.shop=False; self.dialog=None; self.toast=[]; self.flags={'warden':False,'mother':False,'king':False}; self.q=[['Rat Problem',8,0,120,90],['Crystal Harvest',5,0,250,170],['Ancient Machinery',3,0,400,280],['The Warden',1,0,700,550],['Mother of Ash',1,0,1200,1000],['Hollow King',1,0,2500,2200]]; self.play=0; self.spawn()
 def spawn(self):
  self.en=[]
  for name,count in [('Ash Rat',22),('Scavenger',17),('Mutant',12),('Ravager',8),('Ash Knight',4)]:
   for _ in range(count):self.en.append(Enemy(name,random.randint(250,3450),random.randint(200,2350),elite=random.random()<.08))
 def msg(self,t,c=WHITE,d=2):self.toast.append([t,d,c])
 def reg(self,x,y):
  if x<1450 and y<1000:return 'Haven'
  if x<1450:return 'Deadwood'
  if x>=1450 and y<1150:return 'Salt Flats'
  if x<2300:return 'Blackwater'
  return 'Crater'
 def camera(self):return max(0,min(self.world[0]-W,self.p.x-W/2)),max(0,min(self.world[1]-H,self.p.y-H/2))
 def quest(self,i,n=1):
  q=self.q[i]; q[2]=min(q[1],q[2]+n)
  if q[2]>=q[1] and q[1]>0:
   self.p.gold+=q[3]; self.p.xpup(q[4],self); self.msg('QUEST COMPLETE: '+q[0]+'  +'+str(q[3])+'g',GOLD,4); q[1]=0
 def kill(self,e):
  if e not in self.en:return
  self.en.remove(e); self.p.kills+=1; self.p.gold+=e.gold; self.p.xpup(e.xp,self)
  if e.name=='Ash Rat':self.quest(0)
  if random.random()<.22:self.loot.append([e.x,e.y,random.choice(['Medkit','Ash Crystal','Ancient Gear','Bomb'])])
  if e.boss:
   self.p.inv['Moon Shard']=self.p.inv.get('Moon Shard',0)+2
   self.p.inv['Ancient Gear']=self.p.inv.get('Ancient Gear',0)+2
   idx={'The Warden':3,'Mother of Ash':4,'Hollow King':5}[e.name]; self.quest(idx)
   if e.name=='Hollow King':self.state='victory'; self.msg('THE ASHFALL IS BROKEN.',GOLD,6)
 def attack(self):
  if self.p.cd>0:return
  self.p.cd=.22 if 'Rifle' in self.p.weapon else .36; cx,cy=self.camera(); mx,my=pygame.mouse.get_pos(); tx,ty=mx+cx,my+cy; dx,dy=tx-self.p.x,ty-self.p.y; d=max(1,math.hypot(dx,dy)); reach=540 if 'Rifle' in self.p.weapon or 'Bow' in self.p.weapon else 230
  target=None; best=1
  for e in self.en:
   ex,ey=e.x-self.p.x,e.y-self.p.y; ed=math.hypot(ex,ey)
   if ed<reach:
    dot=(ex*dx+ey*dy)/(max(1,ed)*d)
    if dot>.72 and dot>best:target=e;best=dot
    elif dot>.82 and target is None:target=e
  if target:
   dmg=self.p.dmg+random.randint(-3,6)
   if random.random()<.1:dmg*=2
   target.hp-=dmg
   if target.hp<=0:self.kill(target)
 def interact(self):
  p=self.p
  for name,x,y,c in self.npcs:
   if math.hypot(p.x-x,p.y-y)<80:
    if name=='Dax':self.shop=True;return
    if name=='Sera':
     if p.gold>=15:p.gold-=15;p.hp=p.maxhp;self.msg('Sera healed you for 15g.',GREEN)
     else:self.msg('Sera needs 15 gold.',RED);return
    if name=='Mara':
     for i,q in enumerate(self.q):
      if q[1]>0:self.dialog=['Mara',q[0],['Kill 8 rats in Deadwood.','Find 5 Ash Crystals.','Find 3 Ancient Gears.','Go to Blackwater and face the Warden.','Enter the Crater and find Mother of Ash.','The final vault awaits.'][i]];return
    if name=='Rook':self.dialog=['Rook','The Crater is where the sky broke.','If the glowing things notice you, run.'];return
    self.dialog=['Finch','Before the Ashfall, people built machines that could think.','Now we mostly use rusty knives.'];return
  for a in self.loot[:]:
   if math.hypot(a[0]-p.x,a[1]-p.y)<55:
    p.inv[a[2]]=p.inv.get(a[2],0)+1;self.loot.remove(a);self.msg('Picked up '+a[2],GREEN);return
  r=self.region
  if r=='Blackwater' and not self.flags['warden'] and math.hypot(p.x-2800,p.y-600)<180:self.flags['warden']=True;self.en.append(Enemy('The Warden',2800,600,1,True));self.msg('THE WARDEN AWAKENS.',RED,5)
  elif r=='Crater' and self.flags['warden'] and not self.flags['mother'] and math.hypot(p.x-3150,p.y-1800)<220:self.flags['mother']=True;self.en.append(Enemy('Mother of Ash',3150,1800,1,True));self.msg('MOTHER OF ASH RISES.',RED,5)
  elif r=='Crater' and self.flags['mother'] and not self.flags['king'] and math.hypot(p.x-1900,p.y-1800)<220:self.flags['king']=True;self.en.append(Enemy('Hollow King',1900,1800,1,True));self.msg('THE HOLLOW KING HAS RETURNED.',PURPLE,5)
 def buy(self,i):
  names=['Strong Medkit','Iron Sabre','Scrap Vest','Storm Rifle','Sunforged'];name=names[i];kind,powr,price=ITEMS[name]
  if self.p.gold<price:self.msg('Not enough gold.',RED);return
  self.p.gold-=price
  if kind=='weapon':self.p.weapon=name
  elif kind=='armor':self.p.armor=name
  else:self.p.inv[name]=self.p.inv.get(name,0)+1
  self.msg('Bought '+name,GREEN)
 def update(self,dt):
  if self.state!='playing':return
  self.play+=dt;self.hour+=dt/18
  if self.hour>=24:self.hour-=24;self.day+=1
  p=self.p; k=pygame.key.get_pressed(); dx=k[pygame.K_d]-k[pygame.K_a];dy=k[pygame.K_s]-k[pygame.K_w];m=math.hypot(dx,dy);spd=350 if k[pygame.K_LSHIFT] and p.st>0 else 225
  if m:p.x+=dx/m*spd*dt;p.y+=dy/m*spd*dt;p.st=max(0,p.st-(35*dt if spd>300 else 0))
  else:p.st=min(100,p.st+25*dt)
  p.x=max(25,min(self.world[0]-25,p.x));p.y=max(25,min(self.world[1]-25,p.y));p.cd=max(0,p.cd-dt);p.hurt=max(0,p.hurt-dt)
  old=self.region;self.region=self.reg(p.x,p.y)
  if old!=self.region:self.msg('Entered '+self.region,CYAN)
  for e in self.en[:]:e.update(dt)
  if len(self.en)<48 and random.random()<dt*.35:self.en.append(Enemy(random.choice(list(EN)),random.randint(100,3500),random.randint(100,2500)))
  for t in self.toast:t[1]-=dt
  self.toast=[t for t in self.toast if t[1]>0]
 def draw(self):
  if self.state=='menu':self.menu();return
  if self.state=='victory':self.victory();return
  cx,cy=self.camera();S.fill((22,24,28));tile=80
  for x in range(0,self.world[0],tile):
   for y in range(0,self.world[1],tile):
    r=self.reg(x+40,y+40);col=dict(REG)[r];z=5 if (x//tile+y//tile)%2 else 0;pygame.draw.rect(S,tuple(v+z for v in col),(x-cx,y-cy,tile,tile))
  pygame.draw.rect(S,(95,82,65),(0-cx,950-cy,self.world[0],100));pygame.draw.rect(S,(95,82,65),(1380-cx,0-cy,100,self.world[1]))
  pygame.draw.circle(S,(45,23,48),(3150-int(cx),1800-int(cy)),310,9);pygame.draw.circle(S,(18,15,24),(3150-int(cx),1800-int(cy)),175)
  for e in self.en:e.draw(cx,cy)
  for name,x,y,c in self.npcs:pygame.draw.circle(S,c,(int(x-cx),int(y-cy)),18);S.blit(SM.render(name,1,WHITE),(x-cx-25,y-cy-38))
  for x,y,n in self.loot:pygame.draw.rect(S,GOLD,(x-cx-7,y-cy-7,14,14))
  pygame.draw.circle(S,BLUE,(int(self.p.x-cx),int(self.p.y-cy)),16);pygame.draw.circle(S,WHITE,(int(self.p.x-cx),int(self.p.y-cy)),5)
  self.hud()
  if self.inv:self.inventory()
  if self.map:self.mapui()
  if self.dialog:self.dialogui()
  if self.shop:self.shopui()
  if self.state=='paused':pygame.draw.rect(S,(0,0,0,190),(0,0,W,H));S.blit(G.render('PAUSED',1,WHITE),(430,180))
 def hud(self):
  p=self.p;pygame.draw.rect(S,BLACK,(12,12,340,90));pygame.draw.rect(S,RED,(25,30,240,18));pygame.draw.rect(S,GREEN,(25,30,int(240*p.hp/p.maxhp),18));pygame.draw.rect(S,(35,55,70),(25,55,240,10));pygame.draw.rect(S,BLUE,(25,55,int(240*p.xp/max(1,p.need)),10));S.blit(SM.render(f'HP {p.hp}/{p.maxhp}  LV {p.lvl}  XP {p.xp}/{p.need}',1,WHITE),(25,72));S.blit(SM.render(f'{self.region} | Day {self.day} | {int(self.hour):02d}:00 | {p.gold}g',1,WHITE),(370,18));S.blit(SM.render(f'{p.weapon}  DMG {p.dmg} | {p.armor}  DEF {p.defense}',1,WHITE),(370,42));S.blit(SM.render('WASD move | Shift sprint | Mouse attack | E interact | Q heal | TAB inventory | M map | F5 save | F9 load | ESC pause',1,WHITE),(370,66))
  y=H-70
  for t in self.toast[-3:]:a=F.render(t[0],1,t[2]);S.blit(a,(W//2-a.get_width()//2,y));y-=27
 def panel(self,title,x,y,w,h):pygame.draw.rect(S,(25,28,34),(x,y,w,h));pygame.draw.rect(S,(90,95,105),(x,y,w,h),2);S.blit(B.render(title,1,WHITE),(x+25,y+18))
 def inventory(self):
  self.panel('INVENTORY',100,65,900,570);y=125;S.blit(F.render(f'Weapon: {self.p.weapon} | Armor: {self.p.armor} | Gold: {self.p.gold}',1,GOLD),(130,y));y+=45
  for n,c in self.p.inv.items():S.blit(F.render(f'{n:<18} x{c}',1,WHITE),(140,y));y+=30
  S.blit(SM.render('TAB closes. Q uses a Medkit.',1,(180,185,195)),(140,590))
 def mapui(self):
  self.panel('ASH WASTES',120,80,860,540);names=['Haven','Deadwood','Salt Flats','Blackwater','Crater']
  for i,n in enumerate(names):x=170+(i%3)*250;y=190+(i//3)*150;pygame.draw.rect(S,dict(REG)[n],(x,y,190,100));S.blit(F.render(n,1,WHITE),(x+50,y+38))
  S.blit(F.render('Current: '+self.region+'   |   M closes',1,GOLD),(160,555))
 def dialogui(self):
  pygame.draw.rect(S,(10,12,15),(70,510,960,140));S.blit(F.render(self.dialog[0],1,GOLD),(95,530));S.blit(F.render(self.dialog[1],1,WHITE),(95,565));S.blit(F.render(self.dialog[2],1,WHITE),(95,595));S.blit(SM.render('E closes',1,(180,185,195)),(900,620))
 def shopui(self):
  self.panel("DAX'S SHOP",210,90,680,500);names=['Strong Medkit','Iron Sabre','Scrap Vest','Storm Rifle','Sunforged'];y=170
  for i,n in enumerate(names):S.blit(F.render(f'[{i+1}] {n:<18} {ITEMS[n][2]}g',1,WHITE),(260,y));y+=60
  S.blit(SM.render('Number buys | ESC closes',1,(180,185,195)),(260,545))
 def menu(self):
  S.fill((10,12,16));S.blit(G.render('ASHFALL',1,WHITE),(380,100));S.blit(B.render('THE LAST OUTPOST',1,GOLD),(355,175));
  for i,t in enumerate(['A single-file open-world survival RPG.','Five regions. Dozens of enemies. Three bosses.','Quests, gear, loot, shops, levels, saves and a final vault.','','ENTER  New Game','L  Load Save','ESC  Quit']):S.blit(F.render(t,1,(185,190,200)),(300,260+i*42))
 def victory(self):
  S.fill((7,9,13));S.blit(G.render('THE ASH STOPS',1,GOLD),(315,130));S.blit(B.render('You defeated the Hollow King.',1,WHITE),(300,240));S.blit(F.render(f'Days: {self.day}   Level: {self.p.lvl}   Kills: {self.p.kills}   Gold: {self.p.gold}',1,(185,190,200)),(300,310));S.blit(F.render('F5 saves the victory. ESC quits.',1,WHITE),(350,400))
 def save(self):
  with open(SAVE,'w') as f:json.dump({'p':self.p.data(),'q':self.q,'flags':self.flags,'day':self.day,'hour':self.hour,'play':self.play},f);self.msg('Game saved.',GREEN)
 def load(self):
  if not os.path.exists(SAVE):self.msg('No save file.',RED);return
  try:
   with open(SAVE) as f:d=json.load(f)
   self.p=Player(d['p']);self.q=d['q'];self.flags=d['flags'];self.day=d['day'];self.hour=d['hour'];self.play=d['play'];self.state='playing';self.msg('Save loaded.',GREEN)
  except Exception as e:self.msg('Load failed: '+str(e),RED,3)
 def events(self):
  for e in pygame.event.get():
   if e.type==pygame.QUIT:self.running=False
   if e.type==pygame.KEYDOWN:
    if self.state=='menu':
     if e.key==pygame.K_RETURN:self.state='playing';self.msg('Welcome to Haven. Start by talking to Mara.',CYAN,4)
     elif e.key==pygame.K_l:self.load()
     elif e.key==pygame.K_ESCAPE:self.running=False
     continue
    if self.state=='victory':
     if e.key==pygame.K_F5:self.save()
     elif e.key==pygame.K_ESCAPE:self.running=False
     continue
    if e.key==pygame.K_ESCAPE:
     if self.dialog:self.dialog=None
     elif self.shop:self.shop=False
     elif self.inv:self.inv=False
     elif self.map:self.map=False
     else:self.state='paused' if self.state=='playing' else 'playing'
    elif e.key==pygame.K_F5:self.save()
    elif e.key==pygame.K_F9:self.load()
    elif e.key==pygame.K_TAB:self.inv=not self.inv
    elif e.key==pygame.K_m:self.map=not self.map
    elif e.key==pygame.K_e:
     if self.dialog:self.dialog=None
     elif not self.inv and not self.map and not self.shop:self.interact()
    elif e.key==pygame.K_q and self.p.inv.get('Medkit',0):self.p.inv['Medkit']-=1;self.p.hp=min(self.p.maxhp,self.p.hp+ITEMS['Medkit'][1]);self.msg('Medkit used.',GREEN)
    elif self.shop and pygame.K_1<=e.key<=pygame.K_5:self.buy(e.key-pygame.K_1)
   if e.type==pygame.MOUSEBUTTONDOWN and e.button==1 and self.state=='playing' and not(self.inv or self.map or self.shop or self.dialog):self.attack()
GAME=Game();GAME.running=True
while GAME.running:
 dt=min(.05,C.tick(60)/1000);GAME.events();GAME.update(dt);GAME.draw();pygame.display.flip()
pygame.quit()
