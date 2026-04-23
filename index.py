import os
import re
import json
import csv
import html
from docx import Document

# --- 1. KONFIGURATION ---
SITE_NAME = "the vault of antichrister"
BASE_INPUT = 'Manus'
CSV_FILE = 'Filmlista - Blad1.csv'
PDF_INPUT = 'Pressklipp'
VAULT_PASSWORD = '46275Thevault'
CATEGORIES = ['Recensioner', 'Artiklar', 'Uppsats', 'Intervjuer', 'Filmhistoria', 'Information om The Vault']
ALPHABETICAL_CATEGORIES = {'Recensioner', 'Artiklar', 'Intervjuer', 'Information om The Vault'}
EXTRA_CATEGORY_DIRS = {
    'Recensioner': ['reviews'],
    'Artiklar': ['articles'],
    'Intervjuer': ['interviews'],
    'Information om The Vault': ['vault_info'],
}

# Recensioner ursprungligen publicerade på SweGore (matchas på normaliserad titel i gemener)
SWEGORE_TITLES = {
    'black christmas',
    'caged',
    'dead air',
    'deep red',
    'djävla djur. box',
    'donkey punch',
    'eden log',
    'maniac',
    'phenomena',
    'rats – nattens terror',
    'skin in the fifties – the flesh merchant',
    'skräcken har 1000 ögon',
    'the abandoned',
    'the nightmare on elm street collection',
    'the nightmare on elm street collect',
    'the sexploiters',
    'trick or treat',
    'two evil eyes',
    'the beyond',
    'stage fright',
    'district 9',
    'fascination',
    'fredagen 13:e del 3',
    'lucio fulci remembered vol. 1',
    'lucio fulci remembered vol 1',
    'scandinavian blue: erotic cinema of sweden and denmark in the 1960s and 1970s',
    'scandinavian blue: erotic cinema of',
}

# Artiklar ursprungligen publicerade på bloggarna Dawn of the Blog och Mondo Madness
BLOG_TITLES = {
    'dokumentärfilm',
    "don\u2019t call me motherfucker, motherfucker",
    "don\u2019t call me motherfucker, motherfucker!",
    'exploitation: den svårfångade genren',
    'filmtips till halloween.',
    'filmtips till halloween',
    'hur jag slutade oroa mig om bomben och istället älska dess efterdyningar i italiensk filmindustri',
    'hur jag slutade oroa mig om bomben och istället älska dess efterdyningar i italiensk filmindustri!',
    'komedier',
    'mondo movie madness – varför tittar vi?',
    'mondo movie madness  varför tittar vi',
    'människans gryning... full av monster, bystiga tjejer och sämsta smaken',
    'människans gryning... full av monster, bystiga tjejer och sämsskinnsbeklädda hjältar.',
    'riktigt otäcka filmer!',
    'riktigt otäcka filmer',
    'russ meyer: thanks for the mammaries!',
    'russ meyer thanks for the mammaries',
    'sex lögner om videovåld',
    'tack för minnet!',
    'tack för minnet',
    'the big four eller en thrashares bekännelser!',
    'the big four eller en thrashares bekännelser',
    'the dead walk!',
    'the dead walk',
    'the texas chainsaw massacre – 40 år',
    'the texas chainsaw massacre  40 år',
    'these reboots are made for stalking!',
    'these reboots are made for stalking',
    'these reboots are made for stalking! fredag den 13:e',
}

# --- 2. HJÄLPFUNKTIONER ---
def slugify(text):
    if not text: return "sida.html"
    text = text[:50].lower().strip().replace(" ", "_")
    text = re.sub(r'[^\w\s-]', '', text)
    if not text.endswith(".html"): text += ".html"
    return text

def stada_text(text):
    return re.sub(r'([.,!?;:])([a-zA-ZåäöÅÄÖ])', r'\1 \2', text)

def normalize_title(text):
    """Normalisera titel utan att tvinga fram Title Case på varje ord."""
    if not text:
        return text

    normalized = re.sub(r'\s{2,}', ' ', text).strip()
    if not normalized:
        return normalized

    # Om titeln är helt versal/gemen: gör den läsbar i enkel meningsform.
    if normalized.isupper() or normalized.islower():
        lowered = normalized.lower()
        return re.sub(r'([a-zåäö])', lambda m: m.group(1).upper(), lowered, count=1)

    # Vid blandad case antar vi att källan redan har avsedd formatering.
    return normalized

def clean_review_title(text):
    title = normalize_title(text)
    if not title:
        return title

    # Klipp bort vanliga metadata-suffix i recensionsrubriker.
    for marker in (' publicerad i ', ' skribent ', ' by '):
        idx = title.lower().find(marker)
        if idx > 0:
            title = title[:idx].strip()
            break

    # Ta bort avslutande parenteser om de innehåller metadata, men behåll t.ex. årtal.
    while True:
        m = re.search(r'\s*\(([^()]*)\)\s*$', title)
        if not m:
            break
        paren_text = m.group(1).lower()
        if any(token in paren_text for token in ('publicerad', 'skribent', 'violent vision', 'by ')):
            title = title[:m.start()].strip()
        else:
            break

    title = re.sub(r'\s{2,}', ' ', title).strip(' -_')
    return title or normalize_title(text)

def extract_publication_note(text):
    title = normalize_title(text)
    if not title:
        return ''

    # Hitta och behåll var texten publicerats.
    m = re.search(r'\b(publicerad i [^\]\)]+)', title, flags=re.IGNORECASE)
    if not m:
        return ''

    note = m.group(1).strip(' .;,:-_')
    if not note:
        return ''
    return note[0].upper() + note[1:]

def normalize_title_for_category(cat, text):
    title = normalize_title(text)
    if cat in {'Recensioner', 'Artiklar'}:
        cleaned = clean_review_title(title)
        # Specialfall: Tied by conventions blir förkortad till bara Tied
        if cleaned == 'Tied' and 'by conventions' in title.lower():
            return 'Tied by conventions'
        return cleaned
    if cat == 'Filmhistoria' and title == 'Filmkompendie VT 2001 – av Christer Persson och Anne Hammenroth':
        return 'Filmkompendie 2001 av Christer Persson och Anne Hammenroth'
    if cat == 'Intervjuer' and 'psychopathic' in title.lower() and 'morghen' in title.lower():
        return 'John Morghen - From Psychopathic to Ecclesiastic!'
    if cat == 'Intervjuer' and 'jack stevenson' in title.lower() and 'interview' not in title.lower():
        return 'Jack Stevenson and the Swedish sin!'
    if cat == 'Intervjuer' and 'jack stevenson' in title.lower() and 'interview' in title.lower():
        return 'Jack Stevenson 1999'
    return title

def extrahera_nummer(filename):
    match = re.match(r'(\d+)', filename)
    return int(match.group()) if match else 999

def titel_fran_filnamn(filename):
    base = os.path.splitext(os.path.basename(filename))[0]
    return normalize_title(re.sub(r'[_-]+', ' ', base))

def make_unique_slug(base_slug, used_slugs):
    if base_slug not in used_slugs:
        used_slugs.add(base_slug)
        return base_slug
    stem, ext = os.path.splitext(base_slug)
    idx = 2
    while True:
        candidate = f"{stem}_{idx}{ext}"
        if candidate not in used_slugs:
            used_slugs.add(candidate)
            return candidate
        idx += 1

def html_till_text(raw_html):
    cleaned = re.sub(r'<script.*?</script>', ' ', raw_html, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'<style.*?</style>', ' ', cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'<[^>]+>', '\n', cleaned)
    cleaned = html.unescape(cleaned)
    return cleaned

def hamta_reading_room_block(raw_html):
    lower = raw_html.lower()
    marker = '<div class="reading-room"'
    idx = lower.find(marker)
    if idx == -1:
        return raw_html
    tail = raw_html[idx:]
    script_match = re.search(r'<script\b', tail, flags=re.IGNORECASE)
    if script_match:
        tail = tail[:script_match.start()]
    return tail

def hamta_html_rader_och_titel(path, fallback_title):
    source_path = path
    if os.path.isfile(path) and os.path.getsize(path) == 0 and os.path.isfile(path + ".html"):
        source_path = path + ".html"

    try:
        with open(source_path, 'r', encoding='utf-8', errors='ignore') as f:
            raw = f.read()
    except Exception:
        return normalize_title(fallback_title), []

    reading_room = hamta_reading_room_block(raw)
    h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', reading_room, flags=re.IGNORECASE | re.DOTALL)
    if h1_match:
        heading = re.sub(r'<[^>]+>', ' ', h1_match.group(1))
        parsed_title = normalize_title(html.unescape(heading).strip())
    else:
        parsed_title = ''

    text = html_till_text(reading_room)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return (parsed_title or normalize_title(fallback_title)), lines

def rad_ar_rubrik(rad):
    txt = rad.strip()
    if not txt:
        return False
    # Matchar rubriker som "I. Inledning", "1. Bakgrund", "1.1. Metod"
    return bool(re.match(r'^(?:[IVXLCDM]+\.\s+\S.*|\d+\.(?:\d+\.)?\s+\S.*)$', txt, flags=re.IGNORECASE))

def rad_till_paragraf(rad):
    txt = stada_text(rad)
    css_class = ' class="section-heading"' if rad_ar_rubrik(rad) else ''
    return f"<p{css_class}>" + txt + "</p>"

def markera_rubriker_i_html(content_html):
    pattern = re.compile(r'<p>(\s*(?:[IVXLCDM]+\.\s+[^<]+|\d+\.(?:\d+\.)?\s+[^<]+)\s*)</p>', re.IGNORECASE)
    return pattern.sub(r'<p class="section-heading">\1</p>', content_html)

def parse_category_page_entries(cat):
    entries = []
    cat_page = f"cat_{slugify(cat)}"
    if not os.path.isfile(cat_page):
        return entries

    with open(cat_page, 'r', encoding='utf-8', errors='ignore') as f:
        raw = f.read()

    reading_room = hamta_reading_room_block(raw)
    link_matches = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', reading_room, flags=re.IGNORECASE | re.DOTALL)

    for href, link_text in link_matches:
        href = href.strip()
        if not href.lower().endswith('.html'):
            continue
        if not os.path.isfile(href):
            continue

        clean_link_title = normalize_title(html.unescape(re.sub(r'<[^>]+>', ' ', link_text)).strip() or titel_fran_filnamn(href))
        title, lines = hamta_html_rader_och_titel(href, clean_link_title)
        if not lines:
            continue

        content = [rad_till_paragraf(line) for line in lines]
        if content:
            entries.append({'title': title, 'cat': cat, 'content': content})

    return entries

def skapa_entries_fran_rader(lines, cat, fallback_title):
    entries = []
    current = None
    has_titel_blocks = False

    for line in lines:
        txt = line.strip()
        if not txt:
            continue
        if txt.lower().startswith('titel:'):
            raw_title = txt.split(':', 1)[1].strip() or fallback_title
            title = normalize_title_for_category(cat, raw_title)
            # Argento speaks! hör till Intervjuer – hoppas över i Artiklar (finns i interviews/)
            if cat == 'Artiklar' and 'argento speaks' in raw_title.lower():
                current = None
                has_titel_blocks = True
                continue
            current = {'title': title, 'cat': cat, 'content': []}
            if cat in {'Recensioner', 'Artiklar'}:
                publication_note = extract_publication_note(raw_title)
                if publication_note:
                    current['content'].append("<p><em>" + stada_text(publication_note) + "</em></p>")
            entries.append(current)
            has_titel_blocks = True
            continue
        if current is not None:
            current['content'].append(rad_till_paragraf(txt))

    if has_titel_blocks:
        return entries

    content = [rad_till_paragraf(line.strip()) for line in lines if line.strip()]
    if content:
        return [{'title': normalize_title(fallback_title), 'cat': cat, 'content': content}]
    return []

def parse_source_file(path, cat):
    fallback_title = titel_fran_filnamn(path)
    lower = path.lower()

    try:
        if lower.endswith('.docx'):
            doc = Document(path)
            lines = [p.text for p in doc.paragraphs]
            return skapa_entries_fran_rader(lines, cat, fallback_title)

        if lower.endswith('.txt'):
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.read().splitlines()
            return skapa_entries_fran_rader(lines, cat, fallback_title)

        if lower.endswith(('.html', '.htm')):
            title, lines = hamta_html_rader_och_titel(path, fallback_title)
            return skapa_entries_fran_rader(lines, cat, title)
    except Exception:
        return []

    return []

# --- 3. DESIGN (CSS) ---
CSS_CODE = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Lora:ital,wght@0,400;0,500;1,400&family=Playfair+Display:ital,wght@1,600&display=swap');

:root {
  --bg-color: #0d1117;
  --paper-base: #e2dac7; 
  --card-paper: #f4e4bc; 
  --text-dark: #2a2a2a;
  --text-bright: #ffffff;
  --border: #444c56;
  --accent: #f85149;
}

html { overflow-y: scroll; }

body {
  margin: 0; padding: 0; 
  font-family: 'Inter', sans-serif;
  background-color: var(--bg-color);
  background-image: url('background.jpg');
  background-attachment: fixed; 
  background-size: cover;
  background-position: center;
}

.main-nav { background: rgba(13, 17, 23, 0.98); border-bottom: 1px solid var(--border); position: sticky; top: 0; z-index: 1000; height: 110px; width: 100%; }
.nav-container { max-width: 1400px; margin: 0 auto; padding: 0 30px; height: 110px; display: flex; justify-content: flex-end; align-items: center; position: relative; }

.vault-logo { 
    max-width: 280px; position: absolute; left: 30px; top: 20px; 
    cursor: pointer; z-index: 1100; filter: drop-shadow(0 0 20px rgba(0,0,0,0.6));
    transform: rotate(-5deg); transition: transform 0.3s ease;
    will-change: transform;
}
.vault-logo:hover { transform: rotate(-2deg) scale(1.04); }

.nav-links { list-style: none; display: flex; gap: 0; margin: 0; padding: 0; height: 100%; }
.nav-item { position: relative; display: flex; align-items: center; height: 110px; padding: 0 15px; }
.nav-item > a { color: var(--text-bright); text-decoration: none; font-size: 0.9rem; text-transform: lowercase; transition: color 0.2s; display: block; line-height: 110px; }
.nav-item:hover > a { color: var(--accent); }

.dropdown-content { 
    display: none; position: absolute; top: 110px; right: 0; 
    background: #1c2128; min-width: 280px; border: 1px solid var(--border);
    box-shadow: 0 15px 40px rgba(0,0,0,0.8);
    max-height: 70vh;
    overflow-y: auto;
    overflow-x: hidden;
}
.dropdown-content a { display: block; padding: 14px 20px; color: white; text-decoration: none; border-bottom: 1px solid var(--border); font-size: 0.85rem; }
.dropdown-content a:hover { background: #2d333b; color: var(--accent); }
.nav-item:hover .dropdown-content { display: block; }

.reading-room { background-color: var(--paper-base); color: var(--text-dark); max-width: 1000px; margin: 60px 5% 80px 400px; padding: 60px 50px; font-family: 'Lora', serif; border-radius: 8px; box-shadow: 40px 40px 90px rgba(0,0,0,0.8); position: relative; }
.reading-room h1 { font-family: 'Playfair Display', serif; font-size: 2.8rem; text-align: center; margin-bottom: 30px; font-style: italic; }
.reading-room .content p.section-heading { margin-top: 1.1em; }

.film-table { width: 100%; border-collapse: collapse; margin-top: 20px; table-layout: fixed; }
.film-table td { padding: 12px; border-bottom: 1px solid rgba(0,0,0,0.1); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.film-title-link { color: var(--text-dark); text-decoration: none; cursor: pointer; transition: text-shadow 0.2s; }
.film-title-link:hover { text-shadow: 0.5px 0 0 var(--text-dark), -0.5px 0 0 var(--text-dark); color: var(--accent); }

#filmCardOverlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); z-index: 6000; overflow-y: auto; padding: 20px; }
.archival-card { background-color: var(--card-paper); color: var(--text-dark); max-width: 500px; margin: 40px auto; padding: 30px; font-family: 'Lora', serif; border-radius: 4px; position: relative; box-shadow: 0 20px 50px rgba(0,0,0,0.5); }
.archival-card h2 { font-family: 'Playfair Display', serif; font-size: 2rem; border-bottom: 1px solid var(--text-dark); padding-bottom: 10px; margin-bottom: 20px; font-style: italic; text-align: center; }
.card-close { position: absolute; top: 10px; right: 15px; font-size: 35px; cursor: pointer; }
.card-item { margin-bottom: 10px; display: flex; border-bottom: 1px dashed rgba(0,0,0,0.15); padding-bottom: 5px; }
.card-label { font-weight: 600; font-family: 'Inter', sans-serif; text-transform: lowercase; font-size: 0.8rem; width: 140px; color: rgba(0,0,0,0.6); }
.card-value { flex: 1; }
.imdb-btn { display: block; width: 100%; max-width: 180px; margin: 25px auto 0 auto; background: #f5c518; color: black; text-align: center; padding: 10px; text-decoration: none; border-radius: 4px; font-weight: bold; font-family: 'Inter', sans-serif; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 1px; }

.page-nav { display: flex; justify-content: space-between; margin-top: 50px; padding-top: 30px; border-top: 1px solid rgba(0,0,0,0.1); }
.nav-btn { color: var(--text-dark); text-decoration: none; font-weight: bold; font-size: 0.9rem; border: 1px solid var(--text-dark); padding: 8px 15px; border-radius: 4px; }
.nav-btn.hidden { visibility: hidden; }

.mobile-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
.mobile-tile { background: #1c2128; border: 1px solid var(--border); padding: 30px 10px; text-align: center; color: white; text-decoration: none; border-radius: 8px; font-weight: 600; }
.mobile-menu-btn { display: none; background: var(--accent); color: white; border: none; padding: 10px 20px; border-radius: 5px; font-weight: bold; cursor: pointer; }
#mobileMenuOverlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(13, 17, 23, 0.98); z-index: 5000; overflow-y: auto; padding: 60px 20px; }

@media (max-width: 1000px) {
    .nav-links { display: none; }
    .mobile-menu-btn { display: block; }
    .main-nav { height: 80px; }
    .nav-container { height: 80px; }
    .vault-logo { max-width: 130px; top: 15px; left: 15px; transform: rotate(-3deg); }
    .reading-room { margin: 20px auto; width: 92%; padding: 25px 15px; }
    .mobile-grid { grid-template-columns: 1fr; }
    .archival-card { width: 95%; padding: 20px; }
    .card-item { flex-direction: column; }
    .card-label { width: 100%; margin-bottom: 2px; }
}
"""

# --- 4. DATA-HANTERING ---
def read_filmlista():
    films = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                film_data = {key: row.get(key, '') for key in fieldnames}
                film_data['id'] = slugify(row.get('Titel', ''))
                films.append(film_data)
    return films

def process_manus():
    data_list = []
    used_slugs = set()
    seen_by_cat = {cat: set() for cat in CATEGORIES}

    def lagg_till_entry(entry):
        raw_title = entry['title'].strip()
        display_title = normalize_title_for_category(entry['cat'], raw_title)
        normalized_title = display_title.lower()
        if normalized_title in seen_by_cat.get(entry['cat'], set()):
            return
        entry['fname'] = make_unique_slug(slugify(raw_title), used_slugs)
        entry['title'] = display_title
        # Injicera SweGore-not om titeln matchar och ingen publikationsnot redan finns
        if entry['cat'] == 'Recensioner' and normalized_title in SWEGORE_TITLES:
            swegore_note = "<p><em>Publicerad på SweGore</em></p>"
            content = entry['content']
            if not any('publicerad' in p.lower() for p in content):
                entry['content'] = [swegore_note] + content
        # Injicera blogg-not om titeln matchar och ingen publikationsnot redan finns
        if entry['cat'] == 'Artiklar' and normalized_title in BLOG_TITLES:
            blog_note = "<p><em>Artikel från bloggarna Dawn of the Blog och Mondo Madness</em></p>"
            content = entry['content']
            if not any('dawn of the blog' in p.lower() or 'mondo madness' in p.lower() for p in content):
                entry['content'] = [blog_note] + content
        data_list.append(entry)
        seen_by_cat.setdefault(entry['cat'], set()).add(normalized_title)

    for cat in CATEGORIES:
        source_dirs = [os.path.join(BASE_INPUT, cat)] + EXTRA_CATEGORY_DIRS.get(cat, [])
        for source_dir in source_dirs:
            if not os.path.isdir(source_dir):
                continue

            files = []
            for name in os.listdir(source_dir):
                lower = name.lower()
                if name.startswith('~$'):
                    continue
                if lower.endswith(('.docx', '.txt', '.html', '.htm')):
                    files.append(name)

            files = sorted(files, key=lambda f: (extrahera_nummer(f), f.lower()))
            for file in files:
                path = os.path.join(source_dir, file)
                entries = parse_source_file(path, cat)
                for entry in entries:
                    lagg_till_entry(entry)

        # Fallback behövs just nu för legacy-intervjuer (t.ex. David Hess) som saknar källfil i Manus/interviews.
        if cat == 'Intervjuer':
            for entry in parse_category_page_entries(cat):
                lagg_till_entry(entry)

    ordered = []
    for cat in CATEGORIES:
        cat_items = [item for item in data_list if item['cat'] == cat]
        if cat in ALPHABETICAL_CATEGORIES:
            cat_items = sorted(cat_items, key=lambda i: i['title'].lower())
        ordered.extend(cat_items)
    data_list = ordered

    for i in data_list:
        i['content'] = markera_rubriker_i_html("".join(i['content']))
    return data_list

def process_pressklipp():
    files_list = []
    if os.path.exists(PDF_INPUT):
        files = [f for f in os.listdir(PDF_INPUT) if f.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png'))]
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            title = f.replace(ext, "").replace("_", " ")
            files_list.append({'title': title, 'filename': f, 'fname': slugify("press_" + title), 'is_img': ext != '.pdf'})
    return files_list

# --- 5. GENERERING ---
def write_site():
    site_data = process_manus()
    filmlista = read_filmlista()
    pressklipp = process_pressklipp()
    all_content_slugs = [d['fname'] for d in site_data] + [p['fname'] for p in pressklipp]
    
    nav_html = '<li class="nav-item"><a href="index.html">hem</a></li><li class="nav-item"><a href="arkiv.html">sök</a></li>'
    
    mobile_grid_html = '<a href="index.html" class="mobile-tile">hem</a><a href="arkiv.html" class="mobile-tile">sök arkiv</a>'

    nav_categories = [cat for cat in CATEGORIES if cat != 'Information om The Vault']
    if pressklipp:
        nav_categories.append('Pressklipp')
    nav_categories.append('Information om The Vault')

    for cat in nav_categories:
        items = [d for d in site_data if d['cat'] == cat] if cat != 'Pressklipp' else pressklipp
        if items:
            nav_html += f'<li class="nav-item"><a href="#">{cat.lower()} ▼</a><div class="dropdown-content">'
            for item in items: nav_html += f'<a href="{item["fname"]}">{item["title"][:35]}</a>'
            nav_html += '</div></li>'
            mobile_grid_html += f'<a href="cat_{slugify(cat)}" class="mobile-tile">{cat.lower()}</a>'

    if filmlista:
        nav_html += '<li class="nav-item"><a href="the_vault.html" onclick="return goToVault(event);">the vault</a></li>'
        mobile_grid_html += '<a href="the_vault.html" onclick="return goToVault(event);" class="mobile-tile">the vault</a>'

    master_template = """<!DOCTYPE html><html lang="sv"><head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[[SITENAME]]</title>
    <link rel="icon" type="image/png" href="logo.png"> <style>[[CSS]]</style>
    </head><body>
    <nav class="main-nav"><div class="nav-container"><img src="logo.png" onclick="handleLogoClick()" class="vault-logo"><ul class="nav-links">[[NAV]]</ul><button class="mobile-menu-btn" onclick="toggleMenu()">MENY</button></div></nav>
    <div id="mobileMenuOverlay"><span class="close-menu" onclick="toggleMenu()" style="position:absolute; top:20px; right:30px; font-size:40px; color:white; cursor:pointer;">&times;</span><div class="mobile-grid">[[MOBILE_NAV]]</div></div>
    
    <div id="filmCardOverlay"><div class="archival-card" onclick="event.stopPropagation()"><span class="card-close" onclick="closeCard()">&times;</span><h2 id="cardTitle"></h2><div id="cardContent" class="card-details"></div><a href="#" id="cardIMDB" target="_blank" class="imdb-btn">Visa på IMDB</a></div></div>

    [[BODY]]
    
    <script>
    function handleLogoClick() { if (window.innerWidth <= 1000) { toggleMenu(); } else { window.location.href = 'index.html'; } }
    function toggleMenu() { const m = document.getElementById('mobileMenuOverlay'); m.style.display = (m.style.display === 'block') ? 'none' : 'block'; document.body.style.overflow = (m.style.display === 'block') ? 'hidden' : 'auto'; }
    const VAULT_PASSWORD = [[VAULT_PASSWORD_JSON]];
    const VAULT_ACCESS_KEY = 'the_vault_access';

    function hasVaultAccess() { return sessionStorage.getItem(VAULT_ACCESS_KEY) === '1'; }
    function requestVaultAccess() {
        const entered = window.prompt('Lösenord för The Vault:');
        if (entered === null) return false;
        if (entered === VAULT_PASSWORD) {
            sessionStorage.setItem(VAULT_ACCESS_KEY, '1');
            return true;
        }
        window.alert('Fel lösenord.');
        return false;
    }
    function goToVault(event) {
        if (event) event.preventDefault();
        if (hasVaultAccess() || requestVaultAccess()) {
            window.location.href = 'the_vault.html';
            return true;
        }
        return false;
    }
    
    const filmDb = [[FILM_DB_JSON]];
    function openCard(id) {
        const f = filmDb.find(x => x.id === id); if(!f) return;
        document.getElementById("cardTitle").innerText = f.Titel;
        const keys = ['År', 'Regi', 'Land', 'Genre', 'Längd', 'Skådespelare', 'Skådespelare 2', 'Skådespelare 3', 'Producent', 'Musik', 'Specialeffekter'];
        let c = ""; keys.forEach(k => { if (f[k]) c += `<div class="card-item"><span class="card-label">${k}:</span> <span class="card-value">${f[k]}</span></div>`; });
        document.getElementById("cardContent").innerHTML = c;
        document.getElementById("cardIMDB").href = "https://www.imdb.com/find?q=" + encodeURIComponent(f.Titel + " " + (f.År || ""));
        document.getElementById("filmCardOverlay").style.display = "block";
        document.body.style.overflow = "hidden";
    }
    function closeCard() { document.getElementById("filmCardOverlay").style.display = "none"; document.body.style.overflow = "auto"; }
    document.getElementById("filmCardOverlay").onclick = closeCard;

    const allPages = [[SLUGS]];
    const currentPath = window.location.pathname.split('/').pop() || 'index.html';
    const currentIndex = allPages.indexOf(currentPath);
    window.onload = function() {
        if (currentPath === 'the_vault.html' && !(hasVaultAccess() || requestVaultAccess())) {
            window.location.href = 'index.html';
            return;
        }
        const p = document.getElementById('prevBtn'); const n = document.getElementById('nextBtn');
        if (currentIndex > 0 && p) { p.href = allPages[currentIndex-1]; p.classList.remove('hidden'); }
        if (currentIndex < allPages.length-1 && currentIndex !== -1 && n) { n.href = allPages[currentIndex+1]; n.classList.remove('hidden'); }
    };

    function filterVault() {
        const input = document.getElementById("vaultSearch").value.toLowerCase();
        const rows = document.querySelectorAll("#vaultTable tbody tr");
        rows.forEach(row => { row.style.display = row.getAttribute("data-search").includes(input) ? "" : "none"; });
    }

    const db = [[DB_JSON]];
    function doSearch() {
        const q = document.getElementById("searchInput").value.toLowerCase();
        const res = document.getElementById("results");
        res.innerHTML = ""; if(q.length < 2) return;
        const hits = db.filter(d => (d.title + d.content).toLowerCase().includes(q));
        if(hits.length === 0) { res.innerHTML = '<p style="color:white; text-align:center;">Inga resultat hittades.</p>'; } else {
            hits.forEach(d => {
                const cleanText = d.content.replace(/<[^>]*>?/gm, ' ');
                const snippet = cleanText.length > 160 ? cleanText.substring(0, 160) + "..." : cleanText;
                res.innerHTML += `<div style="background:rgba(255,255,255,0.95); padding:25px; margin-bottom:20px; border-radius:10px; box-shadow:0 8px 20px rgba(0,0,0,0.4);"><a href="${d.fname}" style="color:black; font-weight:bold; text-decoration:none; font-size:1.3rem; font-family:'Playfair Display', serif;">${d.title}</a><div style="color:var(--accent); font-size:0.75rem; margin-top:5px; font-weight:600; text-transform:uppercase; letter-spacing:1px;">${d.cat}</div><p style="color:#444; font-size:0.95rem; margin-top:10px; line-height:1.5;">${snippet}</p></div>`;
            });
        }
    }
    </script></body></html>"""

    def render(body, show_btns=True):
        t = master_template.replace("[[SITENAME]]", SITE_NAME).replace("[[CSS]]", CSS_CODE).replace("[[NAV]]", nav_html).replace("[[MOBILE_NAV]]", mobile_grid_html).replace("[[SLUGS]]", json.dumps(all_content_slugs)).replace("[[FILM_DB_JSON]]", json.dumps(filmlista)).replace("[[DB_JSON]]", json.dumps(site_data)).replace("[[VAULT_PASSWORD_JSON]]", json.dumps(VAULT_PASSWORD))
        nav_btns = '<div class="page-nav"><a id="prevBtn" class="nav-btn hidden">← föregående</a><a id="nextBtn" class="nav-btn hidden">nästa →</a></div>' if show_btns else ''
        return t.replace("[[BODY]]", body.replace("[[NAV_BTNS]]", nav_btns))

    for item in site_data:
        with open(item['fname'], "w", encoding="utf-8") as f: f.write(render(f'<div class="reading-room"><h1>{item["title"]}</h1><div class="content">{item["content"]}</div>[[NAV_BTNS]]</div>'))

    for p in pressklipp:
        with open(p['fname'], "w", encoding="utf-8") as f:
            path = f"{PDF_INPUT}/{p['filename']}"
            media = f'<img src="{path}" style="max-width:100%; cursor:zoom-in;">' if p['is_img'] else f'<embed src="{path}" type="application/pdf" style="width:100%; height:80vh;">'
            f.write(render(f'<div class="reading-room"><h1>{p["title"]}</h1>{media}[[NAV_BTNS]]</div>'))

    for cat in CATEGORIES + (['Pressklipp'] if pressklipp else []):
        items = [d for d in site_data if d['cat'] == cat] if cat != 'Pressklipp' else pressklipp
        if items:
            list_html = "".join([f'<div style="margin-bottom:15px; border-bottom:1px solid rgba(0,0,0,0.05); padding-bottom:5px;"><a href="{i["fname"]}" style="color:var(--text-dark); text-decoration:none; font-weight:600;">{i["title"]}</a></div>' for i in items])
            with open(f"cat_{slugify(cat)}", "w", encoding="utf-8") as f: f.write(render(f'<div class="reading-room"><h1>{cat.lower()}</h1>{list_html}[[NAV_BTNS]]</div>', show_btns=False))

    if filmlista:
        rows = "".join([f'<tr data-search="{(f["Titel"]+f["År"]+f.get("Regi","")).lower()}"><td><span class="film-title-link" onclick="openCard(\'{f["id"]}\')">{f["Titel"]}</span></td><td>{f["År"]}</td><td>{f.get("Regi","")}</td></tr>' for f in filmlista])
        vault_body = f'<div class="reading-room"><h1>the vault</h1><input type="text" id="vaultSearch" oninput="filterVault()" placeholder="Sök i listan..."><div style="overflow-x:auto;"><table class="film-table" id="vaultTable"><thead><tr><th>Titel</th><th>År</th><th>Regi</th></tr></thead><tbody>{rows}</tbody></table></div>[[NAV_BTNS]]</div>'
        with open("the_vault.html", "w", encoding="utf-8") as f: f.write(render(vault_body, show_btns=False))

    with open("arkiv.html", "w", encoding="utf-8") as f:
        f.write(render('<div class="reading-room" style="background:transparent;box-shadow:none;"><h2 style="color:white;text-align:center; font-family:\'Playfair Display\'; font-style:italic; font-size:3rem;">Sök i arkivet</h2><input type="text" id="searchInput" oninput="doSearch()" style="width:100%; padding:20px; border-radius:40px; border:none; font-size:1.2rem; box-shadow:0 10px 30px rgba(0,0,0,0.5);" placeholder="Sök artiklar, namn eller ämnen..."><div id="results" style="margin-top:40px;"></div>[[NAV_BTNS]]</div>', show_btns=False))
    
    with open("index.html", "w", encoding="utf-8") as f: f.write(render('<div style="height:60vh;"></div>[[NAV_BTNS]]', show_btns=False))

if __name__ == "__main__":
    write_site()
    print("✅ Uppdatering klar! Favicon är nu logo.png och sidan är redo för Vercel.")