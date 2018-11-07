import os
import json
import colorama
from colorama import Fore, Back, Style
colorama.init()

# TODO : INSTEAD OF USING COLORAMA USE .COLOR as USED IN FORMATTER.PY
# TODO : EDIT THE ERROR.JSON PROPERLY TO SHOW PROPER ERRORS
# TODO : EDIT THE CODE TO SHOW ERRORS PROPERLY
# TODO : LOG ALL ERROS ON SENTRY IF INTERNET IS ON
# TODO : SUBMIT A PLUGIN TO THE MAIN PYPY REPOSITORY - https://medium.freecodecamp.org/how-to-publish-a-pyton-package-on-pypi-a89e9522ce24

def trans(title):
	f = open(os.path.join(os.path.dirname(__file__), 'error.json'), "r")
	s = f.read()
	errors = json.loads(s)
	i = 0
	
	while i>=0:
		error = ""
		if str(errors["values"][i]["from"]) in title:
			error = str(errors["values"][i]["to"])
			error = (Fore.RED + error + Style.RESET_ALL)
			title = title + error + "\n"
			return  title
		# else: 
		# 	return title	
		i +=1