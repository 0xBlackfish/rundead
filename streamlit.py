import streamlit as st
import pandas as pd
import requests
import altair as alt


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
            st.write(' ')
            st.write(' ')

            df_listing_status = df_rundeads_raw.groupby(['listStatus']).count()['mintAddress'].reset_index()

            domain = ['unlisted','listed']
            range_ = ['#f1c40f','grey']

            listing_distribution = alt.Chart(df_listing_status).mark_arc(innerRadius=90).encode(
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
            ).configure_view(
                strokeWidth=0
            )

            st.altair_chart(listing_distribution, use_container_width=True)