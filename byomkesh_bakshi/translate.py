import os
import json
import colorama
from colorama import Fore, Back, Style
colorama.init()

# TODO : INSTEAD OF USING COLORAMA USE .COLOR as USED IN FORMATTER.PY
# TODO : LOG ALL ERROS ON SENTRY IF INTERNET IS ON
# TODO : SUBMIT A PLUGIN TO THE MAIN PYPY REPOSITORY - https://medium.freecodecamp.org/how-to-publish-a-pyton-package-on-pypi-a89e9522ce24

def trans(title):
	f = open(	os.path.join(os.path.dirname(__file__), 'error.json'), "r")
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


# import re
# import colorama
# from colorama import Fore, Back, Style
# colorama.init()

# def trans(title,exc):
	
# 	eol= "SyntaxSahiNahiError: jo aapne Syntax liya hai wo sahi nahi hai"
# 	parentheses = "SyntaxSahiNahiError:  aapne parentheses() nahi liya hai jese print(variable ka nam)"
# 	Nameerror = "NaamNahiHaiError: ye naam undefined hai ye defined nahi kiya hai aapne"
# 	indexError = "IndexError: list ka index jo aapne defined kiya hai usse jada hai"
# 	invalidSyntax = "SyntaxError: Appne jo Syntax liya hai wo galat hai"
# 	with open('error.json') as fileObject:
# 		fileContents = fileObject.read()
# 		r = json.loads(fileContents)
# 		print(type(r))
# 		rahul = "sahi hai"
# 		for i in r["values"]:
# 			if i['from'] == str(exc):
#         		print (i)
# 		# print (r)
# 	if "NameError:" in title:
# 		# if "NameError" in r:
# 		Nameerror = (Fore.RED + Nameerror + Style.RESET_ALL)
# 		title = title + Nameerror + i +"\n"
# 		return title

# 	elif "IndentationError:" in title:
# 		indentation = "AapneGalatSpaceDiyaHaiError:Aapke code ki formatting theek nahi hai. Aapko apne code ki indentation (yaani spacing) theek karo, jisse ki python aapke code ko samajh jayein."
# 		indentation = (Fore.RED + indentation + Style.RESET_ALL)
# 		title = title + indentation + "\n"
# 		return title


# 	elif "IndexError:" in title:
# 		indexError = (Fore.RED + indexError + Style.RESET_ALL)
# 		title = title + indexError + "\n"
# 		return title

# 	elif "SyntaxError:" in title:
# 		if "EOL" in title:
# 			eol = (Fore.RED + eol + Style.RESET_ALL)
# 			title = title + eol + "\n"
# 			return title

# 		elif "Missing parentheses" in title:
# 			parentheses = (Fore.RED + parentheses + Style.RESET_ALL)
# 			title = title + parentheses + "\n"
# 			return title

# 		elif "invalid syntax" in title:
# 			invalidSyntax = (Fore.RED + invalidSyntax + Style.RESET_ALL)
# 			title = title + invalidSyntax + "\n"
# 			return title


# 	elif "TypeError:" in title:
# 		if "TypeError: 'list' object cannot be interpreted as an integer" in title:
# 			typeError = "SahiTypeError:  aapko isko number mai defined nahi kr sakte ho"
# 			typeError = (Fore.RED + typeError + Style.RESET_ALL)
# 			title = title + typeError + "\n"
# 			return title
		
# 		elif "TypeError: 'range'" in title:
# 			typeError = "TypeError:  aap = equl ko variable ko defined karne ke liye nahi kar sakte ho ye support nahi karta hai"
# 			typeError = (Fore.RED + typeError + Style.RESET_ALL)
# 			title = title + typeError + "\n"
# 			return title

# 		elif "TypeError: myMethod() takes 0 positional arguments but 1 was given" in title:
# 			typeError = "TypeError:  function mai ek value bejni padegi aapko"
# 			typeError = (Fore.RED + typeError + Style.RESET_ALL)
# 			title = title + typeError + "\n"
# 			return title

# 		typeError = "SahiTypeError: jo variable aapne defined kiya hai wo support nahi krta hai jesa aap chahte ho"
# 		typeError = (Fore.RED + typeError + Style.RESET_ALL)
# 		title = title + typeError + "\n"
# 		return title

# 	elif "TabError:" in title:
# 		tabError = "TabError: aapne TabKey or spaceKey ka use galat kiya hai usko sahi karo"
# 		tabError = (Fore.RED + tabError + Style.RESET_ALL)
# 		title = title + tabError + "\n"
# 		return title

# 	elif "FileNotFoundError:" in title:
# 		fileNotFoundError = "FileNotFoundError: file nahi mil rahi hai"
# 		fileNotFoundError = (Fore.RED + fileNotFoundError + Style.RESET_ALL)
# 		title = title + fileNotFoundError + "\n"
# 		return title


# 	elif "UnsupportedOperation:" in title:
# 		unsupportedOperation = "UnsupportedOperation: ye operation support nahi karta hai isko pad nahi sakte"
# 		unsupportedOperation = (Fore.RED + unsupportedOperation + Style.RESET_ALL)
# 		title = title + unsupportedOperation + "\n"
# 		return title

# 	elif "KeyError:" in title:
# 		keyError = "KeyError: aapki key sahi nahi hai"
# 		keyError = (Fore.RED + keyError + Style.RESET_ALL)
# 		title = title + keyError + "\n"
# 		return title																										
	
# 	elif "AttributeError:" in title:
#    		attributeError = "AttributeError: ye oject nahi hai"
#    		attributeError = (Fore.RED + attributeError + Style.RESET_ALL)
#    		title = title + attributeError + "\n"
#    		return title

# 	elif "UnboundLocalError:" in title:
#    		unboundLocalError = "UnboundLocalError: aapne defined karne se phele variable ka use kiya hai"
#    		unboundLocalError = (Fore.RED + unboundLocalError + Style.RESET_ALL)
#    		title = title + unboundLocalError + "\n"
#    		return title

# 	return title																	

# 	# if "NameError:" in title:
# 	# 	title = (re.sub("NameError: name", "NaamNahiHaiError: ye naam ", title))
# 	# 	title = (re.sub("is not defined", " undefined hai ye defined nahi kiya hai aapne", title))
# 	# 	rahul = (Fore.GREEN + Back.RED + rahul + Style.RESET_ALL)
# 	# 	title = title + rahul
# 	# 	return title 


# 	# elif "IndexError:" in title:
# 	# 	title = (re.sub("list index out of range", "list ka index jo aapne defined kiya hai usse jada hai", title))
# 	# 	return title																																																																																			


# 	# elif "IndentationError:" in title:
# 	# 	title = (re.sub("IndentationError: unexpected indent",indentation, title))
# 	# 	return title
		

# 	# elif "SyntaxError:" in title:
# 	# 	if "EOL" in title:
# 	# 		title = (re.sub("SyntaxError: EOL while scanning string literal", eol, title))
# 	# 		return title

# 	# 	elif "Missing parentheses" in title:
# 	# 		title = (re.sub("SyntaxError: Missing parentheses in call to 'print'. Did you mean print(a)?", parentheses, title))
# 	# 		return title


# 	# elif "TypeError:" in str(title):
# 	# 	title = re.sub("TypeError: unsupported operand","SahiTypeError: jo variable aapne defined kiya hai wo support nahi krta hai",title)
# 	# 	title = re.sub("for","ke liye",title)
# 	# 	title = re.sub("and","or",title)
# 	# 	return title



# 	# return title


# 	#start formatter.py

# 	#title = trans(title)
#         # str1 = ' '.join(str(e) for e in title)
#         # list = str1.split (' ')
#         # title = list

#         # if title[0] == "NameError:":
#         #     for i in range(0,len(title)-1):
#         #         if title[i] == 'NameError:':
#         #             title.pop(i)
#         #             title.insert(i, 'NaamNahiHaiError:') 
#         #         elif title[i] == 'is':
#         #             title.pop(i)
#         #             title.insert(i, 'ye')
#         #         elif title[i] == 'not':
#         #             title.pop(i)
#         #             title.insert(i, 'defined nhi')
#         #     title.pop()
#         #     title.append('kiya hai aapne')

#         # elif "IndentationError:" in title:
#         #     for i in range(0,len(title)-1):
#         #         if title[i] == 'IndentationError:':
#         #             title.pop(i)
#         #             title.insert(i, 'AapneGalatSpaceDiyaHaiError:') 
#         #         elif title[i] == 'unexpected':
#         #             title.pop()
#         #             title.insert(i, 'aapne space galat de rakha hai')
#         #     title.pop()
#         #     title.append('aapne jo space galat diya hai usko sahi karo')


#         # elif "IndexError:" in title:
#         #     for i in range(0,len(title)-1):
#         #         if title[i] == 'list':
#         #             title.pop(i)
#         #             title.insert(i, 'list ka') 
#         #         elif title[i] == 'out':
#         #             title.pop()
#         #             title.insert(i, 'jo aapne')
#         #         elif title[i] == 'of':
#         #             title.pop()
#         #             title.insert(i, 'usse')
#         #     title.pop()
#         #     title.append('bhar hai aap usko sahi kar sakte ho')
#         # end
