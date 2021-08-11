import base64

import pandas as pd
import numpy as np
import sqlite3
from sqlite3 import Connection
import streamlit as st
import datetime
import os.path
import copy as cp


def init_db(conn: Connection):
    conn.commit()


def build_sidebar(conn: Connection):
    st.sidebar.header("Configuration")
    input1 = st.sidebar.slider("Input 1", 0, 100)
    input2 = st.sidebar.slider("Input 2", 0, 100)
    if st.sidebar.button("Save to database"):
        conn.execute(f"INSERT INTO test (INPUT1, INPUT2) VALUES ({input1}, {input2})")
        conn.commit()


def get_data(conn: Connection):
    df = pd.read_sql("SELECT * FROM player_db", con=conn)
    return df


def get_connection(path: str):
    return sqlite3.connect(path, check_same_thread=False)


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


class main:
    def __init__(self):
        self.menu = ['Home', 'Hỏi Đáp', 'Biểu Đồ', 'Trợ Giúp']
        self.pos = ["Thủ Môn", "Hậu Vệ", 'Tiền Vệ', 'Tiền Đạo']
        self.club = ['Việt Nam', 'Nhật Bản', 'Saudi Arabia', 'Trung Quốc', 'Australia', 'Oman']
        self.removeOpt = ('Xóa tất cả', 'Xóa từng dòng')
        self.qaOpt = ('Tìm tên cầu thủ', 'Cầu thủ trẻ nhất', 'Vị trí của cầu thủ > 25 tuổi')
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
                        conn = self.displayDb(str(buttonOpenFile.name))
                        self.df = pd.DataFrame(get_data(conn))
                    print('ssDf' not in st.session_state)
                elif 'ssDf' in st.session_state:
                    st.info('File dữ liệu đã được lưu trong bộ nhớ tạm')
                else:
                    st.info('Dữ liệu chưa được thêm')
                self.session_state_df(self.df)

            nameValue = st.text_input("Full Name", help='Nhập họ và tên cầu thủ')
            col1, col2 = st.columns(2)
            yearValue = col1.date_input('Date of Birth', help='Nhập ngày tháng năm sinh cầu thủ',
                                        min_value=datetime.datetime(1950, 1, 1), max_value=datetime.datetime.now())
            numValue = col2.number_input("Số Áo", min_value=1, format='%d', help='Nhập số áo cầu thủ')
            clubValue = col1.selectbox("Câu Lạc Bộ", tuple(self.club), help='Chọn câu lạc bộ cầu thủ đang tham gia')
            posValue = col2.selectbox("Vị Trí", tuple(self.pos), help='Chọn vị trí của cầu thủ')

            if nameValue != '' or len(nameValue) != 0:
                buttonSubmit = st.button('Submit')
                if buttonSubmit:
                    newYearValue = datetime.datetime.strptime(str(yearValue), '%Y-%m-%d').strftime('%d/%m/%Y')
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
                st.markdown(download_link(st.session_state.ssDf), unsafe_allow_html=True)
        elif choice == self.menu[1]:  # Hỏi đáp
            import re
            _newDf = None
            _copy_Df = None
            split_space_word = []
            st.title('Hỏi Đáp')
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
            boxQa = st.selectbox('Lựa Chọn Câu Hỏi', options=self.qaOpt)

            if boxQa == self.qaOpt[0]:
                names = st.text_input('Nhập tên cầu thủ muốn tìm')  # Người dùng nhập 1 hoặc nhiều tên
                                                                    # và cách nhau bằng dấu phẩy
                optionSearch = st.radio('Cách tìm kiếm', ('Chính Xác', 'Tương Đối'), index=0)
                if st.session_state.ssDf is not None:
                    split_comma = names.split(',')
                    for word in split_comma:
                        word_list = re.findall(r"[\w']+", word)
                        split_space_word.extend(word_list)
                    _newDf = self.search_string(split_space_word, optionSearch)

            elif boxQa == self.qaOpt[1]:
                pass
                # tuoiBox, cancel = self.dialogBirthBox()
                # if not cancel:
                #     return None
                #
                # result = []
                # today = date.today()
                # yearCurrent = today.strftime('%Y')
                # tuoiDf = cp.deepcopy(self.df)
                #
                # for dateIdx in tuoiDf['Ngày Sinh']:
                #     date_transfer_df = datetime.strptime(dateIdx, '%d/%m/%Y')
                #     year_df = date_transfer_df.strftime('%Y')
                #     tuoiPlayer = int(yearCurrent) - int(year_df)
                #     if tuoiPlayer > tuoiBox:
                #         result.append(True)
                #     else:
                #         result.append(False)
                # tuoiDf['result'] = result
                # tuoiDf = tuoiDf[tuoiDf['result'] == True]
                # obj = tuoiDf.drop(columns='result')
                #
                # return obj
            elif boxQa == self.qaOpt[2]:
                pass
                # posTeamDf = cp.deepcopy(self.df)
                # self.dialog = inputPosClub(option=2)
                # if self.dialog.exec_():
                #     pos, club = self.dialog.getInputs()
                #     posTeamDf = posTeamDf[posTeamDf['Vị Trí'] == pos]
                #     posTeamDf = posTeamDf[posTeamDf['Câu Lạc Bộ'] == club]
                # else:
                #     return None
                # obj = posTeamDf
                # return obj

            buttonQa = st.button('Trả Lời')
            if buttonQa:
                if _newDf is not None:
                    st.dataframe(_newDf)
                else:
                    st.error('Không có dữ liệu để trả lời câu hỏi')
        elif choice == self.menu[2]:  # Biểu đồ
            st.title('Biểu Đồ')
            if self.df is None:
                st.warning('Chưa nhập bất cứ dữ liệu nào')
            else:
                st.info('Dữ liệu đã được nhập')
                st.dataframe(st.session_state.ssDf)
                buttonSave = st.button('Lưu Hình Ảnh')
                if buttonSave:
                    st.markdown(download_link(st.session_state.ssDf), unsafe_allow_html=True)
        elif choice == self.menu[3]:  # Liên hệ
            st.title('Liên Hệ')
            self.info()

    def session_state_df(self, dataframe):
        if dataframe is not None:
            st.session_state.ssDf = dataframe
        return st.dataframe(st.session_state.ssDf)

    def search_string(self, word_list_name, option=0):
        cp_df = cp.deepcopy(st.session_state.ssDf)
        if option == 'Chính Xác':
            obj = cp_df[np.logical_and.reduce([cp_df['Họ và Tên'].str.contains(word) for word in word_list_name])]
        else:
            obj = cp_df[cp_df['Họ và Tên'].str.contains('|'.join(word_list_name))]
        return obj

    def graph(self):
        pass

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

    @staticmethod
    def displayDb(path=None):
        if path is None:
            return
        conn = get_connection(path)
        init_db(conn)
        return conn


if __name__ == '__main__':
    main()
