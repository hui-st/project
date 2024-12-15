# C093073 김정태
# 배포링크: 
import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import folium
import warnings
from streamlit_folium import st_folium
warnings.filterwarnings('ignore')

# 페이지 설정
st.set_page_config(
    page_title = '2023 서울시 물가 데이터_EDA', # 페이지 타이틀
    page_icon = '🛒', # 페이지 아이콘
    layout = 'wide' # 레이아웃을 넓게 설정
)


# 타이틀 텍스트 출력
st.title('**🛒2023 서울시 전통시장 생필품/농수축산물 데이터**')
st.write('### ℹ️ EDA')
# 데이터 출처 표시
st.caption('출처(https://data.seoul.go.kr/dataList/OA-1170/S/1/datasetView.do#)')
# Strimlit 버전 출력
st.write('Streamlit 버전: ', st.__version__)


# 서울시 지도 데이터 로드
df = gpd.read_file("https://raw.githubusercontent.com/hui-st/project/refs/heads/main/df.geojson?raw=true")
df.plot()

# 서울시 전통시장 생필품/농수축산물 가격 정보 데이터 로드
# CSV 파일 읽기
a = pd.read_csv('https://github.com/hui-st/project/blob/main/market.csv?raw=true')
# '년도-월' 기준으로 정렬
a = a.sort_values(by='년도-월')

# 사이드바 설정
st.sidebar.header('데이터 선택창')

# 품목 선택바
gro = st.sidebar.multiselect('품목 선택(복수 선택 가능)', a['품목 이름'].unique())
if not gro:
    a_gro = a.copy() # 전체 선택
else:
    a_gro = a[a['품목 이름'].isin(gro)] # 선택만 필터링

# 월 선택바
mon = st.sidebar.multiselect('월 선택(복수 선택 가능)', a_gro['년도-월'].unique())
if not mon:
    a_mon = a_gro.copy() # 전체 선택
else:
    a_mon = a_gro[a_gro['년도-월'].isin(mon)] # 선택만 필터링

# 시장 선택바
m = st.sidebar.multiselect('시장 선택(복수 선택 가능)', a_mon['시장/마트 이름'].unique())
if not m:
    a_m = a_mon.copy() # 전체 선택
else:
    a_m = a_mon[a_mon['시장/마트 이름'].isin(m)] # 선택만 필터링

# 필터링이 완료된 데이터프레임
filter_df = a_m

st.write('')# 한 칸 띄기
st.write('## 𝄜 필터링된 데이터프레임')

# 스타일링 함수 정의
def highlight_max_min(df):
    # 가격(원) 컬럼에서 가장 높은 값과 가장 낮은 값 찾기
    max_price = df.groupby('품목 이름')['가격(원)'].transform('max')
    min_price = df.groupby('품목 이름')['가격(원)'].transform('min')
    
     # 각 행에 대해 스타일 적용
    def apply_style(row):
        if row['가격(원)'] == max_price[row.name]:
            return ['background-color: red'] * len(row)  # 해당 행의 모든 열을 빨간색 배경으로 변경
        elif row['가격(원)'] == min_price[row.name]:
            return ['background-color: lightgreen'] * len(row) # 해당 행의 모든 열을 연두색 배경으로 변경
        else:
            return [''] * len(row)  # 기본 스타일

    # 각 행에 스타일 적용
    return df.style.apply(apply_style, axis=1)

filtered_df = filter_df.tail(50000) # 처음 출력되는 범위 제한(로딩이 너무 길어서 제한)
pd.set_option('styler.render.max_elements', 275545)  # 스타일링 범위 확대

# 체크박스로 데이터프레임 모드 설정정
if st.checkbox('품목별 높은 가격과 낮은 가격 표시하기'):
    st.dataframe(highlight_max_min(filtered_df[['년도-월', '시장/마트 이름', '자치구 이름', '품목 이름', '가격(원)']]), use_container_width=True)# st.dataframe을 사용하여 스타일 적용된 데이터프레임 출력
else :
    st.dataframe(filter_df[['년도-월', '시장/마트 이름', '자치구 이름', '품목 이름', '가격(원)']], use_container_width=True)




st.divider() # 구분선
st.write('## 데이터 시각화')
st.write('')
######################################################################################(필터링된 데이터를 시각화를 위해 가공)
# '자치구 이름'과 '년도-월' 기준으로 가격 평균 계산 (월별 비교 시각화)
def monthly_mean(df):

    grouped = df.groupby(['자치구 이름', '년도-월'])['가격(원)'].mean().reset_index()
    grouped.columns = ['자치구 이름', '년도-월', '가격 평균']
    return grouped

# '자치구 이름'별 가격 평균 계산 (지도 시각화)
def overall_mean(df):

    grouped = df.groupby('자치구 이름')['가격 평균'].mean().reset_index()
    grouped.columns = ['자치구 이름', '가격 평균']
    return grouped

# '품목 이름'과 '년도-월' 기준으로 가격 평균 계산
def by_item_mean(df):
    grouped = df.groupby(['품목 이름', '년도-월'])['가격(원)'].mean().reset_index()
    grouped.columns = ['품목 이름', '년도-월','가격 평균']
    return grouped


# '시장/마트 이름'과 '년도-월' 기준으로 가격 평균 계산
def by_month_mean(df):
    grouped = df.groupby(['시장/마트 이름','년도-월'])['가격(원)'].mean().reset_index()
    grouped.columns = ['시장/마트 이름', '년도-월','가격 평균']
    return grouped


######################################################################################
#화면을 2개의 컬럼으로 분류
col1, col2 = st.columns(2)
# 품목별 가격 평균을 년도-월별로 시각화 - col1에 표시
with col1:
    # 품목별 평균 가격 (년도-월별) 계산
    df_by_item = by_item_mean(filter_df)

    # Plotly로 막대 그래프 생성 (년도-월별로 facet 분리)
    fig = px.bar(df_by_item, 
                 x='품목 이름',  # x축을 '품목 이름'으로 설정
                 y='가격 평균',  # y축을 '가격 평균'으로 설정
                 color='품목 이름',  # 색상은 품목 이름별로 다르게 설정
                 title='📌 품목별 가격 평균 (월별)',
                 labels={'품목 이름': '품목 이름', '가격 평균': '가격', '년도-월': '년도-월'},
                 facet_col='년도-월',  # facet_col을 사용하여 '년도-월'별로 분리
                 facet_col_wrap=2,  # 한 행에 3개의 그래프를 표시
                 category_orders={'년도-월': sorted(df_by_item['년도-월'].unique())},  # 년도-월별로 정렬
                 color_continuous_scale='Rainbow')# 색상
    
    # fig.update_layout(xaxis_tickangle=45)  # x축 레이블 각도 조정
    fig.update_layout(showlegend=False)  # 범례 숨기기

    # Streamlit에 Plotly 차트 출력
    st.plotly_chart(fig)

    

# 시장별 평균 가격(어느 시장에서 장을 보는 것이 저렴)
with col2:# '시장/마트 이름'을 인덱스로, '년도-월'을 열로 하는 피벗 테이블 생성
    # '년도-월' 기준으로 가격 평균 계산
    df_by_month = by_month_mean(filter_df)

    df_pivot = df_by_month.pivot(index='시장/마트 이름', columns='년도-월', values='가격 평균')
    # 히트맵 생성
    fig = px.imshow(df_pivot,
                labels=dict(x="년도-월", y="시장/마트 이름", color="가격 평균"),
                title="📌 월별 가격 평균 (시장별)",
                color_continuous_scale='Reds') # 색상상
     # Streamlit에 Plotly 차트 출력
    st.plotly_chart(fig)
##########################################################################################
# Choropleth 지도 생성(가격 평균)
def create_choropleth_map(df, geo_data):

    # 지도 중심 (서울 시청 좌표)
    center = [37.566826004661, 126.978652258309]
    
    # 지도 생성
    m = folium.Map(
        location=center,  # 지도 중심
        zoom_start=10.5,  # 확대 정도
    )
    
    # Choropleth 레이어 생성 및 지도에 추가
    folium.Choropleth(
        geo_data=geo_data,  # GeoJSON 데이터
        data=df,  # 데이터프레임
        columns=['자치구 이름', '가격 평균'],  # 데이터프레임 컬럼
        key_on='feature.properties.자치구 이름',  # GeoJSON의 key와 매핑
        fill_color='Reds',  # 색상
        fill_opacity=0.7,  # 채우기 투명도
        line_opacity=0.2,  # 경계선 투명도
        legend_name='가격 평균'  # 범례 이름
    ).add_to(m)
    
    return m

# 월별 평균 계산
monthly_avg = monthly_mean(filter_df)

# 자치구별 평균 계산
overall_avg = overall_mean(monthly_avg)

# Choropleth 지도 생성
m = create_choropleth_map(overall_avg, df)


# 지도 출력
st.subheader('🗺️ 구기준 품목 평균 가격 지도 시각화')
st_folium(m, use_container_width=True)  # folium 그래프를 페이지 사이즈에 맞춤

