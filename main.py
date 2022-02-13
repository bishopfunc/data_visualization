import json
import PySimpleGUI as sg
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pathlib


def merge(data1, data2):
    if (type(data1)!= type(None)) and (type(data2)!= type(None)):
        merged_data = pd.concat([data1,data2],axis=0)
        return merged_data
    else:
        return None

def read_file(filename):
    p_file = pathlib.Path(filename)
    if p_file.suffix == '.txt':
        return True
    elif filename == '':
        sg.popup('No File Input')
        return None
    else:
        sg.popup('File Type Error. Only *.txt is available.')
        return None

def cleaning(filename):
    if read_file(filename):
        raw_data = pd.read_table(filename ,skiprows=1,index_col=1, encoding='utf-8')
        raw_data = raw_data.dropna(how='all',axis=1)
        raw_data = raw_data.dropna(how='all')
        cleaned_data = raw_data.drop('Cycles')
        return cleaned_data
    else:
        return None

def read_dict(column_dict):
    try:
        column_dict = json.loads(column_dict)
        return column_dict
    except:
        sg.popup('Error Column Style')
        return None

def make_fig(cleaned_data, column_dict):
    column_dict = read_dict(column_dict)
    if (type(column_dict) != type(None)) and (type(cleaned_data) != type(None)):
        if (len(cleaned_data.columns) == sum(column_dict.values())):
            times = np.arange(len(cleaned_data.index))

            column_list = []
            for key in column_dict:
                N = column_dict[key]
                for i in range(N):
                    name = f'{key}_{i+1}'
                    column_list.append(name)
            
            cleaned_data.set_axis(column_list,axis=1,inplace=True)

            sns.set(style='ticks',font='sans-serif',font_scale=2)

            fig = plt.figure(figsize=(12,8))
            # plt.title(f'{date}_results',fontsize='30')
            cmap = ['Blue', 'Green', 'Orange', 'Red', 'Cyan','Yellow','Magenta' ,'Black']
            linestyle = ['solid','dashdot','dotted']

            count=0
            for i,key in enumerate(column_dict):
                for j in range(column_dict[key]):
                    name=column_list[count]
                    plt.plot(times,cleaned_data[name].astype('float').values,color=cmap[i%8],label=f'{name}',linestyle=linestyle[j%3])
                    count+=1
                
            plt.legend(bbox_to_anchor=(1.03, 1),loc=2,borderaxespad=0.,fontsize='12')
            plt.ylabel('Fluoresence')
            plt.xlabel('Time [min]')
            plt.subplots_adjust(right=0.7)
            return fig
        else: 
            sg.popup("Column Length is Different")
            return None
    

def plot(fig):
    if fig != None:
        plt.show(block=False)

def save(fig):
    if fig != None:
        filepath = sg.popup_get_file('save', save_as=True, file_types=(("PNG Files", "*.png"),))
        if filepath != None:
            plt.savefig(filepath)
            plt.close(fig)


def show_table(cleaned_data):
    if type(cleaned_data) != type(None):
        data = cleaned_data[1:].values.tolist()
        header_list = cleaned_data.columns.to_list()
        table_layout = [
            [sg.Table(values=data,
                    headings=header_list,
                    display_row_numbers=True,
                    auto_size_columns=False,
                    num_rows=min(25, len(data)))]
        ]
        table_window = sg.Window('Table', table_layout)
        envent, values = table_window.read()
        table_window.close() 
        # print(cleaned_data.shape)
        

default_dict = {"S30 21-6-1 GFPS1":1,
               "S30 21-6-1 sfGFP":3,
               "S30 21-1-2 GFPS1":1,
               "S30 21-1-2 sfGFP":1,
               "S30 miyachi sample GFPS1":1,
               "S30 miyachi sample sfGFP":1,
                }
default_dict = json.dumps(default_dict, indent=4)

tab1_layout =  [[sg.Text('Step1: Enter one *.txt file...')],
                [sg.Text('File 1', size=(8, 1)), sg.Input(key="tab1_file", size=(30,1)), sg.FileBrowse( file_types=(("Text Files", "*.txt"),))],
                [sg.Text(size=(8, 2), pad=(0,1))],
                [sg.Text('Step2: Enter well name and number...')],
                [sg.Multiline(key='tab1_column_dict', default_text=default_dict, size=(30, 10), font=('Arial',15)),],
                [sg.Button('ShowTable'), sg.Button('Plot'), sg.Button('Save', key='Save')]]   

tab2_layout = [[sg.Text('Step1: Enter two *.txt files...')],
                [sg.Text('File 1', size=(8, 1)), sg.Input(key="tab2_file1", size=(30,1),), sg.FileBrowse(file_types=(("Text Files", "*.txt"),))],
                [sg.Text('File 2', size=(8, 1)), sg.Input(key="tab2_file2", size=(30,1),), sg.FileBrowse(file_types=(("Text Files", "*.txt"),))],
                [sg.Text('Step2: Enter well name and number...')],
                [sg.Multiline(key='tab2_column_dict', default_text=default_dict, size=(30, 10), font=('Arial',15)),],
                [sg.Button('ShowTable1'), sg.Button('ShowTable2'), sg.Button('Plot1'), sg.Button('Plot2')],
                [sg.Button('ShowTableMerge'), sg.Button('PlotMerge'), sg.Button('Save', key='SaveMerge')]]   

layout = [[sg.TabGroup([[sg.Tab('1seg mode', tab1_layout), sg.Tab('2seg mode', tab2_layout)]])]]    

main_window = sg.Window('My window with tabs', layout, default_element_size=(30,1))    

while True:    
    event, values = main_window.read()  
    tab1_filename =  values['tab1_file']  
    tab2_filename1 =  values['tab2_file1']  
    tab2_filename2 =  values['tab2_file2']  
    tab1_column_dict =  values['tab1_column_dict']  
    tab2_column_dict =  values['tab2_column_dict']  

    print(f"envet: {event}")  
    print(f"values: {values}")  
    if event == sg.WIN_CLOSED:           # always,  always give a way out!    
        break  
    elif event == 'ShowTable':
        data = cleaning(tab1_filename)
        show_table(data)
    elif event == 'ShowTable1':
        data = cleaning(tab2_filename1)
        show_table(data)
    elif event == 'ShowTable2':
        data = cleaning(tab2_filename2)
        show_table(data)
    elif event == 'ShowTableMerge':
        data1 = cleaning(tab2_filename1)
        data2 = cleaning(tab2_filename2)
        merged_data = merge(data1, data2)        
        show_table(merged_data)
    elif event == 'Plot':
        data = cleaning(tab1_filename)
        _fig = make_fig(data, tab1_column_dict)
        plot(_fig)
    elif event == 'Plot1':
        data = cleaning(tab2_filename1)
        _fig = make_fig(data, tab2_column_dict)
        plot(_fig)
    elif event == 'Plot2':
        data = cleaning(tab2_filename2)
        _fig = make_fig(data, tab2_column_dict)
        plot(_fig)
    elif event == 'PlotMerge':
        data1 = cleaning(tab2_filename1)
        data2 = cleaning(tab2_filename2)
        merged_data = merge(data1, data2)
        _fig = make_fig(merged_data, tab2_column_dict)
        plot(_fig)
    elif event == 'Save':
        data = cleaning(tab1_filename)
        _fig = make_fig(data, tab1_column_dict)
        save(_fig)
    elif event == 'SaveMerge':
        data1 = cleaning(tab2_filename1)
        data2 = cleaning(tab2_filename2)
        merged_data = merge(data1, data2)
        _fig = make_fig(merged_data, tab2_column_dict)
        save(_fig)

