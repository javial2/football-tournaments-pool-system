def format_names(text=''):
    text = text.lower()
    text.replace(' ', '-')
    text.replace('á', 'a')
    text.replace('é', 'e')
    text.replace('í', 'i')
    text.replace('ó', 'o')
    text.replace('ú', 'u')
    
    return text

def printable_names(text=''):
    text = text.split('-')
    new_text = []
    for t in text:
        new_text.append(t[0].upper() + t[1:])
    return " ".join(new_text)