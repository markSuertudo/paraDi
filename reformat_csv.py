import csv
from datetime import datetime
import sys


def open_csvfile(filename: str, data_base: list) -> bool:
    """
    :param filename: name of file
    :param data_base: empty list (or not empty :) for save
         values from CSV-file
    :return: if file will be reading return True
             else False (if file not existing or any error reading file
    :TODO: add checking error
    """
    try:
        with open(filename, "r", newline='') as csvfile:
            # csv.reader() -> return reader object
            row_data = csv.reader(csvfile, delimiter=";", quotechar='"')
            # Convert reader object to list
            data_base[:] = list(row_data)
    except FileNotFoundError:
        print("File {} not found".format(filename))
        return False
    return True

def save_csvfile(filename: str, new_base: list) -> bool:
    with open("db_"+filename, "w", newline='') as csvfile:
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


def add_emptycells(new_base, column) -> None:
    # inicializar valores? Esta accion no es necesaria aqui
    # save_index, save_value, temp_step, i = 0, 0.0, 0.0, 0
    # save_value = 0.0
    # temp_step = 0.0
    i = 0

    while i < len(new_base):
        if new_base[i][column] != "":
            save_index = i
            save_value = float(new_base[i][column])
            i += 1

            # 2023-01-28 : Creo que errore esta aqui
            # salida de funciona en cinco cadenas de codigo abajo :)
            while i < len(new_base) and new_base[i][column] == "":
                i += 1

            if i >= len(new_base):
                return i
            # SALIDA DE FUNCION

            # cocinar/preparar nuevo paso
            temp_step = abs(save_value - float(new_base[i][column]))
            temp_step = temp_step / float(i - save_index)


            for x in range(1, i-save_index):
                if save_value < float(new_base[i][column]):
                    save_value = save_value + temp_step
                else :
                    save_value = save_value - temp_step

                new_base[save_index + x][column] = str(round(save_value, 2))


def main( ) -> None:
    if len(sys.argv) != 2 :
        print("Using: {} filename".format(sys.argv[0]))
        return 128
    else :
        filename = sys.argv[1]

    data_base = []
    if open_csvfile(filename, data_base):
        # I am know format of data base and so : get information, prepare database header
        # info = data_base[:6]
        header = data_base[6]
        # and prepare data
        data_base = data_base[7:]

        reformat_database(data_base)
        new_base = create_newdatabase(data_base)
        deleterows_notpresent(new_base, data_base)

        # 2023-01-29 16:23 Parece que es hora de realizar "untar" en la tabla
        #                  Añadir celdas celdas vacías
        add_emptycells(new_base, 6)
        add_emptycells(new_base, 7)
        add_emptycells(new_base, 8)
        add_emptycells(new_base, 9)
        add_emptycells(new_base, 10)

        # и наконец добавляю заголовок
        header = [header[0]] + ['year', 'month', 'day', 'hour','hour_y'] + header[1:]
        new_base.insert(0,header)


        # можно сохранять (вынести и добавить проверку возможности записи)
        save_csvfile(filename, new_base)


if __name__ == "__main__":
    main()
