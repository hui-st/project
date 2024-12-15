import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings('ignore')

# 페이지 설정
st.set_page_config(
    page_title = '2023 서울시 물가 데이터_EDA', # 페이지 타이틀
    page_icon = '🛒', # 페이지 아이콘
    layout = 'wide' # 레이아웃을 넓게 설정
)


# 타이틀 텍스트 출력
st.title('**🛒서울시 소비자 물가 지수 데이터**')
st.write('### ℹ️ EDA')
# 데이터 출처 표시
st.caption('출처(https://data.seoul.go.kr/dataList/135/S/2/datasetView.do#)')
# Strimlit 버전 출력
st.write('Streamlit 버전: ', st.__version__) 
# CSV 파일 읽기
a2 = pd.read_csv('https://raw.githubusercontent.com/hui-st/project/refs/heads/main/%EC%86%8C%EB%B9%84%EC%9E%90%EB%AC%BC%EA%B0%80%EC%A7%80%EC%88%98(%EC%A3%BC%EC%9A%94%ED%92%88%EB%AA%A9%EB%B3%84)_20241215013822.csv?raw=true')
with st.expander('소비자물가지수 데이터 보기'): # 확장창
    st.dataframe(a2, use_container_width=True)

# 서울시 전통시장 생필품/농수축산물 가격 정보 데이터 로드
# CSV 파일 읽기
a = pd.read_csv('https://github.com/hui-st/project/blob/main/market.csv?raw=true')
# '년도-월' 기준으로 정렬
a = a.sort_values(by='년도-월')


# 사이드바 설정
st.sidebar.header('데이터 선택창')

# 품목 선택바(소비자물가지수)
gro2 = st.sidebar.selectbox('품목 선택', a2['주요품목별(1)'].unique())

if gro2 == '':
    a_gro2 = a2.copy()  # 전체 선택
else:
    a_gro2 = a2[a2['주요품목별(1)'] == gro2]  # 선택한 품목만 필터링

# 품목 선택바(전통시장)
gro = st.sidebar.selectbox('품목 선택', a['품목 이름'].unique())

if gro == '':
    a_gro = a.copy()  # 전체 선택
else:
    a_gro = a[a['품목 이름'] == gro]  # 선택한 품목만 필터링

####################################################################################(필터링된 데이터를 시각화를 위해 가공)
# '품목 이름'과 '년도-월' 기준으로 가격 평균 계산
def by_item_mean(df):
    grouped = df.groupby(['품목 이름', '년도-월'])['가격(원)'].mean().reset_index()
    grouped.columns = ['품목 이름', '년도-월','가격 평균']
    return grouped
####################################################################################
st.divider() # 구분선
# 시계열 분석
st.header('📈 소비자물가지수와 평균가격 시계열 분석 비교')
st.write('### 소비자물가지수: 소비자가 구입하는 상품과 서비스의 가격변동을 측정하기 위한 지표')

# 데이터 변환 (wide -> long 포맷으로 변환 - 아래로 길게 컬럼과 값을 변형)
a_gro2_long = a_gro2.melt(id_vars='주요품목별(1)', var_name='월', value_name='값')

# 시계열 그래프 생성
fig = px.line(
    a_gro2_long,
    x='월', # x축
    y='값', # y축
    color='주요품목별(1)', # 품목별 색상 구분
    title='✨ 품목별 월별 시계열 그래프(소비자물가지수)',
    labels={'값': '값', '월': '월'},
    markers=True # 마커 표시
)

# 그래프 레이아웃 업데이트
fig.update_layout(
    xaxis_title='월',
    yaxis_title='값',
    xaxis=dict(tickmode='linear'), # 균등한 간격으로 표기
    template='plotly_white'
)

# Streamlit에 그래프 출력
st.plotly_chart(fig)

# 품목별 평균 가격 (년도-월별) 계산
monthly_avg_df = by_item_mean(a_gro)

# 3. 시계열 그래프 생성
fig = px.line(
    monthly_avg_df,
    x='년도-월',             # X축: '년도-월'
    y='가격 평균',           # Y축: '가격 평균'
    color='품목 이름',        # 품목별로 선 색상 구분
    title="✨ 품목별 월별 평균 가격 시계열 그래프(평균 가격)",
    labels={'가격 평균': '가격 (원)', '년도-월': '월'},
    markers=True # 마커 표시
)

# 그래프 레이아웃 조정
fig.update_layout(
    xaxis_title="월",
    yaxis_title="가격 (원)",
    legend_title="품목 이름",
    xaxis=dict(tickformat="%Y-%m"),  # X축 형식 지정 (년도-월 형식)
    #xaxis=dict(tickmode='linear'), # 균등한 간격으로 표기
    template='plotly_white'
)

# Streamlit에 그래프 표시
st.plotly_chart(fig, use_container_width=True)

st.divider() # 구분선
#######################################################################################################(변동률 데이터 생성성)

# 전월 대비 변동률 계산(소비자물가지수)
a_gro2_long['변동률'] = a_gro2_long.groupby('주요품목별(1)')['값'].pct_change() * 100 # 변동률 백분위 표기

# t2 데이터프레임 생성
t1 = a_gro2_long[['주요품목별(1)', '월', '변동률']]


# 전월 대비 변동률 계산(평균 가격 데이터)
monthly_avg_df['변동률'] = monthly_avg_df.groupby('품목 이름')['가격 평균'].pct_change() * 100 # 변동률 백분위 표기

# 첫 번째 달에는 변동률을 0으로 대체
monthly_avg_df['변동률'] = monthly_avg_df['변동률'].fillna(0)


# 변동률을 포함한 데이터프레임 t 생성
t2 = monthly_avg_df
##########################################################################################################

#화면을 2개의 컬럼으로 분류
col1, col2 = st.columns(2)

# 컬럼 이름 맞추기
t1 = t1.rename(columns={'주요품목별(1)': '품목', '월': '년도-월'})
t2 = t2.rename(columns={'품목 이름': '품목'})

with col1:
    st.write('### 📌 전월 대비 변동률 (소비자물가지수)')
    # t1에 색상 그라디언트 적용
    st.dataframe(t1.style.background_gradient(cmap='Reds'), use_container_width=True)
    csv = t1.to_csv(index = False).encode('utf-8') # 데이터프레임 csv로 변환
    st.download_button(
        '데이터 다운로드',
        data = csv,
        file_name = 't1.csv', # 파일명
        mime = 'text/csv', # 파일 형식
        help = 'CSV 파일로 다운로드 가능합니다.' # 마우스 이동시 도움말말
    )

with col2:
    st.write('### 📌 전월 대비 변동률 (평균가격)')
    # t2에 색상 그라디언트 적용
    st.dataframe(t2[['품목', '년도-월', '변동률']].style.background_gradient(cmap='Reds'), use_container_width=True)
    csv = t2.to_csv(index = False).encode('utf-8') # 데이터프레임 csv로 변환
    st.download_button(
        '데이터 다운로드',
        data = csv,
        file_name = 't2.csv', # 파일명
        mime = 'text/csv', # 파일 형식
        help = 'CSV 파일로 다운로드 가능합니다.' # 마우스 이동시 도움말말
    )

st.write('')
st.write('### 📊 통합 변동률 막대 그래프')

# 두 데이터프레임을 하나로 합치기 전에 '변동률'을 비교할 수 있도록 '변동률' 컬럼에 대한 색상 구분을 추가
t1['category'] = '소비자물가지수'
t2['category'] = '평균가격'


# 두 데이터프레임 합치기
df = pd.concat([t1[['품목', '년도-월', '변동률', 'category']], t2[['품목', '년도-월', '변동률', 'category']]])

# 막대 그래프 생성
fig = px.bar(df, 
             x='년도-월', 
             y='변동률', 
             color='category', # 색상 구분
             barmode='group',  # 막대 그래프를 그룹으로 표시
             color_discrete_map={'소비자물가지수': 'blue', '평균가격': 'red'},  # 색상 지정
             labels={'변동률': '변동률 (%)', '년도-월': '년도-월'}, # 축이름 설정
)

# 레이아웃 설정
fig.update_layout(
    xaxis_tickangle=-45, # 축 이름 각도 설정
    template='plotly', 
    xaxis_title='년도-월',
    yaxis_title='변동률 (%)'
)

# 그래프 출력
st.plotly_chart(fig)