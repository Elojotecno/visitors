# -*- coding: utf-8 -*-
"""
Created on 08/30/2024
@author: Yann MARCOLINI
"""
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_cookies_controller import CookieController
import hmac
from geopy.geocoders import Nominatim
import plotly.express as px
import datetime
import json
import urllib.request

prod_list = ['M²erlin', 'Barn-E', 'Nano', 'Moov', 'Racleur', 'Autre']
eqt_list = ['TPA', 'Epi', 'Roto', 'Robot', 'Autre']
brand_list = ['Boumatic', 'Delaval', 'Fullwood', 'Gascoigne-Melotte', 'GEA', 'Lely', 'Manus', 'Surge', 'Autre']
user_db = {"FullwoodJoz" : "./data/fj_visitors.csv", "Transfaire" : "./data/trf_visitors.csv"}
user_logo = {"FullwoodJoz" : "./img/fjm.png", "Transfaire" : "./img/transfaire.png"}
terms_and_conditions_fj = "https://www.fullwoodjoz.com/fr/terms-and-conditions/"

st.set_page_config(layout="wide")

def search_city(zip):

    noms_ville = []
    api_base = 'https://geo.api.gouv.fr/communes?codePostal='
	
    if len(zip) != 5:

        noms_ville.append("Code postal erroné...")
    
    else:
    
        cnx = urllib.request.urlopen(api_base + zip)
        contenu = cnx.read().decode('utf8')
        json_lisible = json.loads(contenu)

        for info in json_lisible:
            noms_ville.append(info['nom'])
        return noms_ville


def check_password(controller):
    
    def login_form():
        
        with st.form("Credentials"):
            st.text_input("Utilisateur", key="username")
            st.text_input("Mot de passe", type="password", key="password")
            st.form_submit_button("Valider", on_click=password_entered)
        
    def password_entered():

        controller.set('usr', st.session_state["username"])
        
        if st.session_state["username"] in st.secrets["passwords"]:
            
            if hmac.compare_digest(st.session_state["password"], st.secrets.passwords[st.session_state["username"]]):
                st.session_state["password_correct"] = True
                del st.session_state["password"]  # Don't store the username or password.
                del st.session_state["username"]

            else:
                st.session_state["password_correct"] = False
                

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.write(st.sessions_state)
        st.error("😕 User not known or password incorrect")
    return False

def add_visitor(file, data, container):
    
    df = pd.read_csv(file, sep=";")
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(file, sep=";", index=False)

    container.info(f"Informations concernant {data['farm']} dans le dept. {data['dept']} bien enregistrées le {data['date'].split(',')[0]} à {data['date'].split(',')[1]}.", icon="ℹ️")

def geocode_adr(adr, country='France'):
   
    geolocator = Nominatim(user_agent="visitus")
    location = geolocator.geocode(f'{adr}, {country}')

    return location.latitude, location.longitude

def show_map(df, container):  

    # create the maps

    scope = 'europe'
    projection = 'natural earth'
    theme = 'plotly_dark'

    if theme == "plotly_dark":
        country_color = "darkgray"
        ocean_color="LightBlue"
    else:
        country_color = "darkgray"
        ocean_color="LightBlue"

    fig = px.scatter_geo(
                    df,
                    lon='lon',
                    lat='lat',
                    text = None,
                    hover_data= {"farm":True, "name":True, "lat":False, "lon":False},    
                    scope= scope,         
                    projection=projection,
                    template = theme,
                                
                )
    
    
    fig.update_geos(fitbounds="locations",
                    resolution=50,
                    showcoastlines=True, coastlinecolor="White",
                    showland=True, landcolor="DarkGray",
                    showlakes=False, lakecolor="Blue",
                    showrivers=False, rivercolor="Blue",
                    showcountries=True, countrycolor=country_color,
                    showocean=True, oceancolor=ocean_color,
                    showsubunits=True, subunitcolor="white"
                )
    
    fig.update_traces(marker=dict(size=8,
                    symbol="circle",
                    color="Cyan",
                    line=dict(width=2,
                    color='lightskyblue',
                    )),
                    opacity=0.8,
                    selector=dict(mode="markers")
                )
    
    fig.update_layout(
                    margin={'r':0, 't':0, 'b':0, 'l':0},
                    template=theme,
                    coloraxis_showscale=False,
                    legend=dict( 
                                x=0, 
                                y=1, 
                                title_font_family="Arial", 
                                font=dict( 
                                family="Arial", 
                                size=12, 
                                color="white"
                                ), 
                    bgcolor="LightBlue", 
                    bordercolor="Black", 
                    borderwidth=1
                    ),
                    hoverlabel=dict(bgcolor="#fff", bordercolor="#fff", font_color="#333", font_size=12, font_family="MS Sans Serif"),
                    geo = dict(
                                showland = True,
                                showcountries=True,
                                countrywidth = 0.75,
                                subunitwidth = 0.5
                            ),
                        )
    
    container.plotly_chart(fig, use_container_width=True)

def show_stats(df, container, criteria):

    container.dataframe(df.sort_values(by=criteria, ascending=True))

def pie_graph(df, fig, wrapper, values, names, title, hole=.5):
        fig = px.pie(df, values=values, names=names, hole=hole, title=title)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        wrapper.plotly_chart(fig)

def hist_graph(df, fig, wrapper, x, color, title, use_container_width=True):
        fig = px.histogram(df, x=x, color=color, title=title)
        wrapper.plotly_chart(fig, use_container_width=use_container_width)

def show_analytics(df, container):
        
        col1, col2, col3 = container.columns(3)
        
        visitor_count = df.shape[0]
        with col1:
            with st.container(border=True):
                st.metric(label="Visiteurs", value=visitor_count, delta=None, help=None, label_visibility="visible")

        dept_count = df['dept'].nunique()
        with col2:
            with st.container(border=True):
                st.metric(label="Départements", value=dept_count, delta=None, help=None, label_visibility="visible")

        dept_sales = df['sales'].nunique()
        with col3:
            with st.container(border=True):
                st.metric(label="Donateurs", value=dept_sales, delta=None, help=None, label_visibility="visible")
        
        with container.container(border=True): 

            col_pg1, col_pg2 = st.columns(2)
            col_hist1, col_hist2 = st.columns(2)

            fig_pg1, fig_pg2 = None, None
    
            pie_graph(df, fig_pg1, col_pg1, "dept", "dept", "Visiteurs par département")

            hist_graph(df, fig_pg2, col_pg2, "product", "product", "Types de projet")
            
            fig_hist1, fig_hist2 = None, None

            hist_graph(df, fig_hist1, col_hist1, "sales", "sales", "Visiteurs par SAM")

            hist_graph(df, fig_hist2, col_hist2, "date", None, "Visiteurs par date & heure")
 
def main():
        
    controller = CookieController()
    user_cookie = controller.get('usr')

    if not check_password(controller):
        st.write("Y'a un bug!")
        #st.stop()
    
    st.write(f'Bienvenue {user_cookie}')

    if user_cookie is not None:
        logo = user_logo[user_cookie]
        db = user_db[user_cookie]

    # App lay-out
    header = st.container(border=False)
    
    content = st.container(border=False)
    
    footer = st.container(border=False)
    footer.write("YM - 2024")

    with st.sidebar:

        st.image(logo, width=141)

        sb_menu = option_menu('Menu', 
                                        ['Add visitor', 'Map', 'Analytics'], 
                                        icons=['folder-symlink', 'map', 'activity'], 
                                        menu_icon='cast', default_index=0)

    if sb_menu == "Add visitor":

        header.image(logo ,width=141)
        header.subheader('Nouveau Visiteur')

        sam = content.selectbox("SAM", ['...', 'Fabien', 'Marine', 'Sébastien', 'Silvia', 'Sophie', 'Yann'])

        if sam != "...":

            now = datetime.datetime.now()
            date_now = content.text_input('date', value = now.strftime("%d/%m/%Y, %H:%M:%S"))
            farm = content.text_input('Elevage')
            name = content.text_input('Nom')
            address = content.text_input('Adresse')
            zip = content.text_input('Code postal')
            dept = zip[:2] # Extract dept. number from zip code
            liste_ville = search_city(zip) # Search city name out of zipcode
            city = content.selectbox("Ville", liste_ville)
            mobile = content.text_input('Mobile')
            cows = content.text_input('Nb vaches laitières')
            milking_eqt = content.selectbox("Equipement actuel", eqt_list)
            brand = content.selectbox("Marque actuelle", brand_list)
            product = content.multiselect("Intéressé par", prod_list)

            content.write("Règles sur le traitement de vos données à lire [ici](%s) " % terms_and_conditions_fj)
            gdpr_agreed = content.checkbox("J'ai lu les conditions et j'accepte le traitement de mes données par FullwoodJoz.", value=True)

            if gdpr_agreed:

                submit = content.button('Valider')
            
                if submit:                
    
                    if address is not None:
                        adr = f'{address}, {zip}, {city}'
                    else:
                        adr = f'{zip}, {city}'
    
                    lat, lon = geocode_adr(adr)
    
                    if (lat!=None) and (lon!=None):
    
                        data_dict = {
                            'date' : date_now,
                            'sales' : sam,
                            'farm': farm,
                            'name': name,
                            'address': address,
                            'zip': zip,
                            'dept': dept,
                            'city': city,
                            'mobile': mobile,
                            'cows': cows,
                            'eqt': milking_eqt,
                            'brand': brand,
                            'product': product,
                            'lat':lat,
                            'lon':lon,
                            }
                        
                        add_visitor(db, data_dict, content)
            else:

                content.warning('Vous devez accepter les conditions sur la vie privée.', icon="⚠️")             

    if sb_menu == "Map":

        header.subheader('Geomapping visiteurs')

        df_map = pd.read_csv(db, sep=";")

        show_map(df_map, content)

        criteria = content.selectbox("Critère", df_map.columns, index=5)
        show_stats(df_map, content, criteria)

    if sb_menu == "Analytics":

        header.subheader('Statistiques visiteurs')

        df_analytics = pd.read_csv(db, sep=";")

        show_analytics(df_analytics, content)
       
    
if __name__ == "__main__":
    main()    
