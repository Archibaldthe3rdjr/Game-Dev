import pygame,random,math,json,os
pygame.init()
W,H=1100,700; screen=pygame.display.set_mode((W,H)); pygame.display.set_caption('ASHFALL: REQUIEM OF THE HOLLOW KING'); clock=pygame.time.Clock()
F=pygame.font.SysFont('consolas',18); S=pygame.font.SysFont('consolas',14); B=pygame.font.SysFont('consolas',38,True); G=pygame.font.SysFont('consolas',58,True)
WHITE=(235,235,235);BLACK=(9,11,15);RED=(215,65,70);GREEN=(70,210,100);BLUE=(70,145,235);GOLD=(235,190,55);PURPLE=(165,80,220);CYAN=(65,205,210);GREY=(145,150,160)
SAVE='ashfall_save.json'; WORLD=(5000,3400)
REG={'Haven':((25,55,70),(0,0,1450,1050)),'Deadwood':((40,70,45),(0,1050,1450,2350)),'Salt Flats':((112,95,62),(1450,0,3350,1100)),'Blackwater':((30,65,80),(1450,1100,3350,2350)),'Crater':((70,38,70),(3350,0,5000,3400))}
WEAPONS={'Rusty Blade':(9,.04,100,1,0),'Iron Sabre':(18,.07,110,1.05,180),'Ranger Bow':(25,.15,430,.82,300),'Storm Rifle':(34,.09,600,1.25,520),'Void Carbine':(48,.16,650,1.35,950),'Sunforged':(65,.22,125,1,1500)}
ARMOR={'Cloth Coat':(2,0,0),'Scrap Vest':(7,15,100),'Ranger Mail':(13,35,350),'Aegis Plate':(23,70,900),'Void Mantle':(32,110,1600)}
EN={'Ash Rat':(55,8,115,16,18),'Scavenger':(95,14,125,21,30),'Mutant':(170,23,145,28,60),'Ravager':(260,32,175,32,100),'Ash Knight':(390,44,215,35,170),'Void Hound':(550,57,250,38,260),'Ash Witch':(440,50,115,31,230),'Crater Spawn':(720,65,180,42,360)}
BOSS={'The Warden':(1500,42,115,62,900),'Mother of Ash':(2300,58,145,82,1600),'Hollow King':(3800,78,165,100,3500)}
QUESTS=[
('A Rat in the Walls','Kill 8 Ash Rats','kills','Ash Rat',8,120,90),('Old Roots','Collect 5 Ember Roots','item','Ember Root',5,180,130),('Missing Scout','Find the scout in Deadwood','point','scout',1,240,180),('Scrap Economy','Collect 10 Iron Scrap','item','Iron Scrap',10,220,150),('Crystal Fever','Collect 5 Ash Crystals','item','Ash Crystal',5,320,220),('Night Watch','Survive a night outside Haven','night','night',1,300,250),('The Old Road','Reach the Salt Flats','region','Salt Flats',1,350,300),('Broken Relay','Repair 3 relay stations','relay','relay',3,420,350),('A Voice Below','Enter a procedural ruin','dungeon','d1',1,500,450),('Blackwater','Reach Blackwater','region','Blackwater',1,450,400),('The Warden','Defeat the Warden','boss','The Warden',1,800,650),('Warden Core','Recover a Warden Core','item','Warden Core',1,900,700),('Three Keys','Find 3 Moon Shards','item','Moon Shard',3,1000,850),('Hollow Gate','Find the gate in the Crater','point','gate',1,900,750),('Mother of Ash','Defeat Mother of Ash','boss','Mother of Ash',1,1500,1200),('Last Archive','Search an ancient archive','dungeon','d2',1,1200,1000),('Better Weapon','Craft an upgraded weapon','craft','weapon',1,700,650),('Better Life','Craft upgraded armour','craft','armor',1,700,650),('The Betrayal','Choose at the Obsidian Shrine','choice','shrine',1,1000,800),('Ashfall','Reach the Hollow King','point','king',1,1800,1500),('The Hollow King','Defeat the Hollow King','boss','Hollow King',1,4000,3500),('Aftermath','Decide the fate of Eldoria','ending','ending',1,0,0)]
class P:
 def __init__(self,d=None):
  z=d or {};self.x=z.get('x',820);self.y=z.get('y',560);self.level=z.get('level',1);self.xp=z.get('xp',0);self.need=z.get('need',120);self.hp=z.get('hp',140);self.maxhp=z.get('maxhp',140);self.st=z.get('st',100);self.gold=z.get('gold',120);self.weapon=z.get('weapon','Rusty Blade');self.armor=z.get('armor','Cloth Coat');self.kills=z.get('kills',0);self.crafted=z.get('crafted',0);self.skills=z.get('skills',{'Might':0,'Survival':0,'Arcane':0});self.inv=z.get('inv',{'Medkit':3,'Bomb':1,'Iron Scrap':3,'Ash Crystal':0,'Ancient Gear':0,'Moon Shard':0,'Ember Root':0,'Void Dust':0,'Warden Core':0})
 def data(self):return self.__dict__
 def xpup(self,n,g):
  self.xp+=n
  while self.xp>=self.need:self.xp-=self.need;self.level+=1;self.need=int(self.need*1.3);self.maxhp+=15;self.hp=self.maxhp;g.msg('LEVEL UP! Press K for skills.',GOLD,3)
 @property
 def dmg(self):return WEAPONS[self.weapon][0]+self.skills['Might']*5+(self.level-1)*2
 @property
 def crit(self):return WEAPONS[self.weapon][1]+self.skills['Might']*.025+self.skills['Arcane']*.015
 @property
 def rng(self):return WEAPONS[self.weapon][2]+self.skills['Arcane']*25
 @property
 def defense(self):return ARMOR[self.armor][0]+self.skills['Survival']*2
class E:
 def __init__(self,n,x,y,g,boss=False,elite=False):
  self.name=n;self.x=x;self.y=y;self.boss=boss;self.elite=elite;self.cd=0;h,d,s,r,xp=(BOSS[n] if boss else EN[n]);q=(1+(g.day-1)*.045+(g.p.level-1)*.035)*(1.55 if elite else 1);self.hp=self.maxhp=int(h*q);self.dam=int(d*q);self.spd=s;self.rad=r;self.xp=int(xp*q);self.gold=max(8,int(xp*.42))
 def update(self,dt,g):
  self.cd=max(0,self.cd-dt);dx=g.p.x-self.x;dy=g.p.y-self.y;d=max(1,math.hypot(dx,dy))
  if d<850:self.x+=dx/d*self.spd*dt;self.y+=dy/d*self.spd*dt
  if d<self.rad+17 and self.cd<=0:g.damage(max(1,self.dam-g.p.defense//3));self.cd=.5 if self.boss else .9
 def draw(self,cx,cy):
  x,y=int(self.x-cx),int(self.y-cy);c=PURPLE if self.boss else GOLD if self.elite else RED;pygame.draw.circle(screen,c,(x,y),self.rad);pygame.draw.circle(screen,BLACK,(x,y),max(4,self.rad//3));pygame.draw.rect(screen,BLACK,(x-self.rad,y-self.rad-10,self.rad*2,5));pygame.draw.rect(screen,GREEN,(x-self.rad,y-self.rad-10,int(self.rad*2*self.hp/self.maxhp),5))
class Game:
 def __init__(self):
  self.p=P();self.day=1;self.hour=8.;self.state='menu';self.region='Haven';self.en=[];self.loot=[];self.npcs=[('Mara',760,550,GOLD),('Dax',1010,420,BLUE),('Sera',1100,650,CYAN),('Rook',1210,520,GOLD),('Finch',620,700,GREEN)];self.msgs=[];self.dialog=None;self.shop=False;self.inv=False;self.skills=False;self.map=False;self.craftui=False;self.drooms=[];self.dp=0;self.relays=[[1750,450,0],[2450,720,0],[2850,1550,0],[3950,850,0]];self.q=[list(x) for x in QUESTS];self.flags={'warden':0,'mother':0,'king':0,'shrine':0,'ending':0};self.play=0;self.spawn()
 def msg(self,t,c=WHITE,d=2):self.msgs.append([t,d,c])
 def reg(self,x,y):
  for n,(_,r) in REG.items():
   if r[0]<=x<r[0]+r[2] and r[1]<=y<r[1]+r[3]:return n
  return 'Wilderness'
 def spawn(self):
  for n,num in [('Ash Rat',28),('Scavenger',22),('Mutant',15),('Ravager',10),('Ash Knight',6),('Void Hound',4),('Ash Witch',4),('Crater Spawn',3)]:
   for _ in range(num):
    x,y=random.randint(150,4850),random.randint(150,3250)
    if self.reg(x,y)=='Haven':x+=900
    self.en.append(E(n,x,y,self,elite=random.random()<.07))
 def cam(self):return max(0,min(WORLD[0]-W,self.p.x-W/2)),max(0,min(WORLD[1]-H,self.p.y-H/2))
 def damage(self,n):
  if getattr(self,'ifr',0)>0:return
  self.p.hp-=n;self.ifr=.35
  if self.p.hp<=0:self.p.hp=self.p.maxhp//2;self.p.x,self.p.y=820,560;self.p.gold=max(0,self.p.gold-80);self.msg('Knocked out. Back to Haven. -80g.',RED,4)
 def progress(self,kind,target,n=1):
  for i,q in enumerate(self.q):
   if q[2]>=q[4] or q[2]!=kind and q[2] in ('kills','item','point','night','region','relay','dungeon','boss','craft','choice','ending'):pass
   if q[2]>=q[4] or q[2]!=kind or q[3]!=target:continue
   q[4]=min(q[4],q[4]+n) if False else q[4]
   # progress is stored in q[7], appended lazily
   if len(q)<8:q.append(0)
   if kind=='item':q[7]=min(q[4],self.p.inv.get(target,0))
   else:q[7]=min(q[4],q[7]+n)
   if q[7]>=q[4]:self.complete(i)
 def complete(self,i):
  q=self.q[i]
  if len(q)<8:q.append(q[4])
  if q[7]>=q[4] and q[6]>=0:q[6]=-1;self.p.gold+=q[5];self.p.xpup(q[6]*-1 if False else q[5]//2,self);self.msg('QUEST COMPLETE: '+q[0]+' +'+str(q[5])+'g',GOLD,4)
 def kill(self,e):
  if e not in self.en:return
  self.en.remove(e);self.p.kills+=1;self.p.gold+=e.gold;self.p.xpup(e.xp,self);self.progress('kills',e.name)
  if random.random()<.45:
   d=random.choice(['Iron Scrap','Ember Root','Ash Crystal','Ancient Gear','Void Dust']);self.loot.append([e.x,e.y,d])
  if e.boss:
   self.progress('boss',e.name)
   if e.name=='The Warden':self.flags['warden']=1;self.p.inv['Warden Core']+=1
   if e.name=='Mother of Ash':self.flags['mother']=1;self.p.inv['Moon Shard']+=2
   if e.name=='Hollow King':self.flags['king']=1;self.start_end()
 def attack(self):
  if getattr(self,'atkcd',0)>0:return
  w=WEAPONS[self.p.weapon];self.atkcd=.2/w[3];cx,cy=self.cam();mx,my=pygame.mouse.get_pos();dx,dy=mx+cx-self.p.x,my+cy-self.p.y;d=max(1,math.hypot(dx,dy));tar=None;best=.72
  for e in self.en:
   ex,ey=e.x-self.p.x,e.y-self.p.y;ed=math.hypot(ex,ey)
   if ed<=self.p.rng and ex*dx+ey*dy>best*ed*d:tar=e;best=(ex*dx+ey*dy)/(ed*d)
  if tar:
   dam=self.p.dmg+random.randint(-4,7)
   if random.random()<self.p.crit:dam*=2;self.msg('CRITICAL!',GOLD)
   tar.hp-=dam
   if tar.hp<=0:self.kill(tar)
 def interact(self):
  for n,x,y,c in self.npcs:
   if math.hypot(self.p.x-x,self.p.y-y)<90:
    if n=='Dax':self.shop=True;return
    if n=='Mara':self.quest_dialog();return
    lines={'Sera':('The Ashfall changed the rules of reality.','Ask about the Ashfall?'),'Rook':('The Crater is not a crater. It is a door.','Ask about the Crater?'),'Finch':('The machines remember their makers.','Ask about the old world?')}
    a,b=lines[n];self.dialog=[n,a,b,['Leave','Ask']];return
  for a in self.loot[:]:
   if math.hypot(a[0]-self.p.x,a[1]-self.p.y)<65:self.p.inv[a[2]]=self.p.inv.get(a[2],0)+1;self.loot.remove(a);self.progress('item',a[2]);self.msg('Picked up '+a[2],GREEN);return
  for r in self.relays:
   if not r[2] and math.hypot(self.p.x-r[0],self.p.y-r[1])<85:
    if self.p.inv.get('Iron Scrap',0)>=2:self.p.inv['Iron Scrap']-=2;r[2]=1;self.progress('relay','relay');self.msg('Relay repaired.',GREEN)
    else:self.msg('Need 2 Iron Scrap.',RED)
    return
  if self.region=='Blackwater' and math.hypot(self.p.x-3000,self.p.y-1600)<200:self.boss('The Warden',3000,1600)
  elif self.region=='Crater' and self.flags['warden'] and math.hypot(self.p.x-4100,self.p.y-2100)<240:self.boss('Mother of Ash',4100,2100)
  elif self.region=='Crater' and self.flags['mother'] and math.hypot(self.p.x-4450,self.p.y-700)<250:self.boss('Hollow King',4450,700)
  elif self.region=='Crater' and math.hypot(self.p.x-3700,self.p.y-2750)<180:self.shrine()
  elif self.region in ('Deadwood','Blackwater','Crater') and random.random()<.12:self.dungeon()
 def boss(self,n,x,y):
  if not any(e.boss and e.name==n for e in self.en):self.en.append(E(n,x,y,self,boss=True));self.msg(n.upper()+' AWAKENS.',RED,5)
 def quest_dialog(self):
  for i,q in enumerate(self.q):
   if len(q)<8:q.append(0)
   if q[6]>=0:self.dialog=['MARA',q[0],q[1],[f'Accept quest','Leave'],i];return
  self.dialog=['MARA','You have done all I can ask.','The end is near.',['Leave']]
 def choose(self,n):
  if not self.dialog:return
  if self.dialog[0]=='MARA':self.dialog=None;return
  text=self.dialog[1]
  if n==1:self.dialog=[self.dialog[0],'You have chosen to listen.','Knowledge changes what comes next.',['Leave']]
  else:self.dialog=None
 def shrine(self):self.dialog=['OBSIDIAN SHRINE','A voice offers three futures.','This choice changes the final ending.',['Free the Ash','Bind the Ash','Destroy it']];self.choice='shrine'
 def choice(self,n):self.flags['shrine']=n+1;self.progress('choice','shrine');self.dialog=None;self.msg(['The chains crack.','The chains tighten.','The shrine burns.'][n],GOLD,4)
 def dungeon(self):
  self.drooms=[];x=y=0;seen={(0,0)}
  for _ in range(120):
   dx,dy=random.choice([(1,0),(-1,0),(0,1),(0,-1)]);nx,ny=x+dx,y+dy
   if -5<nx<6 and -4<ny<5:x,y=nx,ny;seen.add((x,y))
  self.drooms=list(seen);self.dp=0;self.state='dungeon';self.msg('A procedural ruin unfolds beneath you.',PURPLE,4);self.progress('dungeon','d1')
 def craft(self,kind):
  rec={'weapon':('Void Carbine',{'Iron Scrap':12,'Ash Crystal':6,'Ancient Gear':4,'Void Dust':2}),'armor':('Void Mantle',{'Iron Scrap':15,'Ash Crystal':8,'Moon Shard':2,'Void Dust':4})}[kind];n,need=rec
  if all(self.p.inv.get(k,0)>=v for k,v in need.items()):
   for k,v in need.items():self.p.inv[k]-=v
   if kind=='weapon':self.p.weapon=n
   else:self.p.armor=n
   self.p.crafted+=1;self.progress('craft',kind);self.msg('CRAFTED '+n+'!',GOLD,4)
  else:self.msg('Missing materials.',RED)
 def update(self,dt):
  if self.state not in ('playing','dungeon'):return
  self.play+=dt;self.atkcd=max(0,getattr(self,'atkcd',0)-dt);self.ifr=max(0,getattr(self,'ifr',0)-dt)
  if self.state=='dungeon':return
  self.hour+=dt/18
  if self.hour>=24:self.hour-=24;self.day+=1;self.progress('night','night')
  k=pygame.key.get_pressed();dx=int(k[pygame.K_d])-int(k[pygame.K_a]);dy=int(k[pygame.K_s])-int(k[pygame.K_w]);m=math.hypot(dx,dy);sp=340 if k[pygame.K_LSHIFT] and self.p.st>0 else 225
  if m:self.p.x+=dx/m*sp*dt;self.p.y+=dy/m*sp*dt;self.p.st=max(0,self.p.st-(40*dt if sp>300 else 0))
  else:self.p.st=min(100,self.p.st+28*dt)
  self.p.x=max(25,min(WORLD[0]-25,self.p.x));self.p.y=max(25,min(WORLD[1]-25,self.p.y));old=self.region;self.region=self.reg(self.p.x,self.p.y)
  if old!=self.region:self.msg('Entered '+self.region,CYAN,3);self.progress('region',self.region)
  for e in self.en[:]:e.update(dt,self)
  if len(self.en)<100 and random.random()<dt*.28:self.en.append(E(random.choice(list(EN)),random.randint(100,4900),random.randint(100,3300),self,elite=random.random()<.06))
  for m in self.msgs:m[1]-=dt
  self.msgs=[m for m in self.msgs if m[1]>0]
 def panel(self,t,x,y,w,h):pygame.draw.rect(screen,(20,23,29),(x,y,w,h));pygame.draw.rect(screen,(90,95,105),(x,y,w,h),2);screen.blit(B.render(t,1,WHITE),(x+20,y+15))
 def hud(self):
  p=self.p;pygame.draw.rect(screen,BLACK,(10,10,360,105));pygame.draw.rect(screen,RED,(25,30,240,18));pygame.draw.rect(screen,GREEN,(25,30,int(240*p.hp/p.maxhp),18));pygame.draw.rect(screen,BLUE,(25,55,int(240*p.xp/max(1,p.need)),10));screen.blit(S.render(f'HP {p.hp}/{p.maxhp}  LV {p.level}  XP {p.xp}/{p.need}',1,WHITE),(25,72));screen.blit(S.render(f'{self.region} | Day {self.day} | {int(self.hour):02d}:00 | {p.gold}g',1,WHITE),(390,18));screen.blit(S.render(f'{p.weapon} {p.dmg}DMG | {p.armor} {p.defense}DEF',1,WHITE),(390,42));screen.blit(S.render('WASD move | Shift sprint | Mouse attack | E interact | Q heal | K skills | I inventory | M map | C craft | F5/F9 save/load',1,WHITE),(390,68));y=H-80
  for t,d,c in self.msgs[-3:]:a=F.render(t,1,c);screen.blit(a,(W//2-a.get_width()//2,y));y-=26
 def worlddraw(self):
  cx,cy=self.cam();screen.fill(BLACK);tile=80
  for x in range(0,WORLD[0],tile):
   for y in range(0,WORLD[1],tile):
    r=self.reg(x+40,y+40);c=REG.get(r,((50,50,50),))[0];v=4 if (x//tile+y//tile)%2 else 0;pygame.draw.rect(screen,tuple(min(255,a+v) for a in c),(x-cx,y-cy,tile,tile))
  for x,y,d in self.relays:pygame.draw.rect(screen,GREEN if d else GOLD,(x-cx-12,y-cy-12,24,24))
  for e in self.en:e.draw(cx,cy)
  for x,y,n in self.loot:pygame.draw.rect(screen,GOLD,(x-cx-6,y-cy-6,12,12))
  for n,x,y,c in self.npcs:pygame.draw.circle(screen,c,(int(x-cx),int(y-cy)),18);screen.blit(S.render(n,1,WHITE),(x-cx-25,y-cy-38))
  pygame.draw.circle(screen,BLUE,(int(self.p.x-cx),int(self.p.y-cy)),17);self.hud()
 def overlay(self):
  if self.inv:
   self.panel('INVENTORY',120,65,860,570);y=130
   for n,v in self.p.inv.items():
    if not n.startswith('_'):screen.blit(F.render(f'{n:<20} x{v}',1,WHITE),(160,y));y+=29
  if self.skills:
   self.panel('SKILL TREE',130,70,840,560);screen.blit(F.render('Spend points earned from levels: 1/2/3',1,GOLD),(170,135));ds=['+5 damage / crit','+2 defence / stamina','+25 range / crit'];ns=['Might','Survival','Arcane']
   for i,n in enumerate(ns):y=200+i*105;screen.blit(F.render(f'[{i+1}] {n}  LEVEL {self.p.skills[n]}',1,WHITE),(180,y));screen.blit(S.render(ds[i],1,GREY),(180,y+35))
  if self.map:
   self.panel('MAP',100,60,900,570)
   for n,(c,r) in REG.items():pygame.draw.rect(screen,c,(150+r[0]/7,145+r[1]/8,r[2]/7,r[3]/8));screen.blit(S.render(n,1,WHITE),(155+r[0]/7,150+r[1]/8))
  if self.craftui:
   self.panel('CRAFTING',180,100,740,500);screen.blit(F.render('[1] Void Carbine: 12 Scrap, 6 Crystal, 4 Gear, 2 Dust',1,WHITE),(230,200));screen.blit(F.render('[2] Void Mantle: 15 Scrap, 8 Crystal, 2 Shard, 4 Dust',1,WHITE),(230,270))
  if self.shop:
   self.panel('DAX SHOP',180,80,740,530);ns=list(WEAPONS)+list(ARMOR)
   for i,n in enumerate(ns):pr=WEAPONS[n][4] if n in WEAPONS else ARMOR[n][2];screen.blit(F.render(f'[{i+1}] {n:<18} {pr}g',1,WHITE),(230+(i%2)*330,150+(i//2)*65))
  if self.dialog:
   self.panel(self.dialog[0],70,475,960,175);screen.blit(F.render(self.dialog[1],1,WHITE),(100,530));screen.blit(S.render(self.dialog[2],1,GREY),(100,560));
   for i,o in enumerate(self.dialog[3]):screen.blit(F.render(f'[{i+1}] {o}',1,GOLD),(100+i*280,600))
 def dungeon_draw(self):
  screen.fill((12,12,18));screen.blit(B.render('PROCEDURAL RUIN',1,PURPLE),(350,30));size=55;ox=525;oy=350
  for x,y in self.drooms:pygame.draw.rect(screen,(65,65,78),(ox+x*size,oy+y*size,size-4,size-4))
  if self.drooms:x,y=self.drooms[self.dp];pygame.draw.rect(screen,GOLD,(ox+x*size+10,oy+y*size+10,30,30))
  screen.blit(F.render('WASD: move between rooms | E: search | ESC: leave',1,WHITE),(300,640))
 def menu(self):
  screen.fill((7,9,13));screen.blit(G.render('ASHFALL',1,WHITE),(350,90));screen.blit(B.render('REQUIEM OF THE HOLLOW KING',1,GOLD),(230,170));ls=['22 QUESTS • PROCEDURAL DUNGEONS • SKILL TREE','CRAFTING • WEAPON STATS • RANDOM EVENTS • CHOICES','THREE ENDINGS • SAVE/LOAD • LONG-FORM STORY','','ENTER New Game','L Load Game','ESC Quit']
  for i,t in enumerate(ls):screen.blit(F.render(t,1,WHITE if i<3 else GREY),(290,250+i*42))
 def ending(self):
  screen.fill(BLACK);screen.blit(G.render('THE HOLLOW KING IS FALLEN',1,GOLD),(220,110));screen.blit(B.render('Choose Eldoria’s future',1,WHITE),(330,210));
  for i,t in enumerate(['Free the Ash and rebuild','Bind the Ash and rule','Destroy the Ash forever']):screen.blit(B.render(f'{i+1}. {t}',1,WHITE),(200,310+i*90))
 def victory(self):
  n=['THE NEW DAWN','THE IRON AGE','THE SILENT WORLD'][self.flags['ending']-1];screen.fill(BLACK);screen.blit(G.render(n,1,GOLD),(300,120));screen.blit(B.render('ELDORIA HAS A NEW FUTURE',1,WHITE),(250,220));screen.blit(F.render(f'Level {self.p.level} | Kills {self.p.kills} | Gold {self.p.gold} | Days {self.day} | Playtime {self.play/3600:.1f}h',1,GREY),(280,330));screen.blit(F.render('F5 save | ESC quit',1,WHITE),(450,420))
 def save(self):
  with open(SAVE,'w') as f:json.dump({'p':self.p.data(),'day':self.day,'hour':self.hour,'q':self.q,'flags':self.flags,'relays':self.relays,'play':self.play},f)
  self.msg('GAME SAVED',GREEN,3)
 def load(self):
  if not os.path.exists(SAVE):self.msg('No save file.',RED);return
  with open(SAVE) as f:d=json.load(f)
  self.p=P(d['p']);self.day=d['day'];self.hour=d['hour'];self.q=d['q'];self.flags=d['flags'];self.relays=d['relays'];self.play=d.get('play',0);self.state='playing';self.msg('SAVE LOADED',GREEN,3)
 def buy(self,i):
  ns=list(WEAPONS)+list(ARMOR)
  if i>=len(ns):return
  n=ns[i];pr=WEAPONS[n][4] if n in WEAPONS else ARMOR[n][2]
  if self.p.gold<pr:self.msg('Not enough gold.',RED);return
  self.p.gold-=pr
  if n in WEAPONS:self.p.weapon=n
  else:self.p.armor=n
  self.msg('Equipped '+n,GREEN)
 def events(self):
  for e in pygame.event.get():
   if e.type==pygame.QUIT:self.running=False
   if e.type==pygame.KEYDOWN:
    if self.state=='menu':
     if e.key==pygame.K_RETURN:self.state='playing';self.msg('Mara is waiting in Haven.',CYAN,4)
     elif e.key==pygame.K_l:self.load()
     elif e.key==pygame.K_ESCAPE:self.running=False
     continue
    if self.state=='ending':
     if e.key in (pygame.K_1,pygame.K_2,pygame.K_3):self.flags['ending']=e.key-pygame.K_0;self.state='victory';self.progress('ending','ending');self.msg('ENDING REACHED',GOLD,8)
     continue
    if self.state=='victory':
     if e.key==pygame.K_F5:self.save()
     elif e.key==pygame.K_ESCAPE:self.running=False
     continue
    if self.state=='dungeon':
     if e.key==pygame.K_ESCAPE:self.state='playing';continue
     if e.key in (pygame.K_w,pygame.K_a,pygame.K_s,pygame.K_d):
      x,y=self.drooms[self.dp];dx=int(e.key==pygame.K_d)-int(e.key==pygame.K_a);dy=int(e.key==pygame.K_s)-int(e.key==pygame.K_w);z=(x+dx,y+dy)
      if z in self.drooms:self.dp=self.drooms.index(z)
     if e.key==pygame.K_e:
      if random.random()<.5:self.p.inv['Ancient Gear']+=1;self.p.xpup(150,self);self.msg('Ancient Gear found.',GOLD)
      else:self.en.append(E(random.choice(list(EN)),self.p.x,self.p.y,self));self.msg('AMBUSH!',RED)
     continue
    if self.dialog:
     if e.key in (pygame.K_1,pygame.K_2,pygame.K_3):
      n=e.key-pygame.K_1
      if getattr(self,'choice',None)=='shrine':self.choice(n);self.choice=None
      else:self.choose(n)
     elif e.key==pygame.K_ESCAPE:self.dialog=None
     continue
    if self.shop:
     if pygame.K_1<=e.key<=pygame.K_9:self.buy(e.key-pygame.K_1)
     elif e.key==pygame.K_ESCAPE:self.shop=False
     continue
    if self.inv:
     if e.key in (pygame.K_i,pygame.K_ESCAPE):self.inv=False
     continue
    if self.skills:
     if e.key in (pygame.K_1,pygame.K_2,pygame.K_3):
      n=['Might','Survival','Arcane'][e.key-pygame.K_1]
      if sum(self.p.skills.values())<self.p.level-1:self.p.skills[n]+=1;self.msg(n+' upgraded.',GREEN)
     elif e.key in (pygame.K_k,pygame.K_ESCAPE):self.skills=False
     continue
    if self.map:
     if e.key in (pygame.K_m,pygame.K_ESCAPE):self.map=False
     continue
    if self.craftui:
     if e.key==pygame.K_1:self.craft('weapon')
     elif e.key==pygame.K_2:self.craft('armor')
     elif e.key in (pygame.K_c,pygame.K_ESCAPE):self.craftui=False
     continue
    if e.key==pygame.K_ESCAPE:self.state='paused' if self.state=='playing' else 'playing'
    elif e.key==pygame.K_F5:self.save()
    elif e.key==pygame.K_F9:self.load()
    elif e.key==pygame.K_i:self.inv=True
    elif e.key==pygame.K_k:self.skills=True
    elif e.key==pygame.K_m:self.map=True
    elif e.key==pygame.K_c:self.craftui=True
    elif e.key==pygame.K_e:self.interact()
    elif e.key==pygame.K_q and self.p.inv.get('Medkit',0):self.p.inv['Medkit']-=1;self.p.hp=min(self.p.maxhp,self.p.hp+70);self.msg('Medkit used.',GREEN)
   if e.type==pygame.MOUSEBUTTONDOWN and e.button==1 and self.state=='playing' and not(self.dialog or self.shop or self.inv or self.skills or self.map or self.craftui):self.attack()
 def draw(self):
  if self.state=='menu':self.menu();return
  if self.state=='ending':self.ending();return
  if self.state=='victory':self.victory();return
  if self.state=='dungeon':self.dungeon_draw();return
  self.worlddraw();self.overlay()
  if self.state=='paused':pygame.draw.rect(screen,(0,0,0,190),(0,0,W,H));screen.blit(G.render('PAUSED',1,WHITE),(420,260))
GAME=Game();GAME.running=True
while GAME.running:
 dt=min(.05,clock.tick(60)/1000);GAME.events();GAME.update(dt);GAME.draw();pygame.display.flip()
pygame.quit()
