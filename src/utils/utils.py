import gspread
from oauth2client.service_account import ServiceAccountCredentials

def format_names(text=''):
    text = text.lower()
    text.replace(' ', '-')
    text.replace('á', 'a')
    text.replace('é', 'e')
    text.replace('í', 'i')
    text.replace('ó', 'o')
    text.replace('ú', 'u')
    
    return text

def upload_rank_to_drive(rank_list, config = {}):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(config['credentials_filename'], scope)
    client = gspread.authorize(creds)

    spreadsheet = client.open_by_key(config['sheet_id'])
    worksheet = spreadsheet.sheet1

    i = 1
    j = 1
    rank_list.pop(0)
    for row in rank_list:
        worksheet.update_cell(i+1, j, row[0])
        worksheet.update_cell(i+1, j+1, row[1])
        worksheet.update_cell(i+1, j+2, row[2])
        i += 1