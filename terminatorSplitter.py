#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import random
import string
import shutil
import os
import getopt

VP=0
HP=1
NUMEROQUELLEVA=1
COMANDOBASE="ssh "
USUARIOCOMANDOBASE=None
PATHFICHEROCLAVE=None
DELIMITADOR="_@_"

def usage():
	sys.stderr.write("USAGE: " + sys.argv[0] + " [-l nombreUsuario][-i ficheroClavePrivada] servidor1 servidor2 ... servidorN\n")
	sys.stderr.write("\n")
	sys.stderr.write("Puedes usar una sintaxis especial para que las máqunas estén en grupos diferentes:\n")
	sys.stderr.write("\t - " + sys.argv[0] + " grupo1" + DELIMITADOR + "nombreMaquina1 grupo1" + DELIMITADOR + "nombreMaquina2 nombreMaquina3\n" )
	sys.stderr.write("\t Creará 3 separaciones, Maquína1 y Maquina2 pertenecerán al grupo grupo1 y Maquina3 al grupo por defecto\n")
	sys.stderr.write("\n")
	sys.stderr.write("Se recomienda no poner demasiados servidores para evitar problemas de visualización\n")
	sys.stderr.write("Es necesario tener el fichero \"config\" de terminator, por defecto en $HOME/.config/terminator/config.\n")
	sys.stderr.write("Para forzar que lo cree, basta con hacer algo en la personalización de terminator en la herramienta web\n")

def tratarOpciones(vector):
	try:
		opts, args = getopt.getopt(vector, "hi:l:",["help"])
	except getopt.GetoptError:
		usage()
		raise SystemExit
	for opt, arg in opts:
		if (opt in ("-h","--help")):
			usage()
			sys.exit()
		elif (opt == "-i"):
			if (arg == None):
				usage()
				raise SystemExit
			global PATHFICHEROCLAVE
			PATHFICHEROCLAVE=arg
		elif (opt == "-l"):
			if (arg == None):
				usage()
				raise SystemExit
			global USUARIOCOMANDOBASE
			USUARIOCOMANDOBASE=arg
	return args

def cadenaAleatoria():
	return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range (5))

def partelo(restantes, padre, ordenParaMiPadre, tipoDeSplit):
	# recibe
	# restantes: los que tenemos que crear
	# padre: nombre del padre
	# ordenParaMiPadre: 0 o 1 indicando si eres el 0 o el 1 de tu padre
	# tipoDeSplit: 1 si vamos a hacer un split Horizontal 0 si sera uno vertical

	global NUMEROQUELLEVA
	global fw
	miNumero=NUMEROQUELLEVA
	NUMEROQUELLEVA = NUMEROQUELLEVA + 1

	if (restantes == 1):
		servidorAux = listaServidores.pop()
		# si existe el delimitador lo tratamos para coger el nombre como grupo
		if servidorAux.find(DELIMITADOR)!=-1:
			grupoAux=servidorAux.split(DELIMITADOR)[0]
			# si en lo que nos queda, hay @ es porque lleva usuario con el servidor
			if grupoAux.find('@')!=-1:
				grupo=grupoAux.split('@')[1]
				servidor=str.join('@',[grupoAux.split('@')[0],servidorAux.split(DELIMITADOR)[1]])
			else:
				grupo=grupoAux
				servidor=servidorAux.split(DELIMITADOR)[1]
		else:
			grupo="grupoTrabajo"
			servidor=servidorAux

		fw.write("    [[[terminal" + str(miNumero) + "]]]\n")
		fw.write("      profile = default\n")
		fw.write("      command = " + COMANDOBASE + servidor + ";bash\n")
		fw.write("      group = " + grupo + "\n")
		fw.write("      type = Terminal\n")
		fw.write("      order = " + str(ordenParaMiPadre) + "\n")
		fw.write("      parent = " + padre + "\n")
	else:
		idAux="child" + str(miNumero)
		fw.write("    [[["+idAux+"]]]\n")
		if (tipoDeSplit == HP):
			fw.write("      type = HPaned\n")
		else:
			fw.write("      type = VPaned\n")
		fw.write("      order = " + str(ordenParaMiPadre) + "\n")
		fw.write("      parent = " + padre + "\n")
		numero1=restantes / 2
		numero0=restantes - numero1
		siguienteSplit=(tipoDeSplit + 1) % 2

		partelo(numero0, idAux, 0, siguienteSplit)
		partelo(numero1, idAux, 1, siguienteSplit)
	return 0

listaServidores = tratarOpciones(sys.argv[1:])
# trato los flag para ver si modifico el SSH por defecto
if USUARIOCOMANDOBASE:
	COMANDOBASE = COMANDOBASE + "-l " + USUARIOCOMANDOBASE + " "

if PATHFICHEROCLAVE:
	COMANDOBASE = COMANDOBASE + "-i " + PATHFICHEROCLAVE + " "

if (len(listaServidores) < 1):
	sys.stderr.write("Numero de argumentos incorrecto\n")
	usage()
	raise SystemExit

if not os.path.exists(os.getenv("HOME") + "/.config/terminator/config"):
	sys.stderr.write("No existe el fichero de configuración predeterminado de terminator\n")
	usage()
	raise SystemExit

#Preparo el fichero auxiliar para no estropear el config del usuario
ficheroAux="config." + cadenaAleatoria()
layoutAux="mlaraLayout-" + cadenaAleatoria()

shutil.copy2(os.getenv("HOME") + "/.config/terminator/config", os.getenv("HOME") + "/.config/terminator/"+ficheroAux)

#Ahora copiamos el contenido que tenía el fichero
fr = open(os.getenv("HOME") + "/.config/terminator/"+ficheroAux, "r")
fw = open(os.getenv("HOME") + "/.config/terminator/config", "w")
while True:
	linea = fr.readline()
	if not linea:
		break
	if linea == "[plugins]\n":
		fw.write("  [[" + layoutAux + "]]\n")
		fw.write("    [[[child0]]]\n")
		fw.write("      type = Window\n")
		fw.write("      order = 0\n")
		fw.write("      parent = \"\"\n")
		partelo(len(listaServidores), "child0", 0, VP)

	fw.write(linea)


fr.close()
fw.close()

os.system("terminator -l " + layoutAux)
#volvemos a poner el config que había antes
shutil.move(os.getenv("HOME") + "/.config/terminator/"+ficheroAux, os.getenv("HOME") + "/.config/terminator/config")

