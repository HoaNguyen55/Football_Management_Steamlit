import base64

import pandas as pd
import numpy as np
import sqlite3
from sqlite3 import Connection
import streamlit as st
from datetime import date, datetime
import os.path
import copy as cp
import re
import plotly.graph_objects as go


class main:
    def __init__(self):
        self.menu = ['Home', 'Hỏi Đáp', 'Biểu Đồ', 'Trợ Giúp']
        self.pos = ["Thủ Môn", "Hậu Vệ", 'Tiền Vệ', 'Tiền Đạo']
        self.club = ['Việt Nam', 'Nhật Bản', 'Saudi Arabia', 'Trung Quốc', 'Australia', 'Oman']
        self.removeOpt = ('Xóa tất cả', 'Xóa từng dòng')
        self.qaOpt = ('Tìm tên cầu thủ', 'Cầu thủ trẻ nhất', 'Vị trí và Câu lạc bộ')
        self.saveOpt = ('Lưu Biểu Đồ', 'Lưu Dữ Liệu')
        self.pos.sort()
        self.club.sort()
        self.df = None
        if 'ssDf' not in st.session_state:
            st.session_state.ssDf = self.df
        self.home()

    def home(self):
        with st.form(key='Form1'):
            choice = st.sidebar.selectbox("Menu", self.menu)
            # with st.sidebar:
            #     editBox = st.radio('Bật Tắt Sửa File', ('Tắt', 'Mở'))
            #     buttonAdd = st.form_submit_button('Thêm Dữ Liệu')
            #     buttonDrawChart = st.form_submit_button('Vẽ Biểu Đồ')

        if choice == self.menu[0]:  # Trang chủ
            st.title('Trang chủ')
            st.image("football-manager-champion.jpg")
            buttonOpenFile = st.file_uploader("Tải file dữ liệu", type=["db", "csv", "xlsx"])

            if st.checkbox("Bật tắt hiển thị dữ liệu"):
                if buttonOpenFile is not None:
                    st.info('Dữ liệu được thêm hoàn tất')
                    _, fileExtension = os.path.splitext(str(buttonOpenFile.name))
                    if fileExtension in ['.xlsx', '.xls']:
                        self.df = pd.read_excel(str(buttonOpenFile.name), engine='openpyxl')
                    elif fileExtension in ['.csv']:
                        self.df = pd.read_csv(str(buttonOpenFile.name), encoding='utf-8')
                    else:  # for *.db file
                        conn = self.get_connection(str(buttonOpenFile.name))
                        self.init_db(conn)
                        split_db_name = str(buttonOpenFile.name).split('.')
                        db_name = split_db_name[0]
                        self.df = pd.DataFrame(self.get_data(conn, db_name))
                elif 'ssDf' in st.session_state and st.session_state.ssDf is not None:
                    st.info('File dữ liệu đã được lưu trong bộ nhớ tạm')
                else:
                    st.info('Dữ liệu chưa được thêm')
                self.session_state_df(self.df)

            nameValue = st.text_input("Full Name", help='Nhập họ và tên cầu thủ')
            col1, col2 = st.columns(2)
            yearValue = col1.date_input('Date of Birth', help='Nhập ngày tháng năm sinh cầu thủ',
                                        min_value=datetime(1950, 1, 1), max_value=datetime.now())
            numValue = col2.number_input("Số Áo", min_value=1, format='%d', help='Nhập số áo cầu thủ')
            clubValue = col1.selectbox("Câu Lạc Bộ", tuple(self.club), help='Chọn câu lạc bộ cầu thủ đang tham gia')
            posValue = col2.selectbox("Vị Trí", tuple(self.pos), help='Chọn vị trí của cầu thủ')

            if nameValue != '' or len(nameValue) != 0:
                buttonSubmit = st.button('Submit')
                if buttonSubmit:
                    newYearValue = datetime.strptime(str(yearValue), '%Y-%m-%d').strftime('%d/%m/%Y')
                    lst = np.array([nameValue, newYearValue, posValue, clubValue, numValue])
                    self.importTable(lst)
                    st.success("Thêm dữ liệu cầu thủ <<< {} >>> hoàn tất".format(nameValue))
            else:
                st.warning('Người dùng cần nhập đầy đủ thông tin')

            boxRemove = col1.selectbox('Lựa Chọn', options=self.removeOpt)
            buttonRemove = col1.button('Xóa')
            if buttonRemove:
                if boxRemove == 'Xóa từng dòng':
                    pass
                else:
                    st.session_state.ssDf = st.session_state.ssDf[0:0]

            if self.df is not None:
                st.dataframe(st.session_state.ssDf)

            buttonSave = st.button('Lưu Dữ Liệu')
            if buttonSave:
                st.markdown(self.download_link(st.session_state.ssDf), unsafe_allow_html=True)
        elif choice == self.menu[1]:  # Hỏi đáp
            _newDf = None
            _copy_Df = None
            split_space_word = []
            st.title('Hỏi Đáp')
            self.check_database_exist()
            boxQa = st.selectbox('Lựa Chọn Câu Hỏi', options=self.qaOpt)
            st.markdown('*Lựa chọn cột hiển thị*')
            col = st.columns(5)
            filter_col1 = col[0].checkbox('Họ và Tên', True)
            filter_col2 = col[1].checkbox('Ngày Sinh', True)
            filter_col3 = col[2].checkbox('Vị Trí', True)
            filter_col4 = col[3].checkbox('Câu Lạc Bộ', True)
            filter_col5 = col[4].checkbox('Số Áo', True)
            col_filter_list = [filter_col1, filter_col2, filter_col3, filter_col4, filter_col5]

            if boxQa == self.qaOpt[0]:
                names = st.text_input('Nhập tên cầu thủ muốn tìm')  # Người dùng nhập 1 hoặc nhiều tên
                # và cách nhau bằng dấu phẩy
                optionSearch = st.radio('Cách tìm kiếm', ('Chính Xác', 'Tương Đối'), index=0)
                if st.session_state.ssDf is not None and len(names) > 0:
                    split_comma = names.split(',')
                    for word in split_comma:
                        word_list = re.findall(r"[\w']+", word)
                        split_space_word.extend(word_list)
                    _newDf = self.search_string(split_space_word, optionSearch)

            elif boxQa == self.qaOpt[1]:
                old_lst = st.slider('Nhập Tuổi', min_value=18, max_value=50, value=[18, 20], step=1)  # Nhập số tuổi
                # của cầu thủ
                if st.session_state.ssDf is not None and len(old_lst) > 0:
                    _newDf = self.search_number(old_lst)
            elif boxQa == self.qaOpt[2]:
                col1 = st.sidebar.selectbox("Vị Trí", self.pos)
                col2 = st.sidebar.selectbox("Câu Lạc Bộ", self.club)
                col_lst = [col1, col2]
                if st.session_state.ssDf is not None:
                    _newDf = self.search_col(col_lst)

            buttonQa = st.button('Trả Lời')
            if buttonQa:
                if _newDf is not None:
                    _newDf = self.filter_col(_newDf, col_filter_list)
                    import time
                    latest_iteration = st.empty()
                    bar = st.progress(0)
                    num = 10
                    for i in range(0, num + 1, 1):
                        latest_iteration.text(f'{num - i} seconds left')
                        bar.progress((100 // num) * i)
                        time.sleep(0.1)
                    st.dataframe(_newDf)
                else:
                    st.error('Không có dữ liệu để trả lời câu hỏi. Vui lòng kiểm tra lại thông tin nhập')
        elif choice == self.menu[2]:  # Biểu đồ
            st.title('Biểu Đồ')
            cp_df = cp.deepcopy(st.session_state.ssDf)
            self.check_database_exist()
            if cp_df is None:
                return

            num_club_dict = self.cal_string_club(cp_df['Câu Lạc Bộ'])
            num_pos_dict = self.cal_string_pos(cp_df['Câu Lạc Bộ'], num_club_dict, cp_df['Vị Trí'])
            #print(num_pos_dict.keys())
            chart_visual = st.sidebar.selectbox('Lựa chọn biểu đồ',
                                                ('Bar Chart', 'Pie Chart'))
            detail = st.sidebar.checkbox('Chi Tiết', help='Thể hiện chi tiết số lượng từng vị trí trong đội bóng')
            opt_club = self.club[:]
            opt_club.insert(0, 'Tất Cả')
            list_club_keys = list(num_club_dict.keys())
            list_club_val = list(num_club_dict.values())
            list_pos_of_club_keys = list(num_pos_dict.keys())
            list_pos_of_club_val = list(num_pos_dict.values())
            list_pos_of_club_in_keys = list(list_pos_of_club_val[0].keys())

            if chart_visual == 'Bar Chart':
                fig = go.Figure(data=[
                    go.Bar(name=list_club_keys[0],
                           x=[list_club_keys[0]],
                           y=[list_club_val[0]]),
                    go.Bar(name=list_club_keys[1],
                           x=[list_club_keys[1]],
                           y=[list_club_val[1]]),
                    go.Bar(name=list_club_keys[2],
                           x=[list_club_keys[2]],
                           y=[list_club_val[2]]),
                    go.Bar(name=list_club_keys[3],
                           x=[list_club_keys[3]],
                           y=[list_club_val[3]]),
                ]
                )
                # Change the bar mode
                fig.update_layout(title='Biểu Đồ Cột Thể Hiện Số Lượng Cầu Thủ Của Từng Đội Bóng World Cup 2021',
                                  barmode='group',
                                  xaxis_title="Các Quốc Gia Tham Gia World Cup 2022 Bảng A",
                                  yaxis_title="Số Lượng Cầu Thủ",
                                  font=dict(
                                      family="Courier New, monospace",
                                      size=15))
                x_axis_0 = [list_pos_of_club_keys[0],
                            list_pos_of_club_keys[1],
                            list_pos_of_club_keys[2],
                            list_pos_of_club_keys[3]]
                y_axis_0 = [list(list_pos_of_club_val[0].values())[0],
                            list(list_pos_of_club_val[1].values())[0],
                            list(list_pos_of_club_val[2].values())[0],
                            list(list_pos_of_club_val[3].values())[0]]
                y_axis_1 = [list(list_pos_of_club_val[0].values())[1],
                            list(list_pos_of_club_val[1].values())[1],
                            list(list_pos_of_club_val[2].values())[1],
                            list(list_pos_of_club_val[3].values())[1]]
                y_axis_2 = [list(list_pos_of_club_val[0].values())[2],
                            list(list_pos_of_club_val[1].values())[2],
                            list(list_pos_of_club_val[2].values())[2],
                            list(list_pos_of_club_val[3].values())[2]]
                y_axis_3 = [list(list_pos_of_club_val[0].values())[3],
                            list(list_pos_of_club_val[1].values())[3],
                            list(list_pos_of_club_val[2].values())[3],
                            list(list_pos_of_club_val[3].values())[3]]

                if detail:
                    fig = go.Figure(data=[
                        go.Bar(name=list_pos_of_club_in_keys[0],
                               x=x_axis_0,
                               y=y_axis_0),
                        go.Bar(name=list_pos_of_club_in_keys[1],
                               x=x_axis_0,
                               y=y_axis_1),
                        go.Bar(name=list_pos_of_club_in_keys[2],
                               x=x_axis_0,
                               y=y_axis_2),
                        go.Bar(name=list_pos_of_club_in_keys[3],
                               x=x_axis_0,
                               y=y_axis_3)])
                    #  Change the bar mode
                    fig.update_layout(title='Số Lượng Vị Trí Cầu Thủ Đội Bóng World Cup 2021',
                                      barmode='group',
                                      xaxis_title="Các Quốc Gia Tham Gia World Cup 2022 Bảng A",
                                      yaxis_title="Số Lượng Cầu Thủ",
                                      font=dict(
                                          family="Courier New, monospace",
                                          size=15)
                                      )
                st.write(fig)

        elif choice == self.menu[3]:  # Liên hệ
            st.title('Liên Hệ')
            self.info()

    @staticmethod
    def getList(inputDict):
        return list(inputDict.keys())

    def cal_string_pos(self, clubDf, clubdict, posLstDf):
        out_pos_dict = {}
        out_dict = {}
        clubdict_keylst = list(clubdict.keys())
        clubdict_vallst = list(clubdict.values())
        for i in range(len(posLstDf)):
            for j in range(len(posLstDf)):
                if posLstDf[i] == posLstDf[j]:
                    out_pos_dict[posLstDf[i]] = 0
                else:
                    pass
        pos_dict = self.getList(out_pos_dict)
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        for i in range(len(clubDf)):

            # print('i=', i)
            for j in range(len(clubdict_keylst)):
                print('result dict', clubdict_vallst[j])
                print('sum dict', sum(out_pos_dict.values()))

                # print('>> out_pos_dict', out_pos_dict)
                # print('>> out_dict', out_dict)
                # print('j', j)
                if clubDf[i] == clubdict_keylst[j]:
                    for k in range(len(pos_dict)):
                        if pos_dict[k] == posLstDf[i]:
                            out_pos_dict[pos_dict[k]] = out_pos_dict.get(pos_dict[k]) + 1
                    out_dict[clubdict_keylst[j]] = out_pos_dict
                    if sum(out_pos_dict.values()) == clubdict_vallst[j]:
                        out_pos_dict = out_pos_dict.fromkeys(out_pos_dict, 0)
        return out_dict

    def cal_string_club(self, inputClubLstDf):
        out_club_dict = {}
        for i in range(len(inputClubLstDf)):
            for j in range(len(inputClubLstDf)):
                if inputClubLstDf[i] == inputClubLstDf[j]:
                    out_club_dict[inputClubLstDf[i]] = 0
                else:
                    pass

        pos_dict = self.getList(out_club_dict)
        for i in range(len(inputClubLstDf)):
            for j in range(len(pos_dict)):
                if pos_dict[j] == inputClubLstDf[i]:
                    out_club_dict[pos_dict[j]] = out_club_dict.get(pos_dict[j]) + 1

        return out_club_dict

    @staticmethod
    def check_database_exist():
        if st.session_state.ssDf is not None:
            _copy_Df = cp.deepcopy(st.session_state.ssDf)
            st.dataframe(_copy_Df)
            col1, col2 = st.columns([4, 1])
            clearDB = col2.button('Clear dữ liệu')
            if clearDB:
                _copy_Df = _copy_Df[0:0]
                col1.warning('Dữ liệu chưa được nhập')
            else:
                col1.info('Dữ liệu đã được nhập')

    @staticmethod
    def search_col(col_list=None):
        cp_df = cp.deepcopy(st.session_state.ssDf)
        if col_list is not None:
            obj = cp_df[cp_df['Vị Trí'] == col_list[0]]
            obj = obj[obj['Câu Lạc Bộ'] == col_list[1]]
        return obj

    @staticmethod
    def filter_col(df, col_filter_list=None):
        show_names_lst = []
        if col_filter_list is not None:
            for i in range(len(col_filter_list)):
                if col_filter_list[i]:
                    show_names_lst.append(df.columns[i])
        obj = df[show_names_lst]
        return obj

    @staticmethod
    def session_state_df(dataframe):
        if dataframe is not None:
            st.session_state.ssDf = dataframe
        return st.dataframe(st.session_state.ssDf)

    def search_number(self, oldList):
        result = []
        today = date.today()
        currentYear = today.strftime('%Y')
        cp_df = cp.deepcopy(st.session_state.ssDf)
        for dateIdx in cp_df['Ngày Sinh']:
            date_transfer_df = datetime.strptime(dateIdx, '%d/%m/%Y')
            year_player = date_transfer_df.strftime('%Y')
            old_player = int(currentYear) - int(year_player)
            if oldList[0] <= int(old_player) <= oldList[1]:
                result.append(True)
            else:
                result.append(False)
        cp_df['result'] = result
        tuoiDf = cp_df[cp_df['result'] == True]
        obj = tuoiDf.drop(columns='result')
        return obj

    @staticmethod
    def search_string(word_list_name, option=0):
        cp_df = cp.deepcopy(st.session_state.ssDf)
        if option == 'Chính Xác':
            obj = cp_df[np.logical_and.reduce([cp_df['Họ và Tên'].str.contains(word) for word in word_list_name])]
        else:
            obj = cp_df[cp_df['Họ và Tên'].str.contains('|'.join(word_list_name))]

        return obj

    @staticmethod
    def rmvDuplicateValInLst(list_value):
        new_list = list(dict.fromkeys(list_value))
        return new_list

    def graph(self):
        pass

    @staticmethod
    def init_db(conn: Connection):
        conn.commit()

    @staticmethod
    def get_data(conn: Connection, db_name):
        db_select = "SELECT * FROM " + db_name
        df = pd.read_sql(db_select, con=conn)
        return df

    @staticmethod
    def get_connection(path: str):
        return sqlite3.connect(path, check_same_thread=False)

    @staticmethod
    def download_link(df):
        from io import BytesIO
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Sheet1', index=False)
        writer.save()
        val = output.getvalue()

        b64 = base64.b64encode(val)  # val looks like b'...'
        return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="database_file.xlsx"><input ' \
               f'type="button" value="Download File"></a>'

    @staticmethod
    def info():
        st.subheader('FOOTBALL MANAGER\n')
        st.code("Phần mềm quản lý cầu thủ đang trong giai đoạn thử nghiệm\n"
                "---------------------------------------------"
                "\nMọi chi tiết xin vui lòng liên hệ:"
                "\nThành viên dự án Football Manager:"
                "\n      Tên: Nguyễn Lê Minh Hòa"
                "\n           Trần Trung Lưu"
                "\n           Trần Huỳnh Quốc Vũ"
                "\n      SĐT: 0944 886 896")

    @staticmethod
    def importTable(lst):
        # Thêm vào database table
        st.session_state.ssDf.loc[-1] = lst
        st.session_state.ssDf.index += 1
        st.session_state.ssDf.sort_index(inplace=True)


if __name__ == '__main__':
    main()
