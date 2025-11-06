def save_result(file_name, *result):
    try:
        with open(file_name, encoding='utf-8', mode='w') as file:
            file.write('\n'.join(result))
        print(f'Результат сохранен в файл {file_name}')
    except Exception as e:
        print(f'Ошибка при сохранении результата в файл\n{e}')


def get_text_from_file(file_name):
    file_text = ''
    try:
        extension = file_name.split('.')[-1].lower()
        if extension == 'txt':
            with open(file_name) as file:
                file_text = '\n'.join([i.strip() for i in file.readlines()])

        elif extension == 'xlsx':
            file_text = {} if words else ''
            from openpyxl import load_workbook
            from openpyxl.utils import get_column_letter
            from openpyxl.styles.numbers import BUILTIN_FORMATS

            wb = load_workbook(file_name, data_only=True)
            sheet = wb.active
            for row in sheet.iter_rows():
                row_text = ''
                for cell in row:
                    if cell.value is not None and cell.value != 0:
                        if isinstance(cell.value, (int, float)):
                            fmt = cell.number_format
                            try:
                                row_text += str(cell.value)  if fmt == 'General' else format(cell.value, '.2f') + ' '
                            except:
                                row_text += str(cell.value) + ' '
                        else:
                            row_text += str(cell.value).lower().replace('\n', '') + ' '
                file_text += row_text + '\n'
        while '\n\n' in file_text:
            file_text = file_text.replace('\n\n', '\n')
    except Exception as e:
        print(f'Ошибка при чтении файла {file_name} \n{e}')
    return file_text


def get_text_from_file_by_words(file_name, words):
    file_text = ''
    try:
        file_text = {} if words else ''
        from openpyxl import load_workbook
        from openpyxl.utils import get_column_letter
        from openpyxl.styles.numbers import BUILTIN_FORMATS

        wb = load_workbook(file_name, data_only=True)
        sheet = wb.active
        for row in sheet.iter_rows():
            row_text = ''
            for cell in row:
                if cell.value is not None and cell.value != 0:
                    if isinstance(cell.value, (int, float)):
                        fmt = cell.number_format
                        try:
                            row_text += str(cell.value)  if fmt == 'General' else format(cell.value, '.2f') + ' '
                        except:
                            row_text += str(cell.value) + ' '
                    else:
                        row_text += str(cell.value).lower().replace('\n', '') + ' '
            if 'цена' in row_text or 'название' in row_text or 'артикул' in row_text or 'стоимость' in row_text:
                file_text['title'] = [row_text]
            for i in words:
                if i in row_text:
                    if i not in file_text:
                        file_text[i] = []
                    file_text[i].append(row_text)
        while '\n\n' in file_text:
            file_text = file_text.replace('\n\n', '\n')
    except Exception as e:
        print(f'Ошибка при чтении файла {file_name} \n{e}')
    return file_text
