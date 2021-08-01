import pandas as pd
from pathlib import Path
import sqlite3
from sqlite3 import Connection
import streamlit as st




def main():
    menu = ['Home', 'File', 'Hỏi Đáp', 'Biểu Đồ', 'Trợ Giúp']
    pos = ["Thủ Môn", "Hậu Vệ", 'Tiền Vệ', 'Tiền Đạo']
    club = ['Việt Nam', 'Nhật Bản', 'Saudi Arabia', 'Trung Quốc', 'Australia', 'Oman']
    removeOpt = ('Xóa tất cả', 'Xóa từng dòng')
    qaOpt = ('Tất cả cầu thủ', 'Cầu thủ trẻ nhất', 'Vị trí của cầu thủ > 25 tuổi')
    saveOpt = ('Lưu Biểu Đồ', 'Lưu Dữ Liệu')
    pos.sort()
    club.sort()

    with st.form(key='Form1'):
        choice = st.sidebar.selectbox("Menu", menu)
        with st.sidebar:
            editBox = st.radio('Bật Tắt Sửa File', ('Tắt', 'Mở'))
            buttonAdd = st.form_submit_button('Thêm Dữ Liệu')
            buttonDrawChart = st.form_submit_button('Vẽ Biểu Đồ')

    if choice == 'Home':
        st.title('Home')
        st.image("football-manager-2021.jpg")
        buttonOpenFile = st.file_uploader("Upload Database File", type="db")
        if buttonOpenFile is not None:
            st.info('Database has imported completely')
            displayDb(str(buttonOpenFile.name))
        else:
            st.warning('Database has not imported yet')

        # col1, col2 = st.beta_columns([1, 2])
        col1, col2 = st.beta_columns(2)
        firstNameValue = col1.text_input("First Name", help='Nhập tên cầu thủ')
        lastNameValue = col2.text_input("Last Name", help='Nhập họ và tên lót cầu thủ')
        yearValue = col1.date_input('Date of Birth', help='Nhập ngày tháng năm sinh cầu thủ' )
        numValue = col2.number_input("Số Áo", min_value=1, format='%d', help='Nhập số áo cầu thủ')
        clubValue = col1.selectbox("Câu Lạc Bộ", tuple(club), help='Chọn câu lạc bộ cầu thủ đang tham gia')
        posValue = col2.selectbox("Vị Trí", tuple(pos), help='Chọn vị trí của cầu thủ')

        col1, col2, col3 = st.beta_columns(3)
        boxRemove = col1.selectbox('Lựa Chọn', options=removeOpt)
        buttonRemove = col1.button('Xóa')
        boxQa = col2.selectbox('Lựa Chọn', options=qaOpt)
        buttonQa = col2.button('Trả Lời')
        boxSave = col3.selectbox('Lựa Chọn', options=saveOpt)
        buttonSave = col3.button('Lưu')
        print(boxRemove, buttonRemove)
        print(boxQa, buttonQa)
        print(boxSave, buttonSave)

def displayDb(path):
    conn = get_connection(path)
    init_db(conn)
    display_data(conn)


def init_db(conn: Connection):
    conn.commit()


def build_sidebar(conn: Connection):
    st.sidebar.header("Configuration")
    input1 = st.sidebar.slider("Input 1", 0, 100)
    input2 = st.sidebar.slider("Input 2", 0, 100)
    if st.sidebar.button("Save to database"):
        conn.execute(f"INSERT INTO test (INPUT1, INPUT2) VALUES ({input1}, {input2})")
        conn.commit()


def display_data(conn: Connection):
    if st.checkbox("Display data in sqlite databse"):
        st.dataframe(get_data(conn))


def get_data(conn: Connection):
    df = pd.read_sql("SELECT * FROM player_db", con=conn)
    return df


def get_connection(path: str):
    return sqlite3.connect(path, check_same_thread=False)


if __name__ == '__main__':
    main()