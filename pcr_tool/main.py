from curses import window
import json
import PySimpleGUI as sg
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pathlib



def save_png(filename):
    if filename != None:
        p_file = pathlib.Path(filename)
 
        if p_file.suffix == '.png':
            return True
        elif p_file.suffix == '.jpg':
            return True
        elif filename == '':
            sg.popup('ファイルが入力されていません!')
            return None
        else:
            sg.popup('ファイルの種類が間違っています!\n*.pngまたは*jpgファイルで保存して下さい!')
            return None

def read_file(filename):
    p_file = pathlib.Path(filename)
    if p_file.suffix == '.txt':
        return True
    elif filename == '':
        sg.popup('ファイルが入力されていません!')
        return None
    else:
        sg.popup('ファイルの種類が間違っています!\n*.txtファイルを開いて下さい!')
        return None

def cleaning(filename):
    if read_file(filename):
        cleaned_data = pd.read_table(filename ,skiprows=8, encoding='utf-8')
        return cleaned_data
    else:
        return None

def read_dict(column_dict):
    try:
        column_dict = json.loads(column_dict)
        return column_dict
    except:
        sg.popup(
            'Well情報のフォーマットが間違っています！\n'
            '行末に余計な(,)がないか、("")と({})が抜けてないか確認しましょう。'
            )
        return None

def check_date(date):
    if date:
        return date
    else:
        sg.popup('日付が入力されていません！')
        return None

def make_fig(cleaned_data, column_dict, date):
    date = check_date(date)
    title = f'{date}_results'
    column_dict = read_dict(column_dict)
    if (not isinstance(column_dict, type(None))) and (not isinstance(cleaned_data, type(None))) and(not isinstance(date, type(None))):
            fig = plt.figure(figsize=(12,8))
            plt.subplots_adjust(wspace=0.4, hspace=0.6, left=0.1, right=0.7 , bottom=0.2, top=0.9)
            ax1 = fig.add_subplot(1,2,1)
            ax2 = fig.add_subplot(1,2,2)
            ax1.set_title(f'{date} (SYBR)',fontsize='30')
            ax1.set_xlabel("Time[min]")

            ax2.set_title(f'{date} (ROX)',fontsize='30')
            ax2.set_xlabel("Time[min]")

            cmap = ['Blue', 'Green', 'Orange', 'Red','Cyan', 'Yellow','Magenta' ,'Black']
            linestyle = ['solid','dashdot','dotted']

            count=0
            for i,key in enumerate(column_dict.keys()):
                for j,well in enumerate(column_dict[key]):
                    name=f"{key}_{well}"
                    tmp_data = data[data["Well"]==well] 
                    times = tmp_data["Cycle"].values
                    
                    sybr = tmp_data["SYBR"].values
                    rox = tmp_data["ROX"].values
                    ax1.plot(times,sybr,color=cmap[i%8],label=f'{name}',linestyle=linestyle[j%3])
                    ax2.plot(times,rox,color=cmap[i%8],label=f'{name}',linestyle=linestyle[j%3])
                    count+=1
                    
            plt.legend(bbox_to_anchor=(1.03, 1),loc=2,borderaxespad=0.1,fontsize='8')
            #plt.savefig(f'{date}_result')
            return fig

def make_fig_error(cleaned_data, column_dict, date):
    date = check_date(date)
    title = f'{date}_results'
    column_dict = read_dict(column_dict)
    if (not isinstance(column_dict, type(None))) and (not isinstance(cleaned_data, type(None))) and(not isinstance(date, type(None))):
        DIV=4

        fig =plt.figure(figsize=(6,7.5))
        for i,key in enumerate(column_dict.keys()):
            for j,well in enumerate(column_dict[key]):
                tmp_data = data[data["Well"]==well] 
                times = tmp_data["Cycle"].values

        time_points=np.linspace(0,len(times),num=DIV+1)
        time_points[0]=1

        for i,key in enumerate(column_dict.keys()):
            ini_well = column_dict[key][0]
            tmp_data = data[data["Well"]==ini_well] 
            times = tmp_data["Cycle"].values
                
            
            means =[]
            sems = []

            for t in time_points:
                ts = data[data["Cycle"]==t]
                ts.set_index("Well",inplace=True)
                x = ts.loc[column_dict[key]]["SYBR"]
                sems.append(x.sem()) #標準誤差
                means.append(x.mean())
            
            plt.plot(time_points,means,label=f"{key}")
            plt.errorbar(time_points,means,yerr=sems,fmt="ko",ecolor="black",capsize=4)

            plt.xlabel("Time[min]")
            plt.legend(bbox_to_anchor=(1.03, 1),loc=2,borderaxespad=0.,fontsize='12')
            plt.tight_layout()
            #plt.savefig(f'{date}_error')
            return fig

def plot(fig):
    if fig != None:
        plt.show(block=False)

def save(fig):
    if fig != None:
        filepath = sg.popup_get_file('ファイルの保存先を選択して下さい。\n*.pngファイルで保存して下さい!', save_as=True, file_types=(png_file_types,))
        if save_png(filepath):
            plt.savefig(filepath)
            plt.close(fig)
            sg.popup("ファイルの保存が成功しました!")


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
        table_window = sg.Window(f'Size: {cleaned_data.shape}', table_layout)
        envent, values = table_window.read()
        table_window.close() 

def redo(event, text):    
    try:    
        text.edit_redo()
    except:
        pass     

default_dict = {
  "fluorecein":["B3","B4","B5","B6","B7","B8","B9","B10"],
  "AtzR:S12=3:7":["C3","C4","C5"],
  "AtzR:S12=3:7_neg":["C6","C7","C8"],
  "4:6":["C9","C10","D3"],
  "4:6_neg":["D4","D5","D6"],
  "5:5":["D7","D8","D9"],
  "5:5_neg":["D10","E3","E4"],
  "6:4":["E5","E6","E7"],
  "6:4_neg":["E8","E9","E10"],
  "7:3":["F3","F4","F5"],
  "7:3_neg":["F6","F7","F8"]
}
default_dict = json.dumps(default_dict, indent=4)

basic_font = ('Arial',15, 'bold')
multiline_font = ('Arial',20)
multiline_size = (30, 10)
inline_text_size = (40, 2)
inline_text_color = 'blue'
basic_text_size = (8, 1)
txt_file_types = ("Text Files", "*.txt")
png_file_types = ("PNG Files", "*.png")

step1_text = 'Step1: *.txtファイルを開いて下さい。\n\
            保存するグラフの日付を入力して下さい。'
step2_text =  'Step2: 実験条件と対応するwellを"condition":["B1","B2","B3"] のように書いてください。\nエラーバー表示してほしい場合下のチェックボックスにチェックを入れてください。'

def make_text(text, size=basic_text_size, pad=None, color=None):
    return sg.Text(text=text, size=size, pad=pad, font=basic_font, text_color=color)


def make_button(text, key=None):
    return sg.Button(button_text=text, font=basic_font, key=key)

tab1_layout =  [[make_text(step1_text, size=inline_text_size, color=inline_text_color)],
                [make_text('File'), sg.Input(key="tab1_file", size=(35,4)), sg.FileBrowse('開く', file_types=(txt_file_types,))],
                [make_text('ErrorBar'), sg.Checkbox("", default=False, key="checkbox",  enable_events=True)],
                [make_text('Date'), sg.Input(key="tab1_date", size=(10,4))],
                [make_text(step2_text, size=(40, 4), color=inline_text_color)],
                [sg.Multiline(key='tab1_column_dict', default_text=default_dict, size=multiline_size, font=multiline_font),],
                [make_button('Table'), make_button('Plot'), make_button('Save'), make_button('Plot ErrorBar'), make_button('Save ErrorBar')]]   


layout = [[sg.TabGroup([[sg.Tab('PCR Tool', tab1_layout, font=basic_font)]])]]    


main_window = sg.Window('Igem PCR Tool Tool', layout, finalize=True)
multiline1 = main_window["tab1_column_dict"].Widget 
multiline1.configure(undo=True)
multiline1.bind("<Control-Key-Y>", lambda event, text = multiline1: redo(event, text)) 
multiline1.bind("<Control-Shift-Key-Z>", lambda event, text = multiline1: redo(event, text)) 
multiline1.bind("<Command-Shift-Key-Z>", lambda event, text = multiline1: redo(event, text)) 

toggle = False
main_window['Plot ErrorBar'].update(visible=False)
main_window['Save ErrorBar'].update(visible=False)   
while True:    
    event, values = main_window.read()  
    if values != None:
        tab1_filename =  values['tab1_file']  
        tab1_column_dict =  values['tab1_column_dict']  
        date1 = values['tab1_date']    

    if event == sg.WIN_CLOSED: 
        break

    elif event == 'Table':
        data = cleaning(tab1_filename)
        show_table(data)
    elif event == 'Plot':
        data = cleaning(tab1_filename)
        _fig = make_fig(data, tab1_column_dict, date1)
        plot(_fig)
    elif event == 'Plot ErrorBar':
        data = cleaning(tab1_filename)
        _fig = make_fig_error(data, tab1_column_dict, date1)
        plot(_fig)
    elif event == 'Save':
        data = cleaning(tab1_filename)
        _fig = make_fig(data, tab1_column_dict, date1)
        save(_fig)
    elif event == 'Save ErrorBar':
        data = cleaning(tab1_filename)
        _fig = make_fig_error(data, tab1_column_dict, date1)
        save(_fig)
    
    if event == 'checkbox':
        toggle = not toggle
    
    if toggle:
        main_window['Plot ErrorBar'].update(visible=True)
        main_window['Save ErrorBar'].update(visible=True)
    else:
        main_window['Plot ErrorBar'].update(visible=False)
        main_window['Save ErrorBar'].update(visible=False)    
