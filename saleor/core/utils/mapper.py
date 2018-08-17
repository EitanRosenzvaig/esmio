TEXT_FIELDS = ['description', 'title', 'breadcrumb']
TOP_CATEGORIES = [
                'Balerinas',
                'Borcegos',
                'Botas',
                'Mocasines',
                'Ojotas',
                'Panchas',
                'Sandalias',
                'Zapatillas',
                'Zapatos Y Stilettos',
                'Zuecos',
                'Plataformas'
                ]

SUB_CATEGORIES = {
        'Balerinas': ['ballerina', 'slip','chatita', 'chata', 'balerina'],
        'Borcegos': ['borceg','acordonado'],
        'Botas': ['bota', 'botinet', 'texan', 'tejan', 'abotina', 'botita', 'charrit', 'ankle-boots', 'botín'],
        'Mocasines': ['casual', 'mocasin', 'oxford', 'acordonado', 'creeper', 'flat'],
        'Ojotas': ['ojot'],
        'Panchas': ['pancha', 'alpargat', 'espadrill', 'chancla', 'pantuf'],
        'Plataformas': ['plataformas'],
        'Sandalias' : ['sandal', 'atanad', 'roman'],
        'Zapatillas': ['zapatilla', 'urbana', 'sneak', 'nautic', 'runing'],
        'Zapatos Y Stilettos': ['zapato', 'noche', 'taco', 'vestir', 'stillet', 'escotado', 'semi abierto', 'fajon'],
        'Zuecos': ['zueco', 'mule', 'sueco', 'taco chino']
}


def flatten_text(item):
    res = ''
    for field in TEXT_FIELDS:
        if field in item and item[field] is not None:
            if type(item[field]) is list:
                res += " " + " ".join(item[field])
            else:
                res += " " + item[field]
    return res.lower()

# Simply choose category that has the most sub-category mentiones in item text
def get_category(item):
    item_text = flatten_text(item)
    max_cat = 'Zapatos Y Stilettos'
    max_cat_match = 0
    for top_cat in TOP_CATEGORIES:
        sub_cats = SUB_CATEGORIES[top_cat]
        cat_match = item_text.count(top_cat.lower())
        if cat_match > 0:
            return top_cat
        for sub_cat in sub_cats:
            cat_match += item_text.count(sub_cat)
        if cat_match > max_cat_match:
            max_cat_match = cat_match
            max_cat = top_cat
    return max_cat

