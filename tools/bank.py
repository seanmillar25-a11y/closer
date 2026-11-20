"""Closer question bank: events + daily rounds.

Run:  python3 tools/bank.py
Writes public/puzzles.js (what the game loads) and data/events.csv + data/rounds.csv,
and checks every round (order, no ties, answer stable for the next few years).
"""
import csv, json, os, sys

W = "https://en.wikipedia.org/wiki/"
NOW = "now"  # "Today" uses the player's current year

# id: (tag, name, year, approx, reach, source, check)
#   reach: global | well-known | regional (regional = not for daily puzzles)
#   check: "verified" = looked up against sources for this bank; "documented" = standard, well-documented date
EV = {
 "today":      ("The present", "Today", NOW, False, "global", "", "n/a"),
 # --- Deep time & prehistory
 "sharks":     ("Prehistory", "The first sharks", -420_000_000, True, "global", "https://www.elasmo-research.org/education/evolution/earliest.htm", "verified"),
 "trees":      ("Prehistory", "The first trees", -385_000_000, True, "global", W+"Wattieza", "documented"),
 "firstdinos": ("Prehistory", "The first dinosaurs", -230_000_000, True, "global", W+"Dinosaur", "documented"),
 "stego":      ("Prehistory", "Stegosaurus roams", -150_000_000, True, "global", W+"Stegosaurus", "documented"),
 "flowers":    ("Prehistory", "The first flowering plants", -130_000_000, True, "global", W+"Flowering_plant", "documented"),
 "trex":       ("Prehistory", "T. rex roams", -67_000_000, True, "global", W+"Tyrannosaurus", "documented"),
 "asteroid":   ("Prehistory", "The asteroid ends the dinosaurs", -66_000_000, True, "global", W+"Cretaceous%E2%80%93Paleogene_extinction_event", "documented"),
 "apes":       ("Prehistory", "The first apes", -25_000_000, True, "global", W+"Ape", "documented"),
 "sapiens":    ("Prehistory", "Homo sapiens appear", -298_000, True, "global", W+"Homo_sapiens", "documented"),
 "neander":    ("Prehistory", "The Neanderthals die out", -38_000, True, "global", W+"Neanderthal", "documented"),
 "lascaux":    ("Prehistory", "The Lascaux cave paintings", -15_000, True, "global", W+"Lascaux", "documented"),
 "iceage":     ("Prehistory", "The last Ice Age ends", -9_700, True, "global", W+"Holocene", "documented"),
 "mammoths":   ("Prehistory", "The last woolly mammoths", -2_000, True, "global", "https://www.nationalgeographic.com/science/article/woolly-mammoth-last-extinction-genetics", "verified"),
 # --- Ancient world
 "writing":    ("Invention", "Writing is invented", -3_200, True, "global", W+"History_of_writing", "documented"),
 "pyramid":    ("Ancient Egypt", "The Great Pyramid is built", -2_560, True, "global", W+"Great_Pyramid_of_Giza", "documented"),
 "stonehenge": ("Prehistory", "Stonehenge's great stones are raised", -2_500, True, "global", W+"Stonehenge", "documented"),
 "tut":        ("Ancient Egypt", "Tutankhamun dies", -1_323, True, "global", W+"Tutankhamun", "documented"),
 "olympia":    ("Ancient Greece", "The first Olympic Games", -776, False, "global", W+"Ancient_Olympic_Games", "documented"),
 "rome":       ("Rome", "Rome is founded (by legend)", -753, False, "global", W+"Founding_of_Rome", "documented"),
 "iliad":      ("Literature", "Homer's Iliad is written down", -750, True, "global", W+"Iliad", "documented"),
 "qin":        ("China", "China's First Emperor unites China", -221, False, "global", W+"Qin_Shi_Huang", "documented"),
 "caesar":     ("Rome", "Julius Caesar is assassinated", -44, False, "global", W+"Assassination_of_Julius_Caesar", "documented"),
 "cleopatra":  ("Ancient Egypt", "Cleopatra dies", -30, False, "global", W+"Cleopatra", "documented"),
 "vending":    ("Invention", "The first vending machine", 50, True, "global", W+"Vending_machine", "documented"),
 "pompeii":    ("Rome", "Vesuvius buries Pompeii", 79, False, "global", W+"Pompeii", "documented"),
 "hadrian":    ("Rome", "Hadrian's Wall is begun", 122, False, "well-known", W+"Hadrian%27s_Wall", "documented"),
 "romefall":   ("Rome", "The Western Roman Empire falls", 476, False, "global", W+"Fall_of_the_Western_Roman_Empire", "documented"),
 # --- Medieval & early modern
 "vinland":    ("Vikings", "Vikings reach North America", 1_000, True, "global", W+"Vinland", "documented"),
 "hastings":   ("England", "The Battle of Hastings", 1_066, False, "well-known", W+"Battle_of_Hastings", "documented"),
 "oxford":     ("Education", "Teaching begins at Oxford", 1_096, False, "global", W+"University_of_Oxford", "documented"),
 "cambridge":  ("Education", "Cambridge University is founded", 1_209, False, "global", W+"University_of_Cambridge", "documented"),
 "magna":      ("Law", "Magna Carta is sealed", 1_215, False, "global", W+"Magna_Carta", "documented"),
 "aztecs":     ("The Americas", "The Aztecs found Tenochtitlan", 1_325, False, "global", W+"Tenochtitlan", "documented"),
 "machu":      ("The Americas", "Machu Picchu is built", 1_450, True, "global", W+"Machu_Picchu", "documented"),
 "constant":   ("Empires", "Constantinople falls", 1_453, False, "global", W+"Fall_of_Constantinople", "documented"),
 "gutenberg":  ("Invention", "The Gutenberg Bible is printed", 1_455, True, "global", W+"Gutenberg_Bible", "verified"),
 "columbus":   ("Exploration", "Columbus reaches the Americas", 1_492, False, "global", W+"Voyages_of_Christopher_Columbus", "documented"),
 "ming":       ("China", "Most of today's Great Wall is built", 1_500, True, "global", W+"Great_Wall_of_China", "documented"),
 "monalisa":   ("Art", "Leonardo begins the Mona Lisa", 1_503, True, "global", W+"Mona_Lisa", "documented"),
 "sistine":    ("Art", "The Sistine Chapel ceiling is finished", 1_512, False, "global", W+"Sistine_Chapel_ceiling", "documented"),
 "armada":     ("War", "The Spanish Armada", 1_588, False, "global", W+"Spanish_Armada", "documented"),
 "quixote":    ("Literature", "Don Quixote is published", 1_605, False, "global", W+"Don_Quixote", "documented"),
 "galileo":    ("Science", "Galileo's telescope", 1_609, False, "global", W+"Galileo_Galilei", "documented"),
 "shakes":     ("Literature", "Shakespeare dies", 1_616, False, "global", W+"William_Shakespeare", "documented"),
 "mayflower":  ("Exploration", "The Mayflower lands", 1_620, False, "global", W+"Mayflower", "documented"),
 "harvard":    ("Education", "Harvard is founded", 1_636, False, "global", W+"Harvard_University", "documented"),
 "taj":        ("Architecture", "The Taj Mahal is completed", 1_653, True, "global", W+"Taj_Mahal", "verified"),
 "dodo":       ("Nature", "The last confirmed dodo sighting", 1_662, False, "global", W+"Dodo", "documented"),
 "fire":       ("London", "The Great Fire of London", 1_666, False, "well-known", W+"Great_Fire_of_London", "documented"),
 "principia":  ("Science", "Newton's Principia is published", 1_687, False, "global", W+"Philosophi%C3%A6_Naturalis_Principia_Mathematica", "documented"),
 # --- 18th–19th century
 "mozart":     ("Music", "Mozart is born", 1_756, False, "global", W+"Wolfgang_Amadeus_Mozart", "documented"),
 "decl":       ("America", "The Declaration of Independence", 1_776, False, "global", W+"United_States_Declaration_of_Independence", "documented"),
 "locomotive": ("Invention", "The first steam locomotive", 1_804, False, "global", W+"Richard_Trevithick", "documented"),
 "tincan":     ("Invention", "The tin can is patented", 1_810, False, "global", W+"Tin_can", "documented"),
 "waterloo":   ("War", "The Battle of Waterloo", 1_815, False, "global", W+"Battle_of_Waterloo", "documented"),
 "bicycle":    ("Invention", "The first bicycle", 1_817, False, "global", W+"Dandy_horse", "documented"),
 "antarctica": ("Exploration", "Antarctica is first sighted", 1_820, False, "global", W+"History_of_Antarctica", "documented"),
 "lighter":    ("Invention", "The first lighter", 1_823, False, "global", W+"D%C3%B6bereiner%27s_lamp", "documented"),
 "ninth":      ("Music", "Beethoven's Ninth Symphony premieres", 1_824, False, "global", W+"Symphony_No._9_(Beethoven)", "documented"),
 "match":      ("Invention", "The friction match", 1_826, False, "global", W+"Match", "documented"),
 "photo":      ("Invention", "The first photograph", 1_826, True, "global", W+"View_from_the_Window_at_Le_Gras", "documented"),
 "victoria":   ("Monarchy", "Queen Victoria is crowned", 1_838, False, "global", W+"Coronation_of_Queen_Victoria", "documented"),
 "fax":        ("Invention", "The fax machine is patented", 1_843, False, "global", W+"Alexander_Bain_(inventor)", "documented"),
 "chocolate":  ("Food & drink", "The first chocolate bar", 1_847, False, "global", W+"J._S._Fry_%26_Sons", "documented"),
 "canopener":  ("Invention", "The can opener is invented", 1_858, False, "global", W+"Can_opener", "documented"),
 "bigben":     ("London", "Big Ben first chimes", 1_859, False, "global", W+"Big_Ben", "documented"),
 "darwin":     ("Science", "Darwin's Origin of Species", 1_859, False, "global", W+"On_the_Origin_of_Species", "documented"),
 "civilwar":   ("War", "The American Civil War begins", 1_861, False, "global", W+"American_Civil_War", "documented"),
 "football":   ("Sport", "Football's first official rules", 1_863, False, "global", W+"History_of_association_football", "documented"),
 "tube":       ("London", "The London Underground opens", 1_863, False, "global", W+"London_Underground", "documented"),
 "civilend":   ("War", "The American Civil War ends", 1_865, False, "global", W+"American_Civil_War", "documented"),
 "phone":      ("Invention", "The telephone is patented", 1_876, False, "global", W+"Invention_of_the_telephone", "documented"),
 "samurai":    ("Japan", "The last samurai uprising", 1_877, False, "global", W+"Satsuma_Rebellion", "documented"),
 "wimbledon":  ("Sport", "The first Wimbledon", 1_877, False, "global", W+"1877_Wimbledon_Championship", "documented"),
 "testcricket":("Sport", "The first Test cricket match", 1_877, False, "well-known", W+"Test_cricket", "documented"),
 "bulb":       ("Invention", "Edison's light bulb", 1_879, False, "global", W+"Incandescent_light_bulb", "documented"),
 "coke":       ("Food & drink", "Coca-Cola is invented", 1_886, False, "global", W+"Coca-Cola", "documented"),
 "liberty":    ("America", "The Statue of Liberty is unveiled", 1_886, False, "global", W+"Statue_of_Liberty", "documented"),
 "sherlock":   ("Literature", "Sherlock Holmes first appears", 1_887, False, "global", W+"A_Study_in_Scarlet", "documented"),
 "nintendo":   ("Games", "Nintendo is founded", 1_889, False, "global", W+"Nintendo", "documented"),
 "eiffel":     ("Paris", "The Eiffel Tower opens", 1_889, False, "global", W+"Eiffel_Tower", "documented"),
 "starry":     ("Art", "Van Gogh paints The Starry Night", 1_889, False, "global", W+"The_Starry_Night", "documented"),
 "basketball": ("Sport", "Basketball is invented", 1_891, False, "global", W+"Basketball", "documented"),
 "nzvote":     ("Democracy", "Women first vote in a national election", 1_893, False, "global", W+"Women%27s_suffrage_in_New_Zealand", "documented"),
 "cinema":     ("Film", "The first public film screening", 1_895, False, "global", W+"Workers_Leaving_the_Lumi%C3%A8re_Factory", "documented"),
 "olympics":   ("Sport", "The first modern Olympics", 1_896, False, "global", W+"1896_Summer_Olympics", "documented"),
 "speeding":   ("Motoring", "The first speeding ticket", 1_896, False, "global", W+"Arnold_(automobile)", "verified"),
 # --- 20th century
 "tour":       ("Sport", "The first Tour de France", 1_903, False, "global", W+"1903_Tour_de_France", "documented"),
 "wright":     ("Flight", "The Wright brothers fly", 1_903, False, "global", W+"Wright_Flyer", "documented"),
 "modelt":     ("Motoring", "The Ford Model T", 1_908, False, "global", W+"Ford_Model_T", "documented"),
 "titanic":    ("Disaster", "The Titanic sinks", 1_912, False, "global", W+"Titanic", "documented"),
 "ww1":        ("War", "The First World War begins", 1_914, False, "global", W+"World_War_I", "documented"),
 "ottoman":    ("Empires", "The Ottoman Empire ends", 1_922, False, "global", W+"Ottoman_Empire", "documented"),
 "tv":         ("Invention", "Television is first demonstrated", 1_926, False, "global", W+"John_Logie_Baird", "documented"),
 "jazzsinger": ("Film", "The first feature-length 'talkie'", 1_927, False, "global", W+"The_Jazz_Singer", "documented"),
 "penicillin": ("Science", "Penicillin is discovered", 1_928, False, "global", W+"History_of_penicillin", "documented"),
 "mickey":     ("Film", "Mickey Mouse first appears", 1_928, False, "global", W+"Steamboat_Willie", "documented"),
 "bread":      ("Food & drink", "Sliced bread goes on sale", 1_928, False, "global", W+"Sliced_bread", "documented"),
 "oscars":     ("Film", "The first Academy Awards", 1_929, False, "global", W+"1st_Academy_Awards", "documented"),
 "pluto":      ("Space", "Pluto is discovered", 1_930, False, "global", W+"Pluto", "documented"),
 "worldcup":   ("Sport", "The first football World Cup", 1_930, False, "global", W+"1930_FIFA_World_Cup", "documented"),
 "owens":      ("Sport", "Jesse Owens wins four Olympic golds", 1_936, False, "global", W+"Jesse_Owens", "documented"),
 "snowwhite":  ("Film", "Snow White, the first animated feature film", 1_937, False, "global", W+"Snow_White_and_the_Seven_Dwarfs_(1937_film)", "documented"),
 "hobbit":     ("Literature", "The Hobbit is published", 1_937, False, "global", W+"The_Hobbit", "documented"),
 "guernica":   ("Art", "Picasso paints Guernica", 1_937, False, "global", W+"Guernica_(Picasso)", "documented"),
 "ww2end":     ("War", "The Second World War ends", 1_945, False, "global", W+"World_War_II", "documented"),
 "f1":         ("Sport", "The first Formula One world championship", 1_950, False, "global", W+"1950_Formula_One_season", "documented"),
 "mile":       ("Sport", "The first four-minute mile", 1_954, False, "global", W+"Four-minute_mile", "documented"),
 "eurovision": ("Music", "The first Eurovision Song Contest", 1_956, False, "global", W+"Eurovision_Song_Contest_1956", "documented"),
 "bubble":     ("Invention", "Bubble wrap is invented", 1_957, False, "global", W+"Bubble_wrap", "verified"),
 "paralympics":("Sport", "The first Paralympic Games", 1_960, False, "global", W+"1960_Summer_Paralympics", "documented"),
 "wallup":     ("Cold War", "The Berlin Wall goes up", 1_961, False, "global", W+"Berlin_Wall", "documented"),
 "beatles":    ("Music", "The Beatles release their first album", 1_963, False, "global", W+"Please_Please_Me", "documented"),
 "superbowl":  ("Sport", "The first Super Bowl", 1_967, False, "global", W+"Super_Bowl_I", "documented"),
 "moon":       ("Space", "The Moon landing", 1_969, False, "global", W+"Apollo_11", "documented"),
 "woodstock":  ("Music", "Woodstock", 1_969, False, "global", W+"Woodstock", "documented"),
 "email":      ("Technology", "The first email is sent", 1_971, False, "global", W+"History_of_email", "documented"),
 "mobile":     ("Technology", "The first mobile phone call", 1_973, False, "global", W+"Martin_Cooper_(inventor)", "documented"),
 "operahouse": ("Architecture", "The Sydney Opera House opens", 1_973, False, "global", W+"Sydney_Opera_House", "documented"),
 "starwars":   ("Film", "Star Wars is released", 1_977, False, "global", W+"Star_Wars_(film)", "documented"),
 "pacman":     ("Games", "Pac-Man is released", 1_980, False, "global", W+"Pac-Man", "documented"),
 "mtv":        ("Music", "MTV goes on air", 1_981, False, "global", W+"MTV", "documented"),
 "tetris":     ("Games", "Tetris is created", 1_984, False, "global", W+"Tetris", "documented"),
 "mario":      ("Games", "Super Mario Bros. is released", 1_985, False, "global", W+"Super_Mario_Bros.", "documented"),
 "liveaid":    ("Music", "Live Aid", 1_985, False, "global", W+"Live_Aid", "documented"),
 "wallfalls":  ("Cold War", "The Berlin Wall falls", 1_989, False, "global", W+"Berlin_Wall", "documented"),
 "www":        ("Technology", "The World Wide Web is invented", 1_989, False, "global", W+"World_Wide_Web", "documented"),
 "sms":        ("Technology", "The first text message", 1_992, False, "global", W+"SMS", "documented"),
 "chunnel":    ("Engineering", "The Channel Tunnel opens", 1_994, False, "global", W+"Channel_Tunnel", "documented"),
 "dolly":      ("Science", "Dolly the sheep is born", 1_996, False, "global", W+"Dolly_(sheep)", "documented"),
 "gta":        ("Games", "Grand Theft Auto is released", 1_997, False, "global", W+"Grand_Theft_Auto_(video_game)", "documented"),
 "potter":     ("Literature", "The first Harry Potter book", 1_997, False, "global", W+"Harry_Potter_and_the_Philosopher%27s_Stone", "documented"),
 "google":     ("Technology", "Google is founded", 1_998, False, "global", W+"Google", "documented"),
 "wikipedia":  ("Technology", "Wikipedia launches", 2_001, False, "global", W+"Wikipedia", "documented"),
 "euro":       ("Europe", "Euro notes and coins arrive", 2_002, False, "global", W+"Euro_banknotes", "documented"),
 "youtube":    ("Technology", "YouTube launches", 2_005, False, "global", W+"YouTube", "documented"),
 "plutodemote":("Space", "Pluto loses planet status", 2_006, False, "global", W+"Pluto", "documented"),
 "iphone":     ("Technology", "The first iPhone", 2_007, False, "global", W+"IPhone_(1st_generation)", "documented"),
 "bolt":       ("Sport", "Usain Bolt runs 100m in 9.58 seconds", 2_009, False, "global", W+"Usain_Bolt", "documented"),
 # --- Regional: kept for special editions, NOT used in daily puzzles
 "kenneth":    ("Scotland", "Kenneth MacAlpin becomes king", 843, True, "regional", W+"Kenneth_MacAlpin", "documented"),
 "lindisfarne":("Vikings", "Vikings raid Lindisfarne", 793, False, "regional", W+"Lindisfarne", "documented"),
 "arbroath":   ("Scotland", "The Declaration of Arbroath", 1_320, False, "regional", W+"Declaration_of_Arbroath", "documented"),
 "standrews":  ("Scotland", "St Andrews University is founded", 1_413, False, "regional", W+"University_of_St_Andrews", "documented"),
 "glasgow":    ("Scotland", "Glasgow University is founded", 1_451, False, "regional", W+"University_of_Glasgow", "documented"),
 "whisky":     ("Scotland", "Scotch whisky is first recorded", 1_494, False, "regional", W+"Scotch_whisky", "documented"),
 "aberdeen":   ("Scotland", "Aberdeen University is founded", 1_495, False, "regional", W+"University_of_Aberdeen", "documented"),
 "edinuni":    ("Scotland", "Edinburgh University is founded", 1_583, False, "regional", W+"University_of_Edinburgh", "documented"),
 "crowns":     ("Scotland", "The Union of the Crowns", 1_603, False, "regional", W+"Union_of_the_Crowns", "documented"),
 "union":      ("Scotland", "The Acts of Union", 1_707, False, "regional", W+"Acts_of_Union_1707", "documented"),
 "dettingen":  ("Monarchy", "The last British king leads troops in battle", 1_743, False, "regional", W+"Battle_of_Dettingen", "documented"),
 "newtown":    ("Scotland", "Edinburgh's New Town is begun", 1_767, False, "regional", W+"New_Town,_Edinburgh", "documented"),
 "discovery":  ("Dundee", "RRS Discovery is launched", 1_901, False, "regional", W+"RRS_Discovery", "documented"),
 "beano":      ("Dundee", "The Beano is first published", 1_938, False, "regional", W+"The_Beano", "documented"),
 "nhs":        ("Britain", "The NHS is founded", 1_948, False, "regional", W+"National_Health_Service", "documented"),
 "abertay":    ("Dundee", "Abertay becomes a university", 1_994, False, "regional", W+"Abertay_University", "documented"),
 "scotparl":   ("Scotland", "The Scottish Parliament reopens", 1_999, False, "regional", W+"Scottish_Parliament", "documented"),
}

# Each day: 5 rounds (L, M, R, fact). Easier start, close call to finish.
DAYS = [
 [ # 1
  ("pyramid","cleopatra","moon","Cleopatra lived about 2,500 years after the Great Pyramid was built, but only about 2,000 years before Apollo 11. To her, the pyramids were already ancient."),
  ("pyramid","mammoths","cleopatra","Woolly mammoths survived on Wrangel Island in the Arctic until about 4,000 years ago. They were still alive while the Great Pyramid was being built."),
  ("stego","trex","today","About 80 million years separate Stegosaurus and T. rex. That's more time than separates T. rex from you."),
  ("fax","civilwar","email","Alexander Bain, a Scottish clockmaker, patented a way of sending images by wire in 1843. The fax is older than the telephone."),
  ("oxford","aztecs","columbus","The Aztec capital, on the site of today's Mexico City, was founded only 167 years before Columbus arrived. Teaching at Oxford had begun more than two centuries earlier."),
 ],
 [ # 2
  ("sharks","trees","trex","Sharks are older than trees. The oldest undisputed shark scales are about 420 million years old, while the first trees appeared around 385 million years ago."),
  ("quixote","sherlock","potter","Sherlock Holmes first appeared in 1887, created by Edinburgh-born Arthur Conan Doyle. He's closer in time to Harry Potter than to Don Quixote."),
  ("samurai","nintendo","mario","Nintendo started out making hand-made playing cards, just 12 years after Japan's last samurai rebellion."),
  ("wallup","tetris","wallfalls","Tetris was created in Moscow in 1984, five years before the Berlin Wall fell."),
  ("olympics","worldcup","superbowl","A close one. The first football World Cup, held in Uruguay in 1930, came 34 years after the first modern Olympics and 37 years before the first Super Bowl."),
 ],
 [ # 3
  ("hadrian","machu","today","Machu Picchu looks ancient, but the Inca built it around 1450. That's closer to today than to the building of Hadrian's Wall."),
  ("ww1","pluto","plutodemote","Pluto was officially a planet for 76 years, from its discovery in 1930 to its reclassification in 2006."),
  ("moon","gta","iphone","The original Grand Theft Auto was made in Dundee by DMA Design and released in 1997, ten years before the first iPhone."),
  ("wright","mile","today","Roger Bannister ran the first mile in under four minutes in 1954, only 51 years after the Wright brothers first flew."),
  ("pyramid","olympia","today","The first recorded Olympics, in 776 BC, were closer in time to the Great Pyramid than to us. Ancient history covers a lot of time."),
 ],
 [ # 4
  ("shakes","harvard","principia","Harvard was founded just 20 years after Shakespeare died, and 51 years before Newton set out his laws of motion."),
  ("waterloo","bigben","phone","Big Ben first rang out in 1859, just 17 years before Edinburgh-born Alexander Graham Bell patented the telephone."),
  ("armada","dodo","decl","The dodo was gone more than a century before the United States existed."),
  ("monalisa","taj","ninth","The Taj Mahal was finished around 1653, about 150 years after Leonardo began the Mona Lisa and roughly 170 years before Beethoven's Ninth Symphony was first performed."),
  ("civilend","coke","wright","A close one: Coca-Cola came 21 years after the American Civil War ended and 17 years before the Wright brothers flew."),
 ],
 [ # 5
  ("cleopatra","oxford","today","Teaching at Oxford began in 1096. Oxford University is closer in time to you than it is to Cleopatra."),
  ("darwin","bulb","modelt","Edison's practical light bulb arrived 20 years after Darwin's big book and 29 years before the Model T."),
  ("firstdinos","trex","today","Dinosaurs ruled for so long that T. rex is far closer to us than to the first dinosaurs."),
  ("columbus","mayflower","decl","The Mayflower landed 128 years after Columbus and 156 years before US independence."),
  ("starry","mickey","starwars","Mickey Mouse made his debut in Steamboat Willie in 1928, 39 years after Van Gogh painted The Starry Night and 49 years before Star Wars."),
 ],
 [ # 6
  ("iliad","pompeii","today","Pompeii was buried by Vesuvius in AD 79, roughly 800 years after Homer's Iliad is thought to have been written down."),
  ("pyramid","vending","today","Hero of Alexandria designed a coin-operated holy water dispenser in the 1st century AD. The vending machine is closer to the pyramids than you might think, but still closer to you."),
  ("vinland","magna","columbus","Leif Erikson's Vikings landed in Newfoundland around the year 1000. Magna Carta came about 215 years later, and Columbus about 490."),
  ("oscars","beatles","today","The Beatles released their first album, Please Please Me, in 1963, only 34 years after the first Academy Awards."),
  ("starwars","youtube","today","A close call: YouTube launched in 2005, 28 years after Star Wars first hit cinemas."),
 ],
 [ # 7
  ("lighter","match","victoria","Johann Döbereiner's lighter, the 'Döbereiner's lamp', came in 1823. That's three years before John Walker invented the friction match."),
  ("tincan","canopener","phone","For almost 50 years people opened tin cans with hammers and chisels. The dedicated can opener didn't appear until 1858."),
  ("titanic","tv","moon","John Logie Baird, from Helensburgh in Scotland, gave the first public demonstration of television in 1926."),
  ("olympics","superbowl","today","The first Super Bowl was played in January 1967, 71 years after the first modern Olympics in Athens."),
  ("moon","dolly","today","A close call: Dolly, cloned at the Roslin Institute near Edinburgh, was born in 1996, 27 years after the Moon landing."),
 ],
 [ # 8
  ("stego","flowers","trex","Stegosaurus probably never saw a flower. Flowering plants appeared later, and T. rex lived among them."),
  ("iceage","pyramid","today","The Great Pyramid is closer in time to you than to the end of the last Ice Age."),
  ("writing","pyramid","cleopatra","The Great Pyramid was built about 640 years after writing first appeared in Mesopotamia, and about 2,500 years before Cleopatra."),
  ("sapiens","neander","today","Our species shared the planet with Neanderthals for well over 200,000 years before they disappeared, roughly 40,000 years ago."),
  ("asteroid","apes","today","The first apes appeared around 25 million years ago. That's much closer to us than to the asteroid that ended the dinosaurs."),
 ],
 [ # 9
  ("oxford","cambridge","columbus","Cambridge was founded in 1209, traditionally by scholars who left Oxford after a dispute with the townspeople."),
  ("gutenberg","galileo","mozart","Galileo first turned a telescope to the sky in 1609, about 154 years after the Gutenberg Bible was printed and 147 years before Mozart was born."),
  ("football","basketball","worldcup","Basketball was invented in 1891 by James Naismith, a Canadian teacher in Massachusetts, 28 years after football's first official rules were agreed in London."),
  ("shakes","principia","darwin","Newton's Principia appeared 71 years after Shakespeare died, and 172 years before Darwin's Origin of Species."),
  ("moon","www","iphone","A close one: Tim Berners-Lee proposed the World Wide Web in 1989, 20 years after the Moon landing and 18 years before the iPhone."),
 ],
 [ # 10
  ("civilend","liberty","ww1","The Statue of Liberty was unveiled in New York in 1886, a gift from the people of France."),
  ("eiffel","tour","titanic","The first Tour de France was raced in 1903, 14 years after the Eiffel Tower opened and nine years before the Titanic sank."),
  ("tetris","bolt","today","Usain Bolt ran 100 metres in 9.58 seconds at the 2009 World Championships in Berlin, the city where the Wall had fallen 20 years earlier."),
  ("email","google","today","A close call: Google was founded in 1998, 27 years after the first email was sent."),
  ("ww2end","moon","chunnel","The closest call of the day: the Moon landing came 24 years after the Second World War ended and 25 years before the Channel Tunnel opened."),
 ],
 [ # 11
  ("qin","hadrian","ming","Hadrian's Wall was begun in AD 122, about 340 years after China's First Emperor unified the country. Most of the Great Wall you can visit today came much later, under the Ming dynasty."),
  ("caesar","constant","today","The Roman Empire survived in the east until the Ottomans took Constantinople in 1453. That end is closer to today than to Julius Caesar's assassination."),
  ("darwin","ottoman","today","The Ottoman Empire, founded around 1300, lasted until 1922. Its end is closer to Darwin's Origin of Species than to today."),
  ("romefall","vinland","columbus","Leif Erikson's Vikings reached North America around the year 1000, slightly closer to Columbus than to the fall of the Western Roman Empire in 476."),
  ("pyramid","tut","cleopatra","Very close: Tutankhamun is about 1,240 years after the Great Pyramid and about 1,290 years before Cleopatra. Ancient Egypt lasted a very long time."),
 ],
 [ # 12
  ("decl","photo","moon","Nicéphore Niépce took the oldest surviving camera photograph, a view from a window in France, around 1826 or 1827."),
  ("columbus","antarctica","moon","Nobody had seen Antarctica until 1820. That's closer to the Moon landing than to Columbus."),
  ("titanic","eurovision","liveaid","The first Eurovision Song Contest was held in Switzerland in 1956, with just seven countries taking part."),
  ("ww2end","mobile","iphone","Motorola's Martin Cooper made the first handheld mobile phone call in 1973, closer to the end of the Second World War than to the iPhone."),
  ("waterloo","speeding","moon","In January 1896 Walter Arnold was fined for driving at 8mph in Kent, four times the speed limit, in what is often called the first speeding ticket. A policeman on a bicycle caught him."),
 ],
 [ # 13
  ("iceage","stonehenge","cleopatra","Stonehenge's big sarsen stones went up around 2500 BC, about the same time as the Great Pyramid, and far later than the end of the Ice Age."),
  ("lascaux","iceage","today","The last Ice Age ended around 9700 BC, closer in time to the Lascaux cave paintings than to today."),
  ("pyramid","pompeii","today","Pompeii was destroyed in AD 79, more than 2,600 years after the Great Pyramid was built."),
  ("tut","rome","cleopatra","Rome's traditional founding date of 753 BC is closer to Tutankhamun than to Cleopatra, who met Julius Caesar."),
  ("writing","olympia","today","A close one: the first recorded Olympics, in 776 BC, came about 2,400 years after writing was invented in Mesopotamia."),
 ],
 [ # 14
  ("magna","sistine","today","Michelangelo finished painting the Sistine Chapel ceiling in 1512, closer to Magna Carta than to today."),
  ("hastings","mozart","today","Mozart was born in 1756, nearly 700 years after the Battle of Hastings."),
  ("decl","chocolate","moon","Fry's of Bristol made the first moulded chocolate bar in 1847. Before that, chocolate was mostly a drink."),
  ("waterloo","tube","moon","The world's first underground railway opened in London in 1863, with steam trains running through the tunnels."),
  ("vinland","taj","today","The Taj Mahal, finished around 1653, is closer to today than to the Vikings' arrival in North America around the year 1000."),
 ],
 [ # 15
  ("shakes","samurai","moon","Samurai were still fighting in 1877, closer in time to the Moon landing than to Shakespeare."),
  ("decl","nzvote","today","New Zealand became the first country to give women the vote in national elections, in 1893."),
  ("titanic","bubble","moon","Bubble wrap was invented in 1957 by Alfred Fielding and Marc Chavannes, who were trying to make textured wallpaper. It didn't catch on as wallpaper."),
  ("moon","sms","today","The first text message, 'Merry Christmas', was sent in December 1992, 23 years after the Moon landing."),
  ("moon","wikipedia","today","Wikipedia launched in January 2001, 32 years after the Moon landing."),
 ],
]

def yr(eid, year_now):
    y = EV[eid][2]
    return year_now if y == NOW else y

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    problems, rows = [], []
    used = set()
    for d, day in enumerate(DAYS, 1):
        if len(day) != 5: problems.append(f"day {d}: {len(day)} rounds")
        for r, (L, M, R, fact) in enumerate(day, 1):
            for e in (L, M, R):
                if e not in EV: problems.append(f"day {d} round {r}: unknown event {e}"); continue
                if EV[e][4] == "regional": problems.append(f"day {d} round {r}: regional event {e}")
                used.add(e)
            answers = set()
            for y in range(2026, 2031):
                l, m, rr = yr(L, y), yr(M, y), yr(R, y)
                if not (l < m < rr): problems.append(f"day {d} round {r}: not in order"); break
                gl, gr = m - l, rr - m
                if gl == gr: problems.append(f"day {d} round {r}: tie in {y}")
                answers.add("L" if gl < gr else "R")
            if len(answers) > 1: problems.append(f"day {d} round {r}: answer changes 2026-2030")
            if "years before today" in fact or "years ago" in fact and "today" in fact:
                problems.append(f"day {d} round {r}: fact mentions years before today")
            l, m, rr = yr(L, 2026), yr(M, 2026), yr(R, 2026)
            gl, gr = m - l, rr - m
            rows.append(dict(day=d, round=r, left=EV[L][1], middle=EV[M][1], right=EV[R][1],
                             answer="Left" if gl < gr else "Right", gap_left=gl, gap_right=gr,
                             closeness=round(min(gl, gr) / max(gl, gr), 2), fact=fact))
    if problems:
        print("PROBLEMS:\n  " + "\n  ".join(problems)); sys.exit(1)

    # puzzles.js for the game
    def ev(e):
        t, n, y, a = EV[e][:4]
        o = {"tag": t, "name": n, "year": y}
        if a: o["approx"] = True
        return o
    days = [[{"L": ev(L), "M": ev(M), "R": ev(R), "fact": f} for (L, M, R, f) in day] for day in DAYS]
    with open(os.path.join(root, "public", "puzzles.js"), "w") as fh:
        fh.write("// Generated by tools/bank.py — edit the bank there, not here.\n")
        fh.write("// year \"now\" means the player's current year.\n")
        fh.write("window.CLOSER_DAYS = " + json.dumps(days, ensure_ascii=False, indent=1) + ";\n")

    os.makedirs(os.path.join(root, "data"), exist_ok=True)
    with open(os.path.join(root, "data", "events.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "event", "year", "approx", "category", "reach", "check", "used_in_puzzles", "source"])
        for k, (t, n, y, a, reach, src, chk) in EV.items():
            if k == "today": continue
            w.writerow([k, n, y, "yes" if a else "", t, reach, chk, "yes" if k in used else "", src])
    with open(os.path.join(root, "data", "rounds.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

    # summary
    for d in range(1, len(DAYS) + 1):
        dr = [x for x in rows if x["day"] == d]
        print(f"day {d:2}: " + " ".join(x["answer"][0] for x in dr) + "   last closeness " + str(dr[-1]["closeness"]))
    cats = {}
    for x in DAYS:
        for (L, M, R, f) in x: cats[EV[M][0]] = cats.get(EV[M][0], 0) + 1
    print("middle-event categories:", dict(sorted(cats.items(), key=lambda kv: -kv[1])))
    n_global = sum(1 for k, v in EV.items() if k != "today" and v[4] != "regional")
    print(f"events: {len(EV)-1} total, {n_global} usable, {len(used)-1} used in puzzles")

if __name__ == "__main__":
    main()
