import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Black Friday laptop prices", layout="wide")

@st.cache()
def get_data(source_file):
    ''' Loading and transforming the data. '''
    col_names = ['Time', 'Name', 'Brand', 'Category', 'Reviews', 'Rating', 'Screen', 'Processor'
            , 'Memory', 'Graphics_Card', 'Disk', 'Operating_System', 'Current_Price', 'Former_Price'
            , 'Delivery', 'Item_Page']
    df = pd.read_csv(source_file, 
                    names=col_names, engine='python', error_bad_lines = False
                    ,parse_dates=['Time'])
    #filtering and cleaning the data data
    df = df[(df['Time'].dt.strftime('%Y-%m-%d') >= '2021-11-25') & (df['Time'].dt.strftime('%Y-%m-%d') <= '2021-11-30') & (df['Delivery'] == 'online')]
    df['Current_Price'] = df['Current_Price'].str.split('zł').str.get(0).str.replace(u'\xa0', u'').astype(float)
    df['Former_Price'] = df['Former_Price'].str.split('zł').str.get(0).str.replace(u'\xa0', u'').astype(float)
    
    def get_rating(row):
        if str(row['Rating']).startswith('Brak') or pd.isnull(row['Rating']):
            return np.nan
        elif str(row['Rating'])[1] == '.':
            return row['Rating'][0:3]
        else:
            return row['Rating'][0]

    def get_reviews_number(row):
        if pd.isnull(row['Reviews']):
            return 0
        else:
            return row['Reviews'].split(' ')[0].replace('(','')

    df['Rating_Number'] = df.apply(get_rating, axis=1)
    df['Reviews_Number'] = df.apply(get_reviews_number, axis=1)
    df['Rating_Number'] = df['Rating_Number'].astype(float)
    df['Reviews_Number'] = df['Reviews_Number'].astype(int)
    return df

@st.cache()
def get_prices_data(source_df):
    ''' Getting max and min prices for each product stored as a new dataframe. '''
    df_prices = source_df.groupby('Name').agg({'Current_Price': ['min', 'max'], 'Former_Price': ['min', 'max']}).reset_index()
    df_prices.columns = list(map('_'.join, df_prices.columns.values))
    return df_prices

df = get_data('laptops_scraped.csv')
df_prices = get_prices_data(df)

#getting products with at least 20% price difference
product_list = df_prices[(df_prices['Current_Price_min'] / df_prices['Current_Price_max']) <= 0.8]['Name_'].tolist()
time_range_list = df['Time'].dt.date.unique().tolist()

st.title('Black Friday (and Cyber Monday) laptop prices 💰📈')
st.write('''This site allows to browse laptop prices during Black Friday (26th Nov) and Cyber Monday (29th Nov) from popular polish
    electronics store, RTV EURO  AGD. Data was gathered through web scraping,
    and full time range is from 25th (late evening) to 30th November.
    \nOnly products that were available online and had prices changes during that time are in scope.
    ''')

select_model = st.sidebar.selectbox('Please select the brand'
                                    ,product_list
                                    ,index=product_list.index('Lenovo IdeaPad 3 15ADA05 15,6" AMD Ryzen 3 3250U - 8GB RAM - 256GB Dysk - Win10S'))
select_date_range = st.sidebar.slider('Please select time range'
                                        ,min_value=min(time_range_list)
                                        ,max_value=max(time_range_list)
                                        ,value=(time_range_list[1],max(time_range_list)))

#filter df
df_sel = df[(df['Name'] == select_model) & ( df['Time'].dt.date.between(select_date_range[0], select_date_range[1]) )]
screen = df_sel['Screen'].unique()[0]
processor = df_sel['Processor'].unique()[0]
memory = df_sel['Memory'].unique()[0]
graphics_card = df_sel['Graphics_Card'].unique()[0]
disk = df_sel['Disk'].unique()[0]
operating_system = df_sel['Operating_System'].unique()[0]
min_price = df_sel['Current_Price'].min()
max_price = df_sel['Current_Price'].max()
rating = df_sel['Rating_Number'].max()
reviews_number = df_sel['Reviews_Number'].max()

def get_stars(rating):
    if pd.isnull(rating):
        return ''
    if rating == 5.0:
        return '⭐⭐⭐⭐⭐'
    if rating >= 4.0:
        return '⭐⭐⭐⭐'
    if rating >= 3.0:
        return '⭐⭐⭐'
    if rating >= 2.0:
        return '⭐⭐'
    if rating >= 1.0:
        return '⭐'       

stars = get_stars(rating)

st.write(f'Selected Model: _{select_model}_')
left_column,right_column = st.columns(2)
with left_column:
    st.write(f'Inches: {screen}')
    st.write(f'Processor: {processor}')
    st.write(f'Memory: {memory}')
    st.write(f'Graphics Card: {graphics_card}')
    st.write(f'Disk: {disk}')
    st.write(f'Operating System: {operating_system}')

with right_column:
    st.write(f'🔥 Lowest price: _{min_price}_ PLN')
    st.write(f'🔕 Highest price: _{max_price}_ PLN')
    st.write(f'Rating: {stars} (_{rating}_)')
    st.write(f'Number of reviews: _{reviews_number}_')


fig = px.line(df_sel, x="Time", y=['Current_Price','Former_Price'])
fig.update_yaxes(rangemode='tozero')
fig.update_layout(
    yaxis_title='Price',
    legend_title='Price type'
    )
newnames = {'Current_Price':'Current Price', 'Former_Price': 'Former Price (before discount)'}
fig.for_each_trace(lambda t: t.update(name = newnames[t.name],
                                      legendgroup = newnames[t.name],
                                      hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])
                                     )
                  )

st.plotly_chart(fig)
