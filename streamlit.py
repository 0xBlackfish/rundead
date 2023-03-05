import streamlit as st
import pandas as pd
import requests
import altair as alt
from datetime import datetime, date, timedelta


st.set_page_config(
    page_title='Bone Counter',
    layout='wide',
    initial_sidebar_state='collapsed'
    )

st.title('Rundead Bone Analytics Hub')
st.markdown(
    '''
    _**Created by:**_ _0xBlackfish   👉   [Telegram](https://t.me/OxBlackfish), 0xBlackfish#6012 on Discord, [Twitter](https://twitter.com/0xBlackfish)_
    
    _Tips are much appreciated and can be sent to `J8gA2QZkxGF1fhJHtWokiWLPjwbTm5QybtSTTDdP8JWK`_
    
    ---

    Welcome to the rundead analytics hub - your destination for crunching the bones...I mean numbers! 
    
    Racetime is upon us. Let's RUN 🔥🔥🔥

    ---

    '''
)

pub_key = st.sidebar.text_input(
    'Enter the pub key of the wallet you want to analyze',
    type='password'
    )
bin_size = st.sidebar.text_input(
    'Bin Size',
    value=5   
)

if pub_key != '':

    offset = 0
    df = pd.DataFrame({'Placeholder': [0], 'Value':[1]})
    df_rundeads_raw = pd.DataFrame()

    while (offset < 20000) and (not df.empty):
        
        url = "http://api-mainnet.magiceden.dev/v2/wallets/"+pub_key+"/tokens?offset="+str(offset)+"&limit=500"
        response = requests.get(url)
        json = response.json()
        
        df = pd.DataFrame(json)
        print(len(df))
        
        if df.empty:
            pass
        else:
            df_rundead_filtered = df[df['collection'] == 'rundead']
            print(len(df_rundead_filtered))
        
            df_rundeads_raw = pd.concat([df_rundead_filtered, df_rundeads_raw])
        
        offset+=500

        df_rundeads_raw['bones'] = df_rundeads_raw['attributes'].apply(lambda x: int(next(item for item in x if item['trait_type'] == 'Bones')['value']))
        
        try:
            df_rundeads_raw['price_per_bone'] = df_rundeads_raw['price'] / df_rundeads_raw['bones']
        except:
            pass

    st.write(' ')
    st.write(' ')
    st.markdown('## Wallet Holdings')
    st.write(' ')
    st.write(' ')

    # KPIs
    with st.container():

        c1c1, c1c2, c1c3 = st.columns(3)

        c1c1.metric('Bone Count', df_rundeads_raw['bones'].sum())
        c1c2.metric('Rundead Count', len(df_rundeads_raw))
        c1c3.metric('Bones per Rundead', round(df_rundeads_raw['bones'].sum() / len(df_rundeads_raw),2))

        st.write(' ')
        st.write(' ')
        st.write(' ')
        st.write(' ')
        st.write(' ')


    # Distributions
    with st.container():

        c2c1, c2c2 = st.columns(2,gap='large')

        with c2c1:
            st.markdown(
                '''
                ##### Absolute Distribution of Rundeads
                _The absolute distribution of rundeads by bins_
                '''
            )
            st.write(' ')
            st.write(' ')
            st.write(' ')
            st.write(' ')

            abs_distribution = alt.Chart(df_rundeads_raw).mark_bar().encode(
                x=alt.X(
                    'bones',
                    axis=alt.Axis(
                        title='Bone Count'
                    ),
                    bin=alt.Bin(
                        step=int(bin_size)
                    )
                ),
                y=alt.Y(
                    'count()',
                    axis=alt.Axis(
                        title='Rundeads',
                        grid=False
                    )
                ),
                color=alt.value('#f1c40f')
            )

            st.altair_chart(abs_distribution, use_container_width=True)

        with c2c2:
            st.markdown(
                '''
                ##### Percentage Distribution of Rundeads
                _The discrete and cumulative percentage distribution of rundeads_
                '''
            )

            df_rundeads_bones_pct = df_rundeads_raw.groupby('bones').sum().reset_index()[['bones','supply']]
            df_rundeads_bones_pct['total_supply'] = len(df_rundeads_raw)
            df_rundeads_bones_pct['pct'] = df_rundeads_bones_pct['supply'] / df_rundeads_bones_pct['total_supply']
            bones_range = pd.Series(range(0,max(df_rundeads_raw['bones'])+1),name='bones')
            df_rundeads_bones_pct_merged = pd.merge(bones_range,df_rundeads_bones_pct,how='left',on='bones')
            df_rundeads_bones_pct_merged['pct'].fillna(0,inplace=True)
            df_rundeads_bones_pct_merged['cumulative_pct'] = df_rundeads_bones_pct_merged['pct'].cumsum()
            
            pct_distribution = alt.Chart(df_rundeads_bones_pct_merged).mark_bar().encode(
                x=alt.X(
                    'bones:O',
                    axis=alt.Axis(
                        title='Bone Count',
                        labelAngle=0
                    )
                ),
                y=alt.Y(
                    'pct',
                    axis=alt.Axis(
                        title='Percent of Rundeads',
                        format='%',
                        grid=False
                    )
                ),
                color=alt.value('#f1c40f'),
                tooltip=[
                    alt.Tooltip('bones',title='Bone Count'),
                    alt.Tooltip('pct',title='Pct',format='.1%')
                ]
            )

            pct_distribution_cumulative = alt.Chart(df_rundeads_bones_pct_merged).mark_area().encode(
                x=alt.X(
                    'bones:O',
                    axis=alt.Axis(
                        title='Bone Count',
                        labelAngle=0
                    )
                ),
                y=alt.Y(
                    'cumulative_pct',
                    axis=alt.Axis(
                        title='Percent of Rundeads',
                        format='%',
                        grid=False
                    )
                ),
                color=alt.value('#f1c40f'),
                tooltip=[
                    alt.Tooltip('bones',title='Bone Count'),
                    alt.Tooltip('cumulative_pct',title='Pct',format='.1%')
                ]
            )

            tab_discrete, tab_cumulative = st.tabs(["Discrete", "Cumulative"])

            with tab_discrete:
                st.altair_chart(pct_distribution, use_container_width=True)
            
            with tab_cumulative:
                st.altair_chart(pct_distribution_cumulative, use_container_width=True)
        
        st.write(' ')
        st.write(' ')
        st.write(' ')
        st.write(' ')
        st.write(' ')

    # Listings
    with st.container():

        c3c1, c3c2 = st.columns(2,gap='large')

        with c3c1:
            st.markdown(
                '''
            ##### Listing Distribution
            _The distribution of how many rundeads are listed vs. unlisted_
                '''
            )
            st.write(' ')
            st.write(' ')

            df_listing_status = df_rundeads_raw.groupby(['listStatus']).count()['mintAddress'].reset_index()

            domain = ['unlisted','listed']
            range_ = ['#f1c40f','#e74c3c']

            listing_distribution = alt.Chart(df_listing_status).mark_arc(innerRadius=75).encode(
                theta=alt.Theta(field="mintAddress", type="quantitative"),
                color=alt.Color(
                    field="listStatus", 
                    type="nominal", 
                    scale=alt.Scale(
                        domain=domain, 
                        range=range_
                    ),
                    legend=alt.Legend(
                        title='Listing Status',
                        orient='bottom'
                    )
                ),
                tooltip=[
                    alt.Tooltip('listStatus', title='Listing Status'),
                    alt.Tooltip('mintAddress',title='Count')
                ]
            ).properties(
                height=300
            ).configure_view(
                strokeWidth=0
            )

            st.altair_chart(listing_distribution, use_container_width=True)

        with c3c2:
            st.markdown(
                '''
            ##### Listing Scatter
            _The listing of rundeads based on bone count and list price_
                '''
            )
            st.write(' ')
            st.write(' ')

            if len(df_rundeads_raw[df_rundeads_raw['listStatus'] == 'unlisted']) != len(df_rundeads_raw):
            
                listing_scatter = alt.Chart(df_rundeads_raw).mark_circle(size=60).encode(
                    x=alt.X(
                        'bones',
                        axis=alt.Axis(
                            title='Bone Count'
                        )
                    ),
                    y=alt.Y(
                        'price',
                        axis=alt.Axis(
                            title='Price (SOL)'
                        )
                    ),
                    color=alt.value('#f1c40f'),
                    size=alt.Size(
                        'price_per_bone',
                        legend=alt.Legend(
                            title='Price per Bone',
                            orient='bottom'
                        )
                    ),
                    tooltip=[
                        alt.Tooltip('name',title='Rundead'),
                        alt.Tooltip('mintAddress',title='mint'),
                        alt.Tooltip('price',title='Price (SOL)'),
                        alt.Tooltip('bones',title='Bone Count'),
                        alt.Tooltip('price_per_bone',title='Price per Bone',format='0.0')
                    ]
                ).properties(
                    height=300
                )

                st.altair_chart(listing_scatter, use_container_width=True)
            
            else:

                st.dataframe(df_rundeads_raw[['name','mintAddress','bones']].sort_values(by='bones',ascending=False),height=250)

    
    st.write(' ')
    st.write(' ')
    st.markdown('## Wallet Activity')
    st.write(' ')
    st.write(' ')

    lookback_window = st.number_input(
        'Activity Lookback Window (hrs)',
        min_value=1,
        value=24,
        step=1
    )
    st.write(' ')
    st.write(' ')
    st.write(' ')
    st.write(' ')

    offset = 0
    df = pd.DataFrame({'Placeholder': [0], 'Value':[1]})
    df_rundeads_activity_raw = pd.DataFrame()

    while (offset < 50000) and (not df.empty):
        
        url = 'http://api-mainnet.magiceden.dev/v2/wallets/'+pub_key+'/activities?offset='+str(offset)+'&limit=500'
        response = requests.get(url)
        json = response.json()
        
        df = pd.DataFrame(json)
        
        if df.empty:
            pass
        else:
            df_rundead_activity_filtered = df[df['collection'] == 'rundead']
        
            df_rundeads_activity_raw = pd.concat([df_rundead_activity_filtered, df_rundeads_activity_raw])
        
        offset+=500

    df_rundeads_activity_raw['timestamp'] = df_rundeads_activity_raw['blockTime'].apply(lambda x: datetime.utcfromtimestamp(x))
    df_rundeads_activity_lookback = df_rundeads_activity_raw[df_rundeads_activity_raw['timestamp']>=(datetime.now()- timedelta(hours=lookback_window))]

    df_rundeads_activity_delist = df_rundeads_activity_raw[df_rundeads_activity_raw['type'] == 'delist']
    df_rundeads_activity_list = df_rundeads_activity_raw[df_rundeads_activity_raw['type'] == 'list']
    df_rundeads_activity_buy = df_rundeads_activity_raw[(df_rundeads_activity_raw['type'] == 'buyNow') & (df_rundeads_activity_raw['buyer'] == pub_key)]
    df_rundeads_activity_sell = df_rundeads_activity_raw[(df_rundeads_activity_raw['type'] == 'buyNow') & (df_rundeads_activity_raw['seller'] == pub_key)]

    # KPIs
    with st.container():

        c4c1, c4c2, c4c3, c4c4 = st.columns(4)

        c4c1.metric('Last {}hr Delistings'.format(lookback_window), df_rundeads_activity_lookback[(df_rundeads_activity_lookback['type'] == 'delist')]['tokenMint'].nunique())
        c4c2.metric('Last {}hr Listings'.format(lookback_window), df_rundeads_activity_lookback[(df_rundeads_activity_lookback['type'] == 'list')]['tokenMint'].nunique())
        c4c3.metric('Last {}hr Purchases'.format(lookback_window), len(df_rundeads_activity_lookback[(df_rundeads_activity_lookback['type'] == 'buyNow') & (df_rundeads_activity_lookback['buyer'] == pub_key)]))
        c4c4.metric('Last {}hr Sales'.format(lookback_window), len(df_rundeads_activity_lookback[(df_rundeads_activity_lookback['type'] == 'buyNow') & (df_rundeads_activity_lookback['seller'] == pub_key)]))

        st.write(' ')
        st.write(' ')
        st.write(' ')
        st.write(' ')
        st.write(' ')

    # List / Delist
    with st.container():

        c5c1, c5c2 = st.columns(2,gap='large')

        with c5c1:

            st.markdown(
                '''
                ##### Rundead Delisting Volume
                _The number of unique Rundead NFTs delisted_
                '''
            )
            st.write(' ')
            st.write(' ')
            st.write(' ')
            st.write(' ')

            delistings = alt.Chart(df_rundeads_activity_delist).mark_bar().encode(
                x=alt.X(
                    'yearmonthdate(timestamp):O',
                    axis=alt.Axis(
                        title='Date',
                        labelAngle=-45
                    )
                ),
                y=alt.Y(
                    'distinct(tokenMint)',
                    axis=alt.Axis(
                        title='Rundead Volume',
                        grid=False
                    )
                ),
                color=alt.value('#f1c40f'),
                tooltip=[
                    alt.Tooltip('yearmonthdate(timestamp):O',title='Date'),
                    alt.Tooltip('distinct(tokenMint)',title='Unique Rundeads')
                ]
            )

            st.altair_chart(delistings, use_container_width=True)

        with c5c2:

            st.markdown(
                '''
                ##### Rundead Listing Volume
                _The number of unique Rundead NFTs listed_
                '''
            )
            st.write(' ')
            st.write(' ')
            st.write(' ')
            st.write(' ')

            listings = alt.Chart(df_rundeads_activity_list).mark_bar().encode(
                x=alt.X(
                    'yearmonthdate(timestamp):O',
                    axis=alt.Axis(
                        title='Date',
                        labelAngle=-45
                    )
                ),
                y=alt.Y(
                    'distinct(tokenMint)',
                    axis=alt.Axis(
                        title='Rundead Volume',
                        grid=False
                    )
                ),
                color=alt.value('#f1c40f'),
                tooltip=[
                    alt.Tooltip('yearmonthdate(timestamp):O',title='Date'),
                    alt.Tooltip('distinct(tokenMint)',title='Unique Rundeads')
                ]
            )

            st.altair_chart(listings, use_container_width=True)
    
        st.write(' ')
        st.write(' ')
        st.write(' ')
        st.write(' ')
        st.write(' ')

    # Sell / Purchase
    with st.container():

        c6c1, c6c2 = st.columns(2,gap='large')

        with c6c1:

            st.markdown(
                '''
                ##### Rundead Sales Volume
                _The number of Rundead NFTs sold_
                '''
            )
            st.write(' ')
            st.write(' ')
            st.write(' ')
            st.write(' ')

            sales = alt.Chart(df_rundeads_activity_sell).mark_bar().encode(
                x=alt.X(
                    'yearmonthdate(timestamp):O',
                    axis=alt.Axis(
                        title='Date',
                        labelAngle=-45
                    )
                ),
                y=alt.Y(
                    'distinct(signature)',
                    axis=alt.Axis(
                        title='Rundead Sales',
                        grid=False
                    )
                ),
                color=alt.value('#f1c40f'),
                tooltip=[
                    alt.Tooltip('yearmonthdate(timestamp):O',title='Date'),
                    alt.Tooltip('distinct(signature)',title='Rundeads Sold')
                ]
            )

            st.altair_chart(sales, use_container_width=True)

        with c6c2:

            st.markdown(
                '''
                ##### Rundead Purchase Volume
                _The number of Rundead NFTs purchased_
                '''
            )
            st.write(' ')
            st.write(' ')
            st.write(' ')
            st.write(' ')

            purchases = alt.Chart(df_rundeads_activity_buy).mark_bar().encode(
                x=alt.X(
                    'yearmonthdate(timestamp):O',
                    axis=alt.Axis(
                        title='Date',
                        labelAngle=-45
                    )
                ),
                y=alt.Y(
                    'distinct(signature)',
                    axis=alt.Axis(
                        title='Rundead Purchases',
                        grid=False
                    )
                ),
                color=alt.value('#f1c40f'),
                tooltip=[
                    alt.Tooltip('yearmonthdate(timestamp):O',title='Date'),
                    alt.Tooltip('distinct(signature)',title='Rundeads Purchased')
                ]
            )

            st.altair_chart(purchases, use_container_width=True)

        
