def format_names(text=''):
    text = text.lower()
    text.replace(' ', '-')
    text.replace('á', 'a')
    text.replace('é', 'e')
    text.replace('í', 'i')
    text.replace('ó', 'o')
    text.replace('ú', 'u')
    
    return text