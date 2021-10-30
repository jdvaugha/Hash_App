from FunctionRepo import *
import pandas as pd
import streamlit as st
import altair as alt
import datetime
import urllib.request


@st.cache
def get_data(num):
    def get_price_hist():
        import pandas as pd
        import urllib
        import json
        json_ = urllib.request.urlopen('https://www.dlob.io/aggregator/external/api/v1/order-books/pb18vd8fpwxzck93qlwghaj6arh4p7c5n894vnu5g/price-history?period=ALL').read()
        json_ = json.loads(json_)
        df = pd.read_json(json.dumps(json_, indent=4, sort_keys=True))
        return df

    def get_current_order_book():
        import pandas as pd
        import urllib
        import json
        order_book_json = urllib.request.urlopen('https://www.dlob.io/aggregator/external/api/v1/order-books/pb18vd8fpwxzck93qlwghaj6arh4p7c5n894vnu5g/price-book').read()
        order_book_json = json.loads(order_book_json)
        df_order_book_json_ask = pd.read_json(json.dumps(order_book_json['asks'], indent=4, sort_keys=True))
        df_order_book_json_ask['trade_type'] = 'asks'
        df_order_book_json_bid = pd.read_json(json.dumps(order_book_json['bids'], indent=4, sort_keys=True))
        df_order_book_json_bid['trade_type'] = 'bids'
        df_order_book = df_order_book_json_ask.append(df_order_book_json_bid)
        return df_order_book

    def get_match_history(num):
        import pandas as pd
        import urllib
        import json
        df = pd.DataFrame()
        for i in range(1,num):
            json_ = json.loads(urllib.request.urlopen('https://www.dlob.io/aggregator/external/api/v1/order-books/pb18vd8fpwxzck93qlwghaj6arh4p7c5n894vnu5g/transactions?page={0}&size=100'.format(i)).read())
            if len(json_["data"]) == 0:
                break
            else:
                df_ = pd.read_json(json.dumps(json_['data'], indent=4, sort_keys=True))
                df = df.append(df_)
                df.displayAmount = pd.to_numeric(df.displayAmount).fillna(0)
        return df

    df_price = get_price_hist()
    df_order = get_current_order_book()
    df_match = get_match_history(num)
    return df_price,df_order, df_match


df_price, df_order, df_match = get_data(1000)

start_date = st.sidebar.date_input('start date', value=datetime.datetime(2021, 5, 1))
end_date = st.sidebar.date_input('end date', value=datetime.datetime.now())

df_price_hist, df_match_hist, df_order_book = update_date(df_price,
                                                          df_order,
                                                          df_match,
                                                          start_date,
                                                          end_date)

st.header("Provenance Hash Price")

col1, col2 = st.columns(2)

with col1:
    st.write("Start Date: ", str(start_date))
with col2:
    st.write("End Date: ", str(end_date))
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Min Price: "+ str(df_price_hist.displayPricePerDisplayUnit.min()))
with col2:
    st.subheader("Avg Price: " + str(round(df_price_hist.displayPricePerDisplayUnit.mean(),3)))
with col3:
    st.subheader("Max Price: "+ str(df_price_hist.displayPricePerDisplayUnit.max()))


price_chart = alt.Chart(df_price_hist).mark_line().encode(
    x=alt.X('dateTime:T',title='Date'),
    y=alt.Y('displayPricePerDisplayUnit:Q',title='Price'),
    tooltip=['dateTime','displayPricePerDisplayUnit']
).interactive()

chart_volume = alt.Chart(df_match_hist[['created','displayAmount','displayPricePerUnit','type']][df_match_hist['type']=='MATCH'].groupby('created')['displayAmount'].sum().reset_index()).mark_bar().encode(
    y=alt.Y('displayAmount:Q',title='Volume'),
    x=alt.X('created:T',title='Date'),
    tooltip=['created','displayAmount']
).interactive()

order_book = alt.Chart(df_order_book[['displayPricePerDisplayUnit','displayTotalUnits','trade_type']]).mark_bar().encode(
    x=alt.X('displayPricePerDisplayUnit:Q',title='Bid/Ask Offer Price'),
    y=alt.Y('displayTotalUnits:Q', scale=alt.Scale(reverse=False),title='Volume'),
    color='trade_type',
    tooltip=['displayPricePerDisplayUnit','displayTotalUnits']
).interactive()

st.subheader("Price History")
st.altair_chart(price_chart, use_container_width=True)
st.subheader("Volume History")
st.altair_chart(chart_volume, use_container_width=True)
st.subheader("Order Book")
st.altair_chart(order_book, use_container_width=True)
#st.altair_chart(alt.hconcat(alt.vconcat(price_chart, chart_volume),order_book))



