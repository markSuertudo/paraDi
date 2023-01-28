import csv
from datetime import datetime


def open_csvfile(filename: str, data_base: list) -> bool:
    """
    :param filename: name of file
    :param data_base: empty list (or not empty :) for save
         values from CSV-file
    :return: if file will be reading return True
             else False (if file not existing or any error reading file
    :TODO: add checking error
    """
    with open(filename, "r", newline='') as csvfile:
        # csv.reader() -> return reader object
        row_data = csv.reader(csvfile, delimiter=";", quotechar='"')
        # Convert reader object to list
        data_base[:] = list(row_data)

    return True

def save_csvfile(filename: str, new_base: list) -> bool:
    with open("new_qw.csv", "w", newline='') as csvfile:
        newbase = csv.writer(csvfile, delimiter = ";", quoting = csv.QUOTE_NONNUMERIC, dialect='excel')
        newbase.writerows(new_base)
    return True

def reformat_database(data_base: list) -> bool:
    """
    :description: reformat database: reverse database
        and split date into parts (assume zero-index element is date)
    :param data_base:
    :return:
    """

    data_base.reverse()

    for indx in range(len(data_base)):
        dt = datetime.strptime(data_base[indx][0], "%d.%m.%Y %H:%M")
        data_base[indx] = data_base[indx][:1] \
            + [dt.year, dt.month, dt.day, dt.hour] \
            + data_base[indx][1:]

    return True

def create_newdatabase(data_base: list) -> list:

    newbase = []
    cur_index = 0
    cur_date = data_base[0][0][:10]
    hours = 1
    # в любом случае дойду получу исключение при выходе за границы массива
    # лучше его перехватить сейчас
    try:
        while True:
            for i in range(24):
                newbase[len(newbase):] = [[data_base[cur_index][0][:10] + ' {:02d}:00'.format(i)]\
                    + data_base[cur_index][1:4] + [i] + [hours]]
                hours += 1

            while cur_date == data_base[cur_index][0][:10]:
                cur_index += 1
            cur_date = data_base[cur_index][0][:10]

    except IndexError:
        # scale table
        for index, item in enumerate(newbase):
            newbase[index] = newbase[index][:6] + ['' for i in range(28)]

        # Like C проверил есть ли запись в data_base
        # если есть занес в new_base
        for i in range(len(newbase)):
            for x in range(len(data_base)):
                if newbase[i][0] == data_base[x][0]:
                    newbase[i] = newbase[i][:6] + data_base[x][5:]
                    break
        return newbase

def deleterows_notpresent(new_base, data_base) -> None:
    # Удалить последние строки не предтавленные в исходной таблице
    # я закладываюсь на то, что начальные начинаются с 00:00 часов
    i = -1
    while new_base[i][0] != data_base[-1][0]:
        i -= 1
    new_base[:] = new_base[:(i + 1)]  # one step back


def add_temperature(new_base) -> None:
    # initialize values
    save_index = 0
    save_value = 0.0
    temp_step = 0.0
    i = 0
    #for i in range(len(new_base)):
    while i < len(new_base):
        if new_base[i][6] != "":
            save_index = i
            save_value = float(new_base[i][6])
            i += 1

            # 2023-01-28 : Creo que errore esta aqui
            # salida de funciona en cinco cadenas de codigo abajo :)
            while i < len(new_base) and new_base[i][6] == "":
                i += 1
                print("WHILE I", i)

            if i >= len(new_base): # SALIDA esta aqui
                return i

            temp_step = abs(save_value - float(new_base[i][6]))

            print('INDEX', i, 'TEMP_STEP', temp_step, "Save Value", save_value, 'new_base',float(new_base[i][6]))
            temp_step = temp_step / float(i - save_index)
            print("AND NOW TEMP_STEP", temp_step)
            for x in range(1, i-save_index):
                if save_value < float(new_base[i][6]):
                    save_value = save_value + temp_step
                else :
                    save_value = save_value - temp_step
                new_base[save_index + x][6] = str(save_value + temp_step)
            i = save_index
        i += 1

def main( ) -> None:
    data_base = []
    open_csvfile("qw.csv", data_base)

    # I am know format of data base and so : get information, prepare database header
    # info = data_base[:6]
    header = data_base[6]
    # and prepare data
    data_base = data_base[7:]

    reformat_database(data_base)
    new_base = create_newdatabase(data_base)
    deleterows_notpresent(new_base, data_base)

    # 2023-01-28 Quizes que es tiempo para realizar "размазывание" por tabla
    add_temperature(new_base)

    # и наконец добавляю заголовок
    header = [header[0]] + ['year', 'month', 'day', 'hour','hour_y'] + header[1:]
    new_base.insert(0,header)
    # Фух! Кажется готово


    # можно сохранять (вынести и добавить проверку возможности записи)
    save_csvfile("new_qw.csv", new_base)


if __name__ == "__main__":
    main()
