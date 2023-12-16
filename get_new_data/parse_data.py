import os
import pandas as pd

directory = "data"

def get_data(directory, file_name):
    """
    Take data from json and return a pd dataframe.
    """
    file_path_json = os.path.join(directory, file_name)

    datetime = file_name.split('.')[0].split('_')[-2] + ' ' + ':'.join(file_name.split('.')[0].split('_')[-1].split('-'))

    data = pd.read_json(file_path_json)

    data['datetime'] = datetime
    data['datetime'] = pd.to_datetime(data['datetime'])


    data = data[['datetime','number', 'name', 'address', 'banking','bonus','bike_stands','available_bike_stands','available_bikes','status','last_update']]
    data['last_update'] = pd.to_datetime(data['last_update'], unit='ms')

    data['time_to_last_update'] = data['datetime'] - data['last_update']
    # print(data.dtypes)
    data['time_to_last_update'] = data['time_to_last_update'].apply(lambda x : x.total_seconds())

    return data

def get_data_for_all_jsons(directory):
    """
    Loop through all jsons.
    """
    files = os.listdir(directory)
    json_files = [file for file in files if file.endswith('.json')]

    # Sort JSON files by creation time
    json_files.sort(key=lambda x: os.path.getctime(os.path.join(directory, x)))

    data = pd.DataFrame()

    for json_file in json_files:
        new_data = get_data(directory, json_file)

        if len(data) == 0:
            data = new_data
        else:
            data = pd.concat([data, new_data], ignore_index=True)
    
    return data


if __name__=="__main__":
    # data = get_data(directory, file_name)

    data = get_data_for_all_jsons("data")
    data.to_csv("podatki_20231215.csv")


