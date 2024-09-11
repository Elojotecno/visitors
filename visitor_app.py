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

prod_list = ['M²erlin', 'Barn-E', 'Nano', 'Moov', 'Racleur', 'Autre']
eqt_list = ['SBS', 'HB', 'Rotary', 'Robot', 'Autre']
brand_list = ['Boumatic', 'Delaval', 'Fullwood', 'Gascoigne-Melotte', 'GEA', 'Lely', 'Manus', 'Surge', 'Autre']
file = "./data/visitors.csv"
terms_and_conditions_fj = "https://www.fullwoodjoz.com/fr/terms-and-conditions/"

st.set_page_config(layout="wide")

def check_password(controller):
    
    def login_form():
        
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():

        controller.set('usr', st.session_state["username"])
        
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
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
        st.error("😕 User not known or password incorrect")
    return False


def add_visitor(file, data, container):
    
    df = pd.read_csv(file, sep=",")
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(file, index=False)

    container.info(f"Informations concernant {data['farm']} dans le dept. {data['dept']} bien enregistrées.", icon="ℹ️")

def geocode_adr(adr, country='France'):
   
    geolocator = Nominatim(user_agent="visitus")
    location = geolocator.geocode(f'{adr}, {country}')
    #st.write(location.address)
    #st.write(location.raw)

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

def show_stats(df, container):

    df = pd.read_csv(file, sep=",")
    container.dataframe(df.sort_values(by='name', ascending=True))

def show_analytics(df, container):

    df = pd.read_csv(file, sep=",")
    visitor_count = df['sales'].value_counts()
    container.metric(label="Visiteurs", value=visitor_count)
    
def main():
        
    controller = CookieController()
    user_cookie = controller.get('usr')

    if not check_password(controller):
        st.stop()
    
    st.write(f'Bienvenue {user_cookie}')

    # App lay-out
    header = st.container(border=False)
    header.image('img/fjm.png')

    content = st.container(border=False)
    
    footer = st.container(border=False)
    footer.write("YM - 2024")

    with st.sidebar:

        sb_menu = option_menu('Options', 
                                        ['Add visitor', 'Map', 'Analytics'], 
                                        icons=['folder-symlink', 'map', 'activity'], 
                                        menu_icon='cast', default_index=0)

    if sb_menu == "Add visitor":

        header.subheader('Nouveau Visiteur')

        sam = content.selectbox("SAM", ['...', 'Fabien', 'Marine', 'Sébastien', 'Silvia', 'Sophie', 'Yann'])
        

        if sam != "...":

            farm = content.text_input('Elevage')
            name = content.text_input('Nom')
            address = content.text_input('Adresse')
            zip = content.text_input('Code postal')
            dept = zip[:2]
            city = content.text_input('Ville')
            mobile = content.text_input('Mobile', value="")
            cows = content.number_input('VL', value=None, placeholder="Ajouter un nombre...")
            milking_eqt = content.selectbox("Eqt. actuel", eqt_list)
            brand = content.selectbox("Marque", brand_list)
            product = content.selectbox("Projet", prod_list)
            submit = content.button('Valider')

            content.write("Règles sur le traitement de vos données à lire [ici](%s) " % terms_and_conditions_fj)
            gdpr_agreed = content.checkbox("J'ai lu les conditions et j'accepte le traitement de mes données par FullwoodJoz.")

            if gdpr_agreed:
            
                if submit:                
    
                    if address is not None:
                        adr = f'{address}, {zip}, {city}'
                    else:
                        adr = f'{zip}, {city}'
    
                    lat, lon = geocode_adr(adr)
    
                    if (lat!=None) and (lon!=None):
    
                        data_dict = {
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
                        
                        add_visitor(file, data_dict, content)
            else:

                content.warning('Vous devez accepter les conditions sur la vie privée.', icon="⚠️")
                    

    if sb_menu == "Map":

        header.subheader('Geomapping visiteurs')
        
        df = pd.read_csv(file, sep=",")
        show_map(df, content)
        show_stats(df, content)

    if sb_menu == "Analytics":

        header.subheader('Statistiques visiteurs')
        show_analytics(df, content)
       
    

if __name__ == "__main__":
    main()    

   

