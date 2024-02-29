from datetime import datetime

import geopandas as gpd
import pandas as pd
import pydeck as pdk
import streamlit as st
import altair as alt


url = "https://ditppu.menlhk.go.id/portal/read/indeks-standar-pencemar-udara-ispu-sebagai-informasi-mutu-udara-ambien-di-indonesia"
urllhk = "https://www.menlhk.go.id/"
urlsipongi = "https://sipongi.menlhk.go.id/"
urlfirms = "https://firms.modaps.eosdis.nasa.gov/api/country/"
urlopenwea = "https://openweathermap.org/api/air-pollution"
urlbmkg = "https://dataonline.bmkg.go.id/akses_data"
urlboston = "https://www.bc.edu/bc-web/centers/schiller-institute/sites/masscleanair/articles/children.html"
urlhalodoc = "https://www.halodoc.com/artikel/perlu-tahu-ini-7-gangguan-kesehatan-yang-dipicu-partikel-polusi-pm2-5"
urlnafas = "https://nafas.co.id/article/Apakah-PM2-5-berbahaya-untuk-anak-anak"
urlotc = "https://otcdigest.id/kesehatan-anak/polusi-udara-tingkatkan-risiko-adhd-pada-anak-anak"
urlkompastv = "https://www.kompas.tv/regional/448420/akibat-karhutla-kabut-asap-di-palembang-makin-pekat"
urlsctv = "https://www.liputan6.com/photo/read/5415505/diselimuti-kabut-asap-palembang-berlakukan-sekolah-daring?page=1"



st.set_page_config(
    page_title = "Polusi Udara dan Hotspot Kebakaran Lahan Hutan",layout="wide"
)

def format_big_number(num):
    if num >= 1e6:
        return f"{num / 1e6:.3f} Mio"
    elif num >= 1e3:
        return f"{num / 1e3:.3f} K"
    elif num >= 1e2:
        return f"{num / 1e3:.3f} K"
    else:
        return f"{num:.3f}"


firm_all = pd.read_csv('data/nasa_viirs_noaa_oct_2023.csv')
firm_all_prev = pd.read_csv('data/nasa_viirs_noaa_oct_2022.csv')
firm = pd.read_csv('data/hotspot_sumsel.csv')
firm_prev = pd.read_csv('data/hotspot_sumsel_2022.csv')
bmkg = pd.read_csv('data/curah_hujan_temp_plb.csv')
firmhs = len(firm_all.index)
sumselhs =len(firm.index)
firmhs_prev = len(firm_all_prev.index)
sumselhs_prev =len(firm_prev.index)


# tahun sebelumnya dan sekarang
dt_prev = min(bmkg['date'])
dt_now = max(bmkg['date'])



#temperatur sebelumnya dan sekarang
t_prev = bmkg['t_avg'][bmkg['date'] == dt_prev]
t_now =  bmkg['t_avg'][bmkg['date'] == dt_now]
t_avg_prev = t_prev.mean(axis=0)
t_avg_now = t_now.mean(axis=0)

#presipitasi sebelumnya dan sekarang
rr_prev = bmkg['rr_avg'][bmkg['date'] == dt_prev]
rr_now =  bmkg['rr_avg'][bmkg['date'] == dt_now]
rr_avg_prev = rr_prev.mean(axis=0)
rr_avg_now = rr_now.mean(axis=0)


st.markdown("<h3 style='text-align: center; color: orange;'> Pengaruh Hotspot Di Musim El Nino"
            " <br> Terhadap Generasi Masa Depan Indonesia <br><br></h3>", unsafe_allow_html=True)

#perbedaan tahun sebelumnya dan sekarang
hs_diff = 100.0 * ((sumselhs - sumselhs_prev)/sumselhs_prev)
t_diff = 100.0 * ((t_avg_now - t_avg_prev)/t_avg_prev)
rr_diff = 100.0 * ((rr_avg_now - rr_avg_prev)/t_avg_prev)
sumselhs_pct = round(100.0 * (sumselhs/firmhs),2)

with st.container(border=True):
    col_hotspot, col_temp, col_presip = st.columns(3) #add three columns

    with col_hotspot:
      st.metric("Hotspot Sumsel", value=format_big_number(sumselhs), delta=f'{hs_diff:.0f}%')
      st.write("% dari Hs Indonesia : " + str(sumselhs_pct) + "%")

    with col_temp:
      st.metric("Temperatur Rata2", value=format_big_number(t_avg_now), delta=f'{t_diff:.2f}%')
      st.write("Unit Pengukuran: Celcius")

    with  col_presip:
      st.metric("Presipitasi Rata2", value=format_big_number(rr_avg_now), delta=f'{rr_diff:.2f}%')
      st.write( "Unit Pengukuran: mm/hari")

with st.container(border=True):
     st.write("Menurut data [SIPONGI KLHK](%s)" % urlsipongi + " dan [FIRMS NASA](%s)" % urlfirms + " pada bulan Oktober 2023, di wilayah Propinsi Sumatera Selatan yang mempunyai penduduk 8,6 juta jiwa (BPS 2022), dan mempunyai metropolitan yang berkembang yakni Patungraya Agung yang berpenduduk 2,6 juta jiwa (BPS 2020), khususnya Kota Palembang yang berpenduduk sekitar 1,7 juta jiwa (BPS 2022), terjadi puncak kejadian Bencana Kebakaran Hutan Lahan yang diperparah oleh fenomena El Nino. Kejadian ini mengakibatkan terpaparnya polusi kabut asap yang mempunyai risiko tinggi terhadap masyarakat, terutama pada kelompok rentan seperti anak-anak dan ibu hamil yang dapat mengancam Generasi Masa Depan Indonesia")


st.markdown("<br><h4 style='text-align: center; color: red;'>Peta Sebaran Hotspot Kebakaran Hutan Lahan Bulan Oktober 2023</h4>", unsafe_allow_html=True)

#tab untuk peta 3 wilayah administrasi
tab1, tab2, tab3 = st.tabs(['Kota Palembang', 'Provinsi Sumatera Selatan', 'Indonesia'])


with tab1:
    sl1, sl2 = st.columns([1,5])
    with sl1:
        values = st.slider(
            'Radius Sebaran Hotspot (Km)',value=50, min_value=25, max_value=75, step=25)
    if values == 25:
            df1 = gpd.read_file('data/hotspot_plb_25.geojson')
    if values == 50:
            df1 = gpd.read_file('data/hotspot_plb_50.geojson')
    if values == 75:
            df1 = gpd.read_file('data/hotspot_plb_75.geojson')
    # st.write(df2.head(5))
    df1['lon'] = df1.geometry.x  # extract longitude from geometry
    df1['lat'] = df1.geometry.y  # extract latitude from geometry
    df1 = df1[['lon', 'lat']]  # only keep longitude and latitude

    firms_pl = pd.DataFrame(
        df1,
        columns=['lat', 'lon'])

    st.pydeck_chart(pdk.Deck(
            map_provider='carto',
            map_style='dark',
            views=pdk.View(type="mapview", controller=True),
            initial_view_state=pdk.ViewState(
                latitude=-2.9831,
                longitude=104.7527,
                zoom=9,
            ),
            layers=[
                pdk.Layer(
                    'ScatterplotLayer',
                    data=firms_pl,
                    get_position='[lon, lat]',
                    get_color='[200, 30, 0, 200]',
                    get_radius=300,
                ),
            ],
        ))


df = pd.read_csv('data/max_hs_pl_palembang_distinct.csv')

data = pd.pivot_table(
    data=df,
    index=['tgl'],
    aggfunc={
        'Value':pd.Series.nunique,
        'Tanggal':pd.Series.nunique,
    }
).reset_index()




st.markdown("<br><h4 style='text-align: center; color: red;'>Tingkat ISPU PM 2.5 per Hari di Bulan Oktober 2023</h4>", unsafe_allow_html=True)

threshold1 = 51.0
threshold2 = 101.0
threshold3 = 201.0
threshold4 = 301.0

bars = alt.Chart(df).mark_bar(color="green", opacity=0.2).encode(
    x="Tanggal:O",
    y="Value:Q",
)

highlight1 = bars.mark_bar(color="blue", opacity=0.2).encode(
    y2=alt.Y2(datum=threshold1)
).transform_filter(
    alt.datum.Value > threshold1
)

highlight2 = bars.mark_bar(color="yellow").encode(
    y2=alt.Y2(datum=threshold2)
).transform_filter(
    alt.datum.Value > threshold2
)

highlight3 = bars.mark_bar(color="red").encode(
    y2=alt.Y2(datum=threshold3)
).transform_filter(
    alt.datum.Value > threshold3
)

rule1 = alt.Chart().mark_rule(size=2).encode(
    y=alt.Y(datum=threshold2)
)

label1 = rule1.mark_text(
    x="width",
    dx=-2,
    align="right",
    baseline="bottom",
    fontSize=15,
    text="TIDAK SEHAT",
    color="grey"

)

rule2 = alt.Chart().mark_rule(size=2).encode(
    y=alt.Y(datum=threshold3)
)

label2 = rule2.mark_text(
    x="width",
    dx=-2,
    align="right",
    baseline="bottom",
    fontSize=15,
    text="SANGAT TIDAK SEHAT",
    color="grey"
)

st.altair_chart(bars + highlight1 + highlight2 + highlight3 + rule1 + label1 +rule2 + label2, use_container_width=True)




left_co, cent_co,last_co = st.columns([1,8,1])
with cent_co:
    st.write("Kategori Indeks Standar Pencemar Udara (ISPU) PM 2.5 yang merupakan partikel"
             "pencemar udara paling berpengaruh"
             " bagi kesehatan manusia ada di tautan [DitppuLHK](%s)" % url)
    st.image("data/kategori_ispu.png")


#dataframe untuk korrelasi
df2 = pd.read_csv('data/pollute_plb_75_b.csv')

data = pd.pivot_table(
    data=df2,
    index=['Tanggal'.format(datetime)],
    aggfunc={
        'ISPU_PM_2_5':pd.Series.nunique,
        'PM2_5':pd.Series.nunique,
        'PM10':pd.Series.nunique,
        'tgl':pd.Series.unique,
        'Jarak':'sum'.format(int),
        'Kecerahan_Channel_4':'sum'.format(int),
        'Kecerahan_Channel_5':'sum'.format(int),
        'Temperatur':'sum'.format(int),
        'Curah_Hujan':'sum'.format(int),
        'Kecepatan_Angin':'sum'.format(int)
    }
).reset_index()


st.markdown("<br><h4 style='text-align: center; color: red;'>Korrelasi ✨ </h4>", unsafe_allow_html=True)

#korrelasi per jarak, curah hujan, kecepatan angin

jarak_hs, hujan_hs, angin_hs = st.columns(3)

with jarak_hs:
        st.markdown("<h5 style='text-align: center; color: white;'>Rata2 Jarak (km) Hotspot Dengan ISPU PM 2.5 per Hari</h5>", unsafe_allow_html=True)
        scatter2 = alt.Chart(df2).mark_point().encode(
        x="mean(Jarak):Q",
        y="ISPU_PM_2_5:Q",
        )

        st.altair_chart(scatter2, theme='streamlit',  use_container_width=True)

with hujan_hs:
        st.markdown("<h5 style='text-align: center; color: white;'>Presipitasi rata2 (mm) dan ISPU PM 2.5 per Hari</h5>", unsafe_allow_html=True)
        scatter = alt.Chart(df2).mark_point().encode(
        x="mean(Curah_Hujan):Q",
        y="ISPU_PM_2_5:Q",
        )

        st.altair_chart(scatter, theme='streamlit',  use_container_width=True)

with angin_hs:
        st.markdown("<h5 style='text-align: center; color: white;'>Rata2 Kecepatan Angin (m/dtk) dan ISPU PM 2.5 per Hari</h5>", unsafe_allow_html=True)
        scatter = alt.Chart(df2).mark_point().encode(
        x="mean(Kecepatan_Angin):Q",
        y="ISPU_PM_2_5:Q",
        )

        st.altair_chart(scatter, theme='streamlit',  use_container_width=True)


    #korrelasi dengan temperatur, curah hujan, kecepatan angin
temp_hs, bright4_hs , bright5_hs = st.columns(3)

with temp_hs:
        st.markdown("<h5 style='text-align: center; color: white;'>Rata2 Temperatur (Celcius) dan ISPU PM 2.5 per Hari</h5>", unsafe_allow_html=True)
        scatter2 = alt.Chart(df2).mark_point().encode(
            x="mean(Temperatur):Q",
            y="ISPU_PM_2_5:Q",
        )

        st.altair_chart(scatter2, theme='streamlit',  use_container_width=True)

with bright4_hs:
        st.markdown("<h5 style='text-align: center; color: white;'>Rata2 Kecerahan Hotspot Channel 4 (Kelvin)  dan ISPU PM 2.5 per Hari</h5>", unsafe_allow_html=True)
        scatter = alt.Chart(df2).mark_point().encode(
            x="mean(Kecerahan_Channel_4):Q",
            y="ISPU_PM_2_5:Q",
        )

        st.altair_chart(scatter, theme='streamlit',  use_container_width=True)

with bright5_hs:
        st.markdown("<h5 style='text-align: center; color: white;'>Rata2 Kecerahan Hotspot Channel 5 (Kelvin) dan ISPU PM 2.5 per Hari</h5>", unsafe_allow_html=True)
        scatter = alt.Chart(df2).mark_point().encode(
            x="mean(Kecerahan_Channel_5):Q",
            y="ISPU_PM_2_5:Q",
        )

        st.altair_chart(scatter, theme='streamlit',  use_container_width=True)


with st.container(border=True):
    st.markdown(
        "<h4 style='text-align: center; color: red;'>Partikel Kecil Mengancam Generasi Masa Depan Indonesia</h4>",
        unsafe_allow_html=True)
    st.write("Particulate Matter (PM2.5) adalah partikel udara yang berukuran lebih kecil dari atau sama dengan 2.5 µm (mikrometer).\n"
             "PM2.5 berbahaya bagi orang-orang dari segala usia namun sangat berbahaya bagi anak-anak. \n"
             "Dibandingkan orang dewasa, tubuh anak-anak lebih rentan terhadap polusi PM2.5 ini. \n " 
             "Partikel kecil ini dapat menyebabkan banyak dampak negatif terhadap kesehatan \n" 
             "pada anak termasuk asma, penurunan volume otak, disfungsi perilaku, ADHD, Autism Spectrum Disorder (ASD), \n"
             "dan gangguan pertumbuhan paru-paru. \n"
             "Paparan seorang ibu terhadap PM2.5 selama kehamilannya meningkatkan risiko kelahiran prematur, \n" 
             " berat badan lahir rendah, dan lahir mati.")


with st.container(border=True):
    st.write("✨ Untuk Korrelasi, Data Jarak dan Kecerahan Hotspot maksimal dalam radius 75km Kota Palembang, menyesuaikan dengan Data Temperatur, Presipitasi, serta Kecepatan Angin, yang Stasiun dan Akurasi Pengukurannya Berada di Sekitar Kota Palembang")
with st.container(border=True):
     st.markdown("* Sumber Data: [KemenLHK](%s)" % urllhk + ", "
             "[FIRMS NASA](%s)" % urlfirms + ", "
             "[Open Weather Map](%s)" % urlopenwea + ", "
             "[BMKG](%s)" % urlbmkg + ", "
             "[Boston College](%s)" % urlboston + ", "
             "[Nafas Indonesia](%s)" % urlnafas + ", "
             "[OTC Digest](%s)" % urlotc + ", "
             "[Halodoc](%s)" % urlhalodoc + ", "
             "[Kompas TV](%s)" % urlkompastv + ", "
             "[Liputan 6 SCTV](%s)" % urlsctv, unsafe_allow_html=True)


#tab lain utk peta diloading paling akhir
with tab2:
    df2 = gpd.read_file('data/hostpot_sumsel.geojsonl.json')
    # st.write(df2.head(5))
    df2['lon'] = df2.geometry.x  # extract longitude from geometry
    df2['lat'] = df2.geometry.y  # extract latitude from geometry
    df2 = df2[['lon', 'lat']]  # only keep longitude and latitude

    firms = pd.DataFrame(
        df2,
        columns=['lat', 'lon'])

    st.pydeck_chart(pdk.Deck(
        map_provider='carto',
        map_style='dark',
        views=pdk.View(type="mapview", controller=True),
        initial_view_state=pdk.ViewState(
            latitude=-2.9831
            , longitude=104.7527,
            zoom=7,
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=firms,
                get_position='[lon, lat]',
                get_color='[200, 30, 0, 200]',
                get_radius=300,
            ),
        ],
    ))

with tab3:
    df3 = gpd.read_file('data/idn.geojson')
    df3['lon'] = df3.geometry.x  # extract longitude from geometry
    df3['lat'] = df3.geometry.y  # extract latitude from geometry
    df3 = df3[['lon', 'lat']]  # only keep longitude and latitude

    firms_idn = pd.DataFrame(
        df3,
        columns=['lat', 'lon'])

    st.pydeck_chart(pdk.Deck(
        map_provider='carto',
        map_style='dark',
        views=pdk.View(type="mapview", controller=True),
        initial_view_state=pdk.ViewState(
            latitude=-3.1952,
            longitude=117.6524,
            zoom=4,
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=firms_idn,
                get_position='[lon, lat]',
                get_color='[200, 30, 0, 200]',
                get_radius=300,
            ),
        ],
    ))
