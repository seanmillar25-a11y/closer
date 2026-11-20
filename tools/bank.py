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
 "earth":      ("Prehistory", "The Earth forms", -4_540_000_000, True, "global", W+"Age_of_Earth", "documented"),
 "life":       ("Prehistory", "Life first appears on Earth", -3_700_000_000, True, "global", W+"Earliest_known_life_forms", "documented"),
 "cambrian":   ("Prehistory", "The Cambrian explosion of animal life", -538_000_000, True, "global", W+"Cambrian_explosion", "documented"),
 "landplants": ("Prehistory", "Plants first grow on land", -470_000_000, True, "global", W+"Evolutionary_history_of_plants", "documented"),
 "insects":    ("Prehistory", "The first insects", -400_000_000, True, "global", W+"Evolution_of_insects", "documented"),
 "tetrapods":  ("Prehistory", "Animals first walk on land", -375_000_000, True, "global", W+"Tiktaalik", "documented"),
 "greatdying": ("Prehistory", "The Great Dying wipes out most life", -252_000_000, True, "global", W+"Permian%E2%80%93Triassic_extinction_event", "documented"),
 "pangaea":    ("Prehistory", "Pangaea begins to break apart", -175_000_000, True, "global", W+"Pangaea", "documented"),
 "tools":      ("Prehistory", "The first stone tools", -3_300_000, True, "global", W+"Lomekwi", "documented"),
 "lucy":       ("Prehistory", "Lucy, the famous early human ancestor", -3_200_000, True, "global", W+"Lucy_(Australopithecus)", "documented"),
 "erectus":    ("Prehistory", "Homo erectus appears", -1_900_000, True, "global", W+"Homo_erectus", "documented"),
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
 "farming":    ("Prehistory", "Farming begins", -10_000, True, "global", W+"Neolithic_Revolution", "documented"),
 "gobekli":    ("Prehistory", "Göbekli Tepe temple is built", -9_500, True, "global", W+"G%C3%B6bekli_Tepe", "documented"),
 "gilgamesh":  ("Literature", "The Epic of Gilgamesh is written down", -2_100, True, "global", W+"Epic_of_Gilgamesh", "documented"),
 "ramesses":   ("Ancient Egypt", "Ramesses II dies", -1_213, True, "global", W+"Ramesses_II", "documented"),
 "troy":       ("Ancient Greece", "The Trojan War (by tradition)", -1_184, True, "global", W+"Trojan_War", "documented"),
 "alphabet":   ("Invention", "The Phoenician alphabet", -1_050, True, "global", W+"Phoenician_alphabet", "documented"),
 "coins":      ("Invention", "The first coins", -600, True, "global", W+"Lydian_coinage", "documented"),
 "archimedes": ("Science", "Archimedes dies", -212, False, "global", W+"Archimedes", "documented"),
 "spartacus":  ("Rome", "Spartacus leads a slave revolt", -73, False, "global", W+"Spartacus", "documented"),
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
 # --- Added Nov 2026 so no event repeats across puzzles
 "wheel":      ("Invention", "The wheel is invented", -3_500, True, "global", W+"Wheel", "documented"),
 "hammurabi":  ("Law", "The Code of Hammurabi", -1_754, True, "global", W+"Code_of_Hammurabi", "documented"),
 "confucius":  ("China", "Confucius is born", -551, True, "global", W+"Confucius", "documented"),
 "marathon":   ("Ancient Greece", "The Battle of Marathon", -490, False, "global", W+"Battle_of_Marathon", "documented"),
 "parthenon":  ("Ancient Greece", "The Parthenon is completed", -432, False, "global", W+"Parthenon", "documented"),
 "socrates":   ("Ancient Greece", "Socrates dies", -399, False, "global", W+"Socrates", "documented"),
 "alexander":  ("Ancient Greece", "Alexander the Great dies", -323, False, "global", W+"Alexander_the_Great", "documented"),
 "hannibal":   ("Rome", "Hannibal crosses the Alps", -218, False, "global", W+"Hannibal%27s_crossing_of_the_Alps", "documented"),
 "terracotta": ("China", "The Terracotta Army is buried", -210, True, "global", W+"Terracotta_Army", "documented"),
 "colosseum":  ("Rome", "The Colosseum opens", 80, False, "global", W+"Colosseum", "documented"),
 "hagia":      ("Architecture", "Hagia Sophia is completed", 537, False, "global", W+"Hagia_Sophia", "documented"),
 "charlemagne":("Empires", "Charlemagne is crowned emperor", 800, False, "global", W+"Charlemagne", "documented"),
 "crusade":    ("War", "The First Crusade sets out", 1_096, False, "global", W+"First_Crusade", "documented"),
 "angkor":     ("Architecture", "Angkor Wat is built", 1_150, True, "global", W+"Angkor_Wat", "documented"),
 "genghis":    ("Empires", "Genghis Khan becomes Great Khan", 1_206, False, "global", W+"Genghis_Khan", "documented"),
 "marcopolo":  ("Exploration", "Marco Polo reaches China", 1_275, True, "global", W+"Marco_Polo", "documented"),
 "blackdeath": ("Disaster", "The Black Death reaches Europe", 1_347, False, "global", W+"Black_Death", "documented"),
 "forbidden":  ("China", "The Forbidden City is completed", 1_420, False, "global", W+"Forbidden_City", "documented"),
 "joan":       ("War", "Joan of Arc is executed", 1_431, False, "global", W+"Joan_of_Arc", "documented"),
 "leonardo":   ("Art", "Leonardo da Vinci is born", 1_452, False, "global", W+"Leonardo_da_Vinci", "documented"),
 "gama":       ("Exploration", "Vasco da Gama reaches India", 1_498, False, "global", W+"Vasco_da_Gama", "documented"),
 "luther":     ("Europe", "Luther's 95 Theses", 1_517, False, "global", W+"Ninety-five_Theses", "documented"),
 "magellan":   ("Exploration", "The first voyage around the world ends", 1_522, False, "global", W+"Magellan_expedition", "documented"),
 "copernicus": ("Science", "Copernicus puts the Sun at the centre", 1_543, False, "global", W+"De_revolutionibus_orbium_coelestium", "documented"),
 "elizabeth":  ("Monarchy", "Elizabeth I is crowned", 1_559, False, "global", W+"Elizabeth_I", "documented"),
 "stbasil":    ("Architecture", "St Basil's Cathedral is completed", 1_561, False, "global", W+"Saint_Basil%27s_Cathedral", "documented"),
 "hamlet":     ("Literature", "Shakespeare writes Hamlet", 1_600, True, "global", W+"Hamlet", "documented"),
 "versailles": ("Paris", "Versailles becomes the royal palace", 1_682, False, "global", W+"Palace_of_Versailles", "documented"),
 "stpete":     ("Europe", "Peter the Great founds St Petersburg", 1_703, False, "global", W+"Saint_Petersburg", "documented"),
 "seasons":    ("Music", "Vivaldi's Four Seasons is published", 1_725, False, "global", W+"The_Four_Seasons_(Vivaldi)", "documented"),
 "messiah":    ("Music", "Handel's Messiah premieres", 1_742, False, "global", W+"Messiah_(Handel)", "documented"),
 "cook":       ("Exploration", "Captain Cook reaches Australia", 1_770, False, "global", W+"James_Cook", "documented"),
 "balloon":    ("Flight", "People fly in a hot-air balloon", 1_783, False, "global", W+"Montgolfier_brothers", "documented"),
 "frenchrev":  ("Paris", "The French Revolution begins", 1_789, False, "global", W+"French_Revolution", "documented"),
 "vaccine":    ("Science", "The first vaccine", 1_796, False, "global", W+"Edward_Jenner", "documented"),
 "rosetta":    ("Ancient Egypt", "The Rosetta Stone is found", 1_799, False, "global", W+"Rosetta_Stone", "documented"),
 "napoleon":   ("Paris", "Napoleon crowns himself emperor", 1_804, False, "global", W+"Coronation_of_Napoleon", "documented"),
 "pride":      ("Literature", "Pride and Prejudice is published", 1_813, False, "global", W+"Pride_and_Prejudice", "documented"),
 "frankenstein":("Literature", "Frankenstein is published", 1_818, False, "global", W+"Frankenstein", "documented"),
 "carol":      ("Literature", "A Christmas Carol is published", 1_843, False, "global", W+"A_Christmas_Carol", "documented"),
 "telegraph":  ("Invention", "Morse sends his famous telegraph", 1_844, False, "global", W+"Samuel_Morse", "documented"),
 "goldrush":   ("America", "The California Gold Rush begins", 1_848, False, "global", W+"California_gold_rush", "documented"),
 "mobydick":   ("Literature", "Moby-Dick is published", 1_851, False, "global", W+"Moby-Dick", "documented"),
 "alice":      ("Literature", "Alice in Wonderland is published", 1_865, False, "global", W+"Alice%27s_Adventures_in_Wonderland", "documented"),
 "suez":       ("Engineering", "The Suez Canal opens", 1_869, False, "global", W+"Suez_Canal", "documented"),
 "periodic":   ("Science", "The periodic table", 1_869, False, "global", W+"Dmitri_Mendeleev", "documented"),
 "eighty":     ("Literature", "Around the World in Eighty Days", 1_872, False, "global", W+"Around_the_World_in_Eighty_Days", "documented"),
 "swanlake":   ("Music", "Swan Lake premieres", 1_877, False, "global", W+"Swan_Lake", "documented"),
 "krakatoa":   ("Disaster", "Krakatoa erupts", 1_883, False, "global", W+"1883_eruption_of_Krakatoa", "documented"),
 "benz":       ("Motoring", "Karl Benz patents the motor car", 1_886, False, "global", W+"Benz_Patent-Motorwagen", "documented"),
 "scream":     ("Art", "Munch paints The Scream", 1_893, False, "global", W+"The_Scream", "documented"),
 "xrays":      ("Science", "X-rays are discovered", 1_895, False, "global", W+"X-ray", "documented"),
 "dracula":    ("Literature", "Dracula is published", 1_897, False, "global", W+"Dracula", "documented"),
 "nobel":      ("Science", "The first Nobel Prizes", 1_901, False, "global", W+"Nobel_Prize", "documented"),
 "einstein":   ("Science", "Einstein's special relativity", 1_905, False, "global", W+"Special_relativity", "documented"),
 "southpole":  ("Exploration", "Amundsen reaches the South Pole", 1_911, False, "global", W+"Roald_Amundsen", "documented"),
 "russianrev": ("Empires", "The Russian Revolution", 1_917, False, "global", W+"Russian_Revolution", "documented"),
 "tuttomb":    ("Ancient Egypt", "Tutankhamun's tomb is discovered", 1_922, False, "global", W+"KV62", "documented"),
 "crash":      ("America", "The Wall Street Crash", 1_929, False, "global", W+"Wall_Street_crash_of_1929", "documented"),
 "empirestate":("America", "The Empire State Building opens", 1_931, False, "global", W+"Empire_State_Building", "documented"),
 "earhart":    ("Flight", "Amelia Earhart flies solo across the Atlantic", 1_932, False, "global", W+"Amelia_Earhart", "documented"),
 "monopoly":   ("Games", "Monopoly goes on sale", 1_935, False, "global", W+"Monopoly_(game)", "documented"),
 "superman":   ("Literature", "Superman first appears", 1_938, False, "global", W+"Action_Comics_1", "documented"),
 "oz":         ("Film", "The Wizard of Oz is released", 1_939, False, "global", W+"The_Wizard_of_Oz_(1939_film)", "documented"),
 "eniac":      ("Technology", "The ENIAC computer is unveiled", 1_946, False, "global", W+"ENIAC", "documented"),
 "robinson":   ("Sport", "Jackie Robinson breaks baseball's colour line", 1_947, False, "global", W+"Jackie_Robinson", "documented"),
 "orwell":     ("Literature", "Nineteen Eighty-Four is published", 1_949, False, "global", W+"Nineteen_Eighty-Four", "documented"),
 "everest":    ("Exploration", "Everest is first climbed", 1_953, False, "global", W+"1953_British_Mount_Everest_expedition", "documented"),
 "dna":        ("Science", "The DNA double helix", 1_953, False, "global", W+"Nucleic_acid_double_helix", "documented"),
 "elvis":      ("Music", "Elvis releases Heartbreak Hotel", 1_956, False, "global", W+"Heartbreak_Hotel", "documented"),
 "sputnik":    ("Space", "Sputnik, the first satellite", 1_957, False, "global", W+"Sputnik_1", "documented"),
 "pele":       ("Sport", "Pelé wins his first World Cup", 1_958, False, "global", W+"1958_FIFA_World_Cup", "documented"),
 "lego":       ("Games", "The Lego brick is patented", 1_958, False, "global", W+"Lego", "documented"),
 "barbie":     ("Games", "Barbie goes on sale", 1_959, False, "global", W+"Barbie", "documented"),
 "gagarin":    ("Space", "Yuri Gagarin goes into space", 1_961, False, "global", W+"Yuri_Gagarin", "documented"),
 "jfk":        ("America", "President Kennedy is assassinated", 1_963, False, "global", W+"Assassination_of_John_F._Kennedy", "documented"),
 "heart":      ("Science", "The first heart transplant", 1_967, False, "global", W+"Christiaan_Barnard", "documented"),
 "fosbury":    ("Sport", "The Fosbury Flop wins Olympic gold", 1_968, False, "global", W+"Dick_Fosbury", "documented"),
 "rumble":     ("Sport", "The Rumble in the Jungle", 1_974, False, "global", W+"The_Rumble_in_the_Jungle", "documented"),
 "rubik":      ("Games", "The Rubik's Cube is invented", 1_974, False, "global", W+"Rubik%27s_Cube", "documented"),
 "jaws":       ("Film", "Jaws is released", 1_975, False, "global", W+"Jaws_(film)", "documented"),
 "nadia":      ("Sport", "The first perfect 10 in Olympic gymnastics", 1_976, False, "global", W+"Nadia_Com%C4%83neci", "documented"),
 "concorde":   ("Flight", "Concorde's first passenger flight", 1_976, False, "global", W+"Concorde", "documented"),
 "invaders":   ("Games", "Space Invaders is released", 1_978, False, "global", W+"Space_Invaders", "documented"),
 "walkman":    ("Music", "The Sony Walkman goes on sale", 1_979, False, "global", W+"Walkman", "documented"),
 "thriller":   ("Music", "Michael Jackson's Thriller", 1_982, False, "global", W+"Thriller_(album)", "documented"),
 "chernobyl":  ("Disaster", "The Chernobyl disaster", 1_986, False, "global", W+"Chernobyl_disaster", "documented"),
 "gameboy":    ("Games", "The Game Boy goes on sale", 1_989, False, "global", W+"Game_Boy", "documented"),
 "simpsons":   ("Film", "The Simpsons begins as a TV series", 1_989, False, "global", W+"The_Simpsons", "documented"),
 "hubble":     ("Space", "The Hubble Space Telescope launches", 1_990, False, "global", W+"Hubble_Space_Telescope", "documented"),
 "mandela":    ("Democracy", "Nelson Mandela is freed", 1_990, False, "global", W+"Nelson_Mandela", "documented"),
 "ussr":       ("Cold War", "The Soviet Union breaks up", 1_991, False, "global", W+"Dissolution_of_the_Soviet_Union", "documented"),
 "playstation":("Games", "The PlayStation goes on sale", 1_994, False, "global", W+"PlayStation_(console)", "documented"),
 "toystory":   ("Film", "Toy Story, the first computer-animated feature", 1_995, False, "global", W+"Toy_Story", "documented"),
 "pokemon":    ("Games", "The first Pokémon games", 1_996, False, "global", W+"Pok%C3%A9mon_Red_and_Blue", "documented"),
 "genome":     ("Science", "The human genome is sequenced", 2_003, False, "global", W+"Human_Genome_Project", "documented"),
 "facebook":   ("Technology", "Facebook launches", 2_004, False, "global", W+"Facebook", "documented"),
 "phelps":     ("Sport", "Michael Phelps wins eight golds in one Games", 2_008, False, "global", W+"Michael_Phelps", "documented"),
 "bitcoin":    ("Technology", "Bitcoin is launched", 2_009, False, "global", W+"Bitcoin", "documented"),
 "higgs":      ("Science", "The Higgs boson is found", 2_012, False, "global", W+"Higgs_boson", "documented"),
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
# Repeat limits (checked below): question events never repeat; left/right events
# at most MAX_USES times, MIN_GAP_DAYS apart. "today" is exempt.
DAYS = [
 [ # 1
  ("pyramid","cleopatra","moon","Cleopatra lived about 2,500 years after the Great Pyramid was built, but only about 2,000 years before Apollo 11. To her, the pyramids were already ancient."),
  ("cook","civilwar","email","The American Civil War began in 1861, 91 years after Captain Cook reached Australia's east coast and 110 years before the first email."),
  ("stego","trex","today","About 80 million years separate Stegosaurus and T. rex. That's more time than separates T. rex from you."),
  ("gobekli","mammoths","today","Woolly mammoths survived on Wrangel Island in the Arctic until around 2000 BC, after the Great Pyramid was built. That's closer to today than to Göbekli Tepe, one of the oldest known temples."),
  ("genghis","aztecs","joan","A close one: the Aztecs founded Tenochtitlan, on the site of today's Mexico City, in 1325, 119 years after Genghis Khan became Great Khan and 106 years before Joan of Arc was executed."),
 ],
 [ # 2
  ("sharks","trees","greatdying","Sharks are older than trees. The oldest undisputed shark scales are about 420 million years old, while the first trees grew around 385 million years ago."),
  ("quixote","sherlock","potter","Sherlock Holmes first appeared in 1887, created by Edinburgh-born Arthur Conan Doyle. He's closer in time to Harry Potter than to Don Quixote."),
  ("napoleon","nintendo","mario","Nintendo was founded in 1889 to make hand-made playing cards, 85 years after Napoleon crowned himself emperor."),
  ("wallup","tetris","wallfalls","Tetris was created in Moscow in 1984, five years before the Berlin Wall fell."),
  ("benz","worldcup","invaders","A close one: the first football World Cup, held in Uruguay in 1930, came 44 years after Karl Benz patented his motor car and 48 years before Space Invaders."),
 ],
 [ # 3
  ("parthenon","machu","today","Machu Picchu looks ancient, but the Inca built it around 1450. That's much closer to today than to the building of the Parthenon in Athens."),
  ("periodic","pluto","plutodemote","Pluto was discovered in 1930, 61 years after Mendeleev drew up the periodic table, and counted as a planet for 76 years until 2006."),
  ("hubble","gta","genome","The original Grand Theft Auto was made in Dundee by DMA Design and released in 1997, seven years after Hubble launched and six years before the human genome was sequenced."),
  ("scream","mile","today","Roger Bannister ran the first mile in under four minutes in 1954, closer in time to Munch painting The Scream than to today."),
  ("ramesses","olympia","socrates","A close one: the first recorded Olympics, in 776 BC, are slightly closer to the death of Socrates than to the death of Ramesses II."),
 ],
 [ # 4
  ("elizabeth","harvard","versailles","Harvard was founded in 1636, closer in time to Louis XIV moving his court to Versailles than to Elizabeth I's coronation."),
  ("carol","bigben","phone","Big Ben first rang out in 1859, 16 years after Dickens's A Christmas Carol and 17 years before Edinburgh-born Alexander Graham Bell patented the telephone."),
  ("armada","dodo","decl","The dodo was gone more than a century before the United States existed."),
  ("monalisa","taj","ninth","The Taj Mahal was finished around 1653, about 150 years after Leonardo began the Mona Lisa and roughly 170 years before Beethoven's Ninth Symphony was first performed."),
  ("civilend","coke","einstein","A close one: Coca-Cola was invented in 1886, 21 years after the American Civil War ended and 19 years before Einstein's special relativity."),
 ],
 [ # 5
  ("hannibal","oxford","today","Teaching at Oxford began in 1096. Oxford is closer in time to you than to Hannibal crossing the Alps with his elephants."),
  ("mobydick","bulb","modelt","Edison's practical light bulb arrived in 1879, 28 years after Moby-Dick and 29 years before the Model T."),
  ("firstdinos","asteroid","today","Dinosaurs had been around for over 160 million years when the asteroid hit, about 66 million years ago. The end of their reign is closer to us than to its beginning."),
  ("copernicus","mayflower","stpete","The Mayflower landed in 1620, 77 years after Copernicus put the Sun at the centre of the universe and 83 years before St Petersburg was founded."),
  ("starry","mickey","starwars","Mickey Mouse made his debut in Steamboat Willie in 1928, 39 years after Van Gogh painted The Starry Night and 49 years before Star Wars."),
 ],
 [ # 6
  ("iliad","pompeii","today","Pompeii was buried by Vesuvius in AD 79, roughly 800 years after Homer's Iliad is thought to have been written down."),
  ("archimedes","vending","today","Hero of Alexandria designed a coin-operated holy water dispenser in the 1st century AD, only about 260 years after Archimedes died."),
  ("charlemagne","magna","fire","Magna Carta was sealed in 1215, 415 years after Charlemagne was crowned emperor and 451 years before the Great Fire of London."),
  ("oscars","beatles","today","The Beatles released their first album, Please Please Me, in 1963, only 34 years after the first Academy Awards."),
  ("walkman","youtube","today","A close call: YouTube launched in 2005, 26 years after the Sony Walkman first went on sale."),
 ],
 [ # 7
  ("waterloo","match","victoria","John Walker invented the friction match in 1826, 11 years after the Battle of Waterloo and 12 years before Queen Victoria was crowned."),
  ("tincan","canopener","wright","For almost 50 years people opened tin cans with hammers and chisels. The dedicated can opener didn't appear until 1858."),
  ("alice","tv","gameboy","John Logie Baird, from Helensburgh in Scotland, gave the first public demonstration of television in 1926, 61 years after Alice in Wonderland was published."),
  ("nobel","superbowl","today","The first Super Bowl was played in January 1967, 66 years after the first Nobel Prizes were awarded."),
  ("fosbury","dolly","today","A close call: Dolly, cloned at the Roslin Institute near Edinburgh, was born in 1996, 28 years after Dick Fosbury flopped his way to Olympic gold."),
 ],
 [ # 8
  ("insects","flowers","today","Insects had been around for well over 200 million years before the first flowers. Flowering plants are closer in time to you than to the first insects."),
  ("farming","gilgamesh","today","The Epic of Gilgamesh, one of the oldest known stories, was first written down around 2100 BC. That's closer to today than to the beginnings of farming."),
  ("sapiens","neander","today","Our species shared the planet with Neanderthals for well over 200,000 years before they disappeared, roughly 40,000 years ago."),
  ("pangaea","apes","today","The first apes appeared around 25 million years ago, long after the supercontinent Pangaea began to break apart."),
  ("alexander","terracotta","caesar","China's Terracotta Army was buried around 210 BC with the First Emperor, about 110 years after Alexander the Great died."),
 ],
 [ # 9
  ("crusade","cambridge","blackdeath","Cambridge was founded in 1209, traditionally by scholars who left Oxford, 113 years after the First Crusade set out."),
  ("gutenberg","galileo","messiah","Galileo first turned a telescope to the sky in 1609, slightly closer in time to Handel's Messiah than to the Gutenberg Bible."),
  ("lighter","basketball","jfk","Basketball was invented in 1891 by James Naismith, a Canadian teacher in Massachusetts, 68 years after the first lighter."),
  ("magellan","principia","darwin","Newton's Principia appeared in 1687, 165 years after the first voyage around the world ended and 172 years before Darwin's Origin of Species."),
  ("jaws","www","euro","A close one: Tim Berners-Lee proposed the World Wide Web in 1989, 14 years after Jaws and 13 years before euro notes and coins arrived."),
 ],
 [ # 10
  ("football","liberty","ww1","The Statue of Liberty was unveiled in New York in 1886, a gift from the people of France."),
  ("eiffel","tour","titanic","The first Tour de France was raced in 1903, 14 years after the Eiffel Tower opened and nine years before the Titanic sank."),
  ("chernobyl","bolt","today","Usain Bolt ran 100 metres in 9.58 seconds at the 2009 World Championships in Berlin, 23 years after the Chernobyl disaster."),
  ("rumble","google","today","Google was founded in 1998, 24 years after Muhammad Ali beat George Foreman in the Rumble in the Jungle."),
  ("ww2end","woodstock","chunnel","The closest call of the day: Woodstock came 24 years after the Second World War ended and 25 years before the Channel Tunnel opened."),
 ],
 [ # 11
  ("qin","hadrian","ming","Hadrian's Wall was begun in AD 122, about 340 years after China's First Emperor unified the country. Most of the Great Wall you can visit today came much later, under the Ming dynasty."),
  ("marathon","constant","today","The Roman Empire survived in the east until 1453, when the Ottomans took Constantinople. That's closer to today than to the Battle of Marathon."),
  ("goldrush","ottoman","today","The Ottoman Empire, founded around 1300, lasted until 1922. Its end is closer to the California Gold Rush than to today."),
  ("hammurabi","tut","alphabet","Tutankhamun died around 1323 BC, closer in time to the Phoenician alphabet than to Hammurabi's code of laws."),
  ("romefall","vinland","columbus","Leif Erikson's Vikings reached North America around the year 1000, slightly closer to Columbus than to the fall of the Western Roman Empire in 476."),
 ],
 [ # 12
  ("seasons","photo","empirestate","Nicéphore Niépce took the oldest surviving camera photograph around 1826, about a century after Vivaldi's Four Seasons was published."),
  ("vaccine","antarctica","fax","Nobody had seen Antarctica until 1820, 24 years after Edward Jenner gave the first vaccination."),
  ("tuttomb","eurovision","liveaid","The first Eurovision Song Contest was held in Switzerland in 1956, with just seven countries taking part."),
  ("orwell","mobile","iphone","Motorola's Martin Cooper made the first handheld mobile phone call in 1973, 24 years after Orwell's Nineteen Eighty-Four was published."),
  ("telegraph","speeding","eniac","A close one: in 1896 Walter Arnold was fined for driving at 8mph in Kent, four times the speed limit, in what is often called the first speeding ticket."),
 ],
 [ # 13
  ("writing","stonehenge","confucius","Stonehenge's great sarsen stones went up around 2500 BC, about 700 years after writing first appeared in Mesopotamia."),
  ("lascaux","iceage","today","The last Ice Age ended around 9700 BC, closer in time to the Lascaux cave paintings than to today."),
  ("spartacus","colosseum","today","The Colosseum in Rome opened in AD 80, about 150 years after Spartacus led his slave revolt."),
  ("troy","rome","today","Rome's legendary founding in 753 BC is closer to the traditional date of the Trojan War than to today."),
  ("wheel","coins","today","A close one: the first coins were made in Lydia, in today's Turkey, around 600 BC. That's slightly closer to today than to the invention of the wheel."),
 ],
 [ # 14
  ("marcopolo","sistine","today","Michelangelo finished painting the Sistine Chapel ceiling in 1512, closer in time to Marco Polo's travels than to today."),
  ("rosetta","chocolate","dracula","Fry's of Bristol made the first moulded chocolate bar in 1847. Before that, chocolate was mostly a drink."),
  ("bicycle","tube","southpole","The world's first underground railway opened in London in 1863, with steam trains running through the tunnels."),
  ("hagia","angkor","today","Angkor Wat, built in the 1100s, is closer in time to Constantinople's Hagia Sophia, finished in 537, than to today."),
  ("leonardo","mozart","today","Mozart was born in 1756, slightly closer to today than to the birth of Leonardo da Vinci."),
 ],
 [ # 15
  ("balloon","samurai","heart","Samurai were still fighting in 1877, slightly closer in time to the first heart transplant than to the first people flying in a hot-air balloon."),
  ("frenchrev","nzvote","today","New Zealand became the first country to give women the vote in national elections, in 1893."),
  ("guernica","bubble","concorde","Bubble wrap was invented in 1957 by Alfred Fielding and Marc Chavannes, who were trying to make textured wallpaper. It didn't catch on as wallpaper."),
  ("paralympics","sms","today","The first text message, 'Merry Christmas', was sent in December 1992, 32 years after the first Paralympic Games in Rome."),
  ("thriller","wikipedia","today","Wikipedia launched in January 2001, 19 years after Michael Jackson's Thriller came out."),
 ],
]

MAX_USES = 3        # most times any event may appear across all puzzles
MIN_GAP_DAYS = 30   # fewest days between two appearances of the same event

def yr(eid, year_now):
    y = EV[eid][2]
    return year_now if y == NOW else y

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    problems, rows, seen = [], [], {}
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
            for e in (L, M, R):
                if e != "today":
                    seen.setdefault(e, []).append(f"{d}.{r}")
            if "years before today" in fact or "years ago" in fact and "today" in fact:
                problems.append(f"day {d} round {r}: fact mentions years before today")
            l, m, rr = yr(L, 2026), yr(M, 2026), yr(R, 2026)
            gl, gr = m - l, rr - m
            rows.append(dict(day=d, round=r, left=EV[L][1], middle=EV[M][1], right=EV[R][1],
                             answer="Left" if gl < gr else "Right", gap_left=gl, gap_right=gr,
                             closeness=round(min(gl, gr) / max(gl, gr), 2), fact=fact))
    # Repeat limits: a middle (question) event is never reused; an anchor (left/right)
    # event may appear up to MAX_USES times, at least MIN_GAP_DAYS apart, never twice in a day.
    mids = {}
    for d, day in enumerate(DAYS, 1):
        for r, (L, M, R, f) in enumerate(day, 1):
            mids.setdefault(M, []).append(f"{d}.{r}")
    for e, where in mids.items():
        if len(where) > 1: problems.append(f"question used twice: {EV[e][1]} in rounds {', '.join(where)}")
    for e, where in seen.items():
        if len(where) > MAX_USES:
            problems.append(f"used {len(where)} times (max {MAX_USES}): {EV[e][1]} in {', '.join(where)}")
        days = sorted(int(w.split('.')[0]) for w in where)
        for a, b in zip(days, days[1:]):
            if b - a < MIN_GAP_DAYS:
                problems.append(f"repeated within {MIN_GAP_DAYS} days: {EV[e][1]} in {', '.join(where)}"); break
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
