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
import os.path
import math
import webcolors

menu_options = ['Nouveau visiteur']
menu_options_admin = ['Nouveau visiteur', 'Carte', 'Données', 'Téléchargements']
menu_icon = ['folder-symlink']
menu_icon_admin = ['folder-symlink', 'map', 'activity', 'download']
users_list = {"FullwoodJoz" : ['...', 'Fabien', 'Marine', 'Sébastien', 'Silvia', 'Sophie'], "Transfaire" : ["Transfaire"], "Admin" : ["Admin"]}
prod_list = ['M²erlin', 'Barn-E', 'Nano', 'Moov', 'Racleur', 'Autre']
eqt_list = ['TPA', 'Epi', 'Roto', 'Robot', 'Autre']
brand_list = ['Boumatic', 'Delaval', 'Fullwood', 'Gascoigne-Melotte', 'GEA', 'Lely', 'Manus', 'Surge', 'Autre']
user_db = {"FullwoodJoz" : "./data/fj_visitors.csv", "Transfaire" : "./data/trf_visitors.csv", "Admin" : "./data/fj_visitors.csv"}
user_logo = {"FullwoodJoz" : "./img/fjm.png", "Transfaire" : "./img/transfaire.png", "Admin" : "./img/fjm.png"}
terms_and_conditions_fj = "https://www.fullwoodjoz.com/fr/terms-and-conditions/"
data_dir= './data/'
empty_data = {
                            'date' : None,
                            'sales' : None,
                            'farm': None,
                            'name': None,
                            'address': None,
                            'zip': None,
                            'dept': None,
                            'city': None,
                            'mobile': None,
                            'cows': None,
                            'eqt': None,
                            'brand': None,
                            'product': None,
                            'lat':None,
                            'lon':None,
                            }
lst_colors = ["aliceblue", "blueviolet", "cornflowerblue",
"cyan", "darkblue", "darkcyan",
"darkgoldenrod", "darkgray", "darkgrey", "darkgreen",
"lightblue", "lightcoral", "lightcyan",
"lightgoldenrodyellow", "lightgray", "lightgrey",
"lightgreen", "lightpink", "lightsalmon", "lightseagreen",
"lightskyblue", "lightslategray", "lightslategrey",
"lightsteelblue", "lightyellow", "lime", "limegreen",
"linen", "magenta", "maroon", "paleturquoise",
"palevioletred", "papayawhip", "peachpuff", "peru", "pink",
"plum", "powderblue", "purple", "red", "skyblue",
"tomato", "violet", "whitesmoke", "yellow", "yellowgreen"]

               
st.set_page_config(layout="wide")

def legend_layout(df, content, column, max_cols, colors, options_type):

    # Create a map legend layout showing selected items, number of occurences per item and associated color

    with content.container(border=False):

        layout_rows = math.ceil(len(options_type)/max_cols)
        
        for row in range(layout_rows):
            
            # set the start index in the list
            start_index = max_cols * row
            #Extract the options before loop
            options = options_type[start_index:start_index + max_cols]

            with st.container(border=False):

                columns = st.columns(max_cols+1)

                for index, option in enumerate(options):
                    
                    with columns[index+1]:
    
                        #Create color legend tile
                        legend = f" {option} ({str(len(df[df[column] == option]['name']))})"
                        st.color_picker(legend, webcolors.name_to_hex(colors[option]), key="color_picker_"+str(index)+str(row), disabled=False)
                        
def color_picker(df, column, content):

    # Assign a color to each selected column item

    options_type = content.multiselect("Pick up one or more categories", list(df[column].unique()), list(df[column].unique()), key="cat")
    colors={}

    if options_type != None:
        df = df[df[column].isin(options_type)]

        for index, option in enumerate(options_type):
            
            #Create color selectbox per type
            with st.expander("Réglages couleurs", expanded=False, icon=":material/waving_hand:"):
                colors[option] = content.selectbox(str(option), lst_colors, index=index, key = option)

        if len(colors) != 0:  

            # Create a legend layout showing markers color
            legend_layout(df, content, column, len(list(df[column].unique())), colors, options_type)
                
            # Assign color index to markers and create a new column in dataset
            df['color']= df[column].apply(lambda x: colors[x])
        
        return df

def add_header_content(header_id, logo, title):

    header_id.image(logo)
    header_id.subheader(title)
     
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
            st.selectbox("Utilisateur", ["FullwoodJoz", "Transfaire", "Admin"], key="username")
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

        else:
            st.error("😕 Utilisateur inconnu.")

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    #st.write(st.session_state)
    
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False

def add_visitor(file, data, container):
    
    if os.path.isfile(file):
        df = pd.read_csv(file, sep=";")
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
        container.dataframe(pd.DataFrame([data]))
        df.to_csv(file, sep=";", index=False)
   
    container.info(f"Informations concernant {data['farm']} dans le dept. {data['dept']} bien enregistrées dans {file} le {data['date'].split(',')[0]} à {data['date'].split(',')[1]}.", icon="ℹ️")

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
                    color=df['color'],
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

def show_data(df, container, criteria):

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

def listdir(path):

    list_file = []

    for f in os.listdir(path):

        if len(f) > 5:
            list_file.append(f)


    return list_file

def make_filepath(dir, file):

    filepath = dir + file

    return filepath

def check_df_status(df, container):

    result= False

    if df is not None:

        result = True

        if df.shape[0] == 0:
            result = False
            result = container.info("😕 Pas de données disponible.")
        else:
            result = True
    
    else:
        result = False
        result = container.info("😕 Pas de données disponible.")
    
    return result

def select_dataset(data_dir, content, instr_all="Fusionner"):

    # search datasets in directory and put them in a selectbox
    datasets = listdir(data_dir)

    df_ = None

    if len(datasets) !=0:

        datasets.append(instr_all)
        selected_data = content.selectbox("Données", datasets, index=0)
        master_dataset = make_filepath(data_dir, selected_data)          

        if selected_data == instr_all:

            if len(datasets[:-1]) > 1:

                empty = pd.DataFrame([empty_data])

                for dataset in datasets[:-1]:

                    new = pd.read_csv(make_filepath(data_dir, dataset), sep=";")

                    if df_ is None:
                        df_ = pd.concat([empty, new], ignore_index=True)
                    else:
                        df_ = pd.concat([df_, new], ignore_index=True)
            
            else:
                df_ = pd.read_csv(master_dataset, sep=";")
                    
        else:
            df_ = pd.read_csv(master_dataset, sep=";")

    return df_

def main():
        
    controller = CookieController()
    user_cookie = controller.get('usr')

    # Check security access
    if not check_password(controller):
        st.stop()
    
    # Welcome text
    #st.write(f'{user_cookie}')

    # Create logo and user dataset according to the user
    if user_cookie is not None:

        logo = user_logo[user_cookie]
        db = user_db[user_cookie]

    # App lay-out
    
    # Header
    header = st.container(border=False)
    
    # Body
    content = st.container(border=False)
    
    # Footer
    footer = st.container(border=False)
    footer.write("YM - 2024")

    # Menu sidebar
    with st.sidebar:

        if user_cookie == "Admin":

            sb_menu = option_menu('Menu', 
                                            menu_options_admin, 
                                            icons=menu_icon_admin, 
                                            menu_icon='cast', default_index=0, orientation="vertical")
        else:

            sb_menu = option_menu('Menu', 
                                            menu_options, 
                                            icons=menu_icon, 
                                            menu_icon='cast', default_index=0, orientation="vertical")

    if sb_menu == menu_options[0]:

    
        add_header_content(header, logo, 'Nouveau visiteur')

        sam = content.selectbox("SAM", users_list[user_cookie])

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

    if user_cookie == "Admin":

        if sb_menu == menu_options_admin[1]:

            add_header_content(header, logo, 'Geomapping visiteurs')

            # Search datasets in a directory, create a selectbox of datasets and return a single dataset 
            df_map = select_dataset(data_dir, content)

            # Check that dataset is not None and not empty
            map_check = check_df_status(df_map, content)
            
            if map_check == True:
                map_options = ['sales', 'dept', 'eqt', 'product']
                feature = content.selectbox("Pick up one category", map_options, index=0)
                df_map = color_picker(df_map, feature, content)
                show_map(df_map, content)              


        if sb_menu == menu_options_admin[2]:

            add_header_content(header, logo, 'Statistiques visiteurs')

            # Search datasets in a directory, create a selectbox of datasets and return a single dataset
            df_analytics = select_dataset(data_dir, content)

            # Check that dataset is not None and not empty
            data_check = check_df_status(df_analytics, content)
            
            if data_check == True:
                show_analytics(df_analytics, content)
            
        
        if sb_menu == menu_options_admin[3]:

            add_header_content(header, logo, 'Téléchargements')

            key_index = 0

            with content.container(border=False):

                for f in os.listdir(data_dir):

                    if len(f) > 5:

                        link = make_filepath(data_dir, f)
                        columns = st.columns(2)

                        columns[0].write(link)

                        with open(link) as f:
                            columns[1].download_button('Télécharger le fichier CSV', f, key=key_index)
                            key_index += 1

    
if __name__ == "__main__":
    main()    
