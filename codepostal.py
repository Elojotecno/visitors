#!/usr/bin/env python3
# -*- coding:Utf-8 -*- 

# script python3 utilisant l'API geo.api.gouv.fr
# afin de retourner le code postal d'une ville envoyé en argument.
# mazarie29@openmailbox.org

import sys
import json
import urllib.request

### Fonctions

class GouvExo():

	def __init__(self, params):
		self.commune = params[1]
		self.api_base = 'https://geo.api.gouv.fr/'

	def what_commune(self):
		print ("La commune demandée est: ", self.commune)

	def get_url(self):
		url = self.api_base + 'communes?nom=' + self.commune
		return url

	def recup_json(self):
		url = self.api_base + 'communes?nom=' + self.commune
		cnx = urllib.request.urlopen(url)
		contenu = cnx.read().decode('utf8')
		json_lisible = json.loads(contenu)
		return json_lisible

	def recup_infos(self, infos_liste):
		noms = []
		for info in infos_liste:
			noms.append(info['codesPostaux'])
		return noms

	def print_list(self, ma_liste):
		for obj in ma_liste:
			print (obj)

	def fait_details(self):
		result = []
		for obj in self.recup_json():
			x = {
				'nom': obj['nom'],
				'code postal': obj['codesPostaux'],
				'Numéro du département': obj['codeDepartement'],
				'La population est de': obj['population'],
			}
			result.append(x)
		return result

	def affiche_details(self):
		for details in self.fait_details():
			print ("nom".ljust(20), ":", details['nom'])
			del details['nom']
			for key,value in details.items():
				print (key.capitalize().ljust(20), ":", str(value).capitalize())
			print ("")


### Exécution

exo = GouvExo(sys.argv)
exo.what_commune()
print (exo.get_url())
json_list = exo.recup_json()
noms = exo.recup_infos(json_list)
# exo.print_list(noms)
exo.affiche_details()