TEXT_FIELDS = ['description', 'title', 'breadcrumb']
CATEGORIES = {
        'Botas y Botinetas': ['bota', 'botineta', 'borcego', 'abotinado'],
        'Sandalias y Ojotas': ['sandalia', 'ojota', 'chinela'],
        'Stilletos y Plataformas': ['stilleto', 'guillermina', 'plataforma'],
        'Chatitas': ['chatita', 'balerina'],
        'Mocasines y Vestir': ['mocasine', 'creeper', 'nautico', 'vestir', 'zapato', 'mocasin'],
        'Zuecos y Mules': ['zueco', 'mule'],
        'Casual': ['pantufla', 'alpargata', 'pancha'],
        'Zapatillas': ['zapatailla', 'urbana', 'running', 'botita', 'nautica']
}


def flatten_text(item):
    res = ''
    for field in TEXT_FIELDS:
        if field in item:
            if type(item[field]) is list:
                res += " " + " ".join(item[field])
            else:
                res += " " + item[field]
    return res.lower()

# Simply choose category that has the most sub-category mentiones in item text
def get_category(item):
    item_text = flatten_text(item)
    max_cat = 'Botas y Botinetas'
    max_cat_match = 0
    for cat, sub_cats in CATEGORIES.items():
        cat_match = item_text.count(cat.lower())
        for sub_cat in sub_cats:
            cat_match += item_text.count(sub_cat)
        if cat_match > max_cat_match:
            max_cat_match = cat_match
            max_cat = cat
    return max_cat

