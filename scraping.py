
import csv
from bs4 import BeautifulSoup
import requests
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import urllib.parse

urls = ["https://www.jumia.com.tn/smartphones/",
        "https://www.jumia.com.tn/smartphones/?page=2#catalog-listing",
        "https://www.jumia.com.tn/smartphones/?page=3#catalog-listing",
        "https://www.jumia.com.tn/smartphones/?page=4#catalog-listing",
        "https://www.jumia.com.tn/smartphones/?page=5#catalog-listing",
        "https://www.jumia.com.tn/smartphones/?page=6#catalog-listing",
        "https://www.jumia.com.tn/smartphones/?page=7#catalog-listing"]
all_urls = []

with open('products.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Brand', 'Name', 'Price', 'Image', 'Link'])
    for url in urls:
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        products = soup.find_all('article', class_='prd _fb col c-prd')
        all_urls.extend(products)
        for product in products:
            brand = product.find("a", class_='core')["data-brand"]
            name = product.find("h3", class_='name').text
            price = product.find("div", class_='prc').text
            price = float(price.replace(",", "").rstrip("TND"))
            image = product.find("img", class_='img')["data-src"]
            link = product.find("a", class_="core")['href']
            link = "https://www.jumia.com.tn/smartphones/" + link
            writer.writerow([brand, name, price, image, link])

brands = list(set([row.find("a", class_='core')["data-brand"] for row in all_urls]))

# Créer l'application Dash
app = dash.Dash(name, external_stylesheets=['https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css'])
app.layout = html.Div([
    html.H2('Smartphones :', className='display-4 mt-3 mb-5'),
    html.Label('Marque : ', className='lead'),
    dcc.Dropdown(
        id='dropdown-brand',
        options=[{'label': brand, 'value': brand} for brand in brands],
        value=brands[0],
    ),
    html.Label('Prix maximal : ', className='lead'),
    dcc.Input(
        id='input-price',
        type='number',
        placeholder='Entrez un prix maximal valide',
        className='form-control mb-3'
    ),
    html.Button('Rechercher', id='button-search', n_clicks=0, className='btn btn-success mb-5'),
    html.Div(id='output-table')
])


def generate_jumia_url(phone):
    query_params = {'q': phone['Name']}
    encoded_params = urllib.parse.urlencode(query_params)
    url = f'https://www.jumia.tn/catalog/?{encoded_params}'
    return url


def display_all_phones():
    phone_rows = []
    for product in all_urls:
        brand = product.select_one("a.core")["data-brand"]
        name = product.select_one("h3.name").text
        price = product.select_one("div.prc").text
        image = product.select_one("img.img")["data-src"]
        link = "https://www.jumia.com.tn/smartphones/" + product.select_one("a.core")['href']
        phone = {
            "Brand": brand,
            "Name": name,
            "Price": price,
            "Image": image,
            "Link": link
        }
        phone_rows.append(html.Tr([
            html.Td(html.Img(src=image, style={'height': '100px'})),
            html.Td(brand),
            html.Td(name),
            html.Td(price),
            html.Td(html.A('Voir sur Jumia', href=generate_jumia_url(phone), target='_blank'))
        ]))

    return html.Table([
        html.Thead(html.Tr([
            html.Th('Image'),
            html.Th('Marque'),
            html.Th('Nom'),
            html.Th('Prix'),
            html.Th('Lien Jumia')
        ])),
        html.Tbody(phone_rows)
    ], className='table')





# Définir la fonction de callback pour afficher le tableau
@app.callback(Output('output-table', 'children'),
              [Input('button-search', 'n_clicks')],
              [State('dropdown-brand', 'value'),
               State('input-price', 'value')])
def display_table(n_clicks, marque, max_price):
    if n_clicks == 0:
        return display_all_phones()

    # Le reste du code pour filtrer les smartphones
    # ...

    # Filtrer les données pour correspondre à la marque et au prix maximal sélectionnés
    with open('products.csv', 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        filtered_data = [row for row in reader if row['Brand'] == marque and float(row['Price']) <= float(max_price)]

    # Si aucune donnée ne correspond aux critères, afficher un message d'erreur
    if not filtered_data:
        return html.Div('Aucun téléphone trouvé.')

    # Créer une liste d'éléments HTML pour chaque smartphone correspondant
    phone_rows = []
    for phone in filtered_data:
        phone_rows.append(html.Tr([
            html.Td(html.Img(src=phone['Image'], style={'height': '100px'})),
            html.Td(phone['Brand']),
            html.Td(phone['Name']),
            html.Td(phone['Price']),
            html.Td(html.A('Voir sur Jumia', href=generate_jumia_url(phone), target='_blank'))
        ]))

    # Afficher le tableau des smartphones correspondants
    return html.Table([
        html.Thead(html.Tr([
            html.Th('Image'),
            html.Th('Marque'),
            html.Th('Nom'),
            html.Th('Prix'),
            html.Th('Lien Jumia')
        ])),
        html.Tbody(phone_rows)
    ], className='table')


# Lancer l'application Dash
if __name__ == '__main__':
    app.run_server(debug=True)