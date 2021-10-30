def update_date(df_price,df_order, df_match, start_date,end_date):
    import datetime
    import pandas as pd
    df_price_hist = df_price.copy()
    df_price_hist['date'] = pd.to_datetime(df_price_hist['dateTime']).dt.date
    df_price_hist = df_price_hist[(df_price_hist['date'] >= start_date) &(df_price_hist['date'] <= end_date)]
    df_match_hist = df_match.copy()
    df_match_hist['date'] = pd.to_datetime(df_match_hist['created']).dt.date
    df_match_hist = df_match_hist[(df_match_hist['date'] >= start_date) & (df_match_hist['date'] <= end_date)]
    df_order_book = df_order.copy()
    return df_price_hist, df_match_hist, df_order_book
