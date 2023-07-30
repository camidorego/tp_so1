import warnings
import subprocess
import os
import time
import signal
import shutil
# import distutils.dir_util
import ftplib
import logging
import psutil # instalar desde la terminal -> pip install psutil
import errno
import socket
import sys
import getpass
from re import split
warnings.filterwarnings("ignore", category=DeprecationWarning)
import crypt
import spwd
from hmac import compare_digest as compare_hash
#registroUsuarios : 2023-01-10 16:01:41,269 : root 192.168.100.78 08:00 12:00
# ---LOGS--- #
	#LEER README PARA INSTALACION Y CREACION DE LOS LOGS
def logRegistroUsuarios(message):
	#creamos/llamamos al log
        log = logging.getLogger('registroUsuarios')
        log.setLevel(logging.INFO)
        #creamos el archivo donde se van a almacenar los registros
        fileHandler = logging.FileHandler('/var/log/shell/registro_usuarios.log')
        fileHandler.setLevel(logging.DEBUG)
        #le damos el formato deseado
        formato = logging.Formatter('%(name)s : %(asctime)s : %(message)s')
        fileHandler.setFormatter(formato)
        #agregamos al log
        log.addHandler(fileHandler)
        #establecemos el mensaje
        log.info(message)
        #cerramos el log
        log.removeHandler(fileHandler)
        fileHandler.flush()
        fileHandler.close()
	
def logErrores(message):
        log = logging.getLogger('systemError')
        log.setLevel(logging.INFO)
        # Abrimos el archivo donde escribimos los logs
        fileHandler = logging.FileHandler('/var/log/shell/sistema_error.log')
        fileHandler.setLevel(logging.ERROR)
        #le damos el formato deseado
        formato = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
        fileHandler.setFormatter(formato)
        #agregamos al log
        log.addHandler(fileHandler)
        #establecemos el mensaje
        log.info(message)
        #cerramos el log
        log.removeHandler(fileHandler)
        fileHandler.flush()
        fileHandler.close()

def logMovimientos(message):
	#creamos/llamamos al log
        log = logging.getLogger('movimientos')
        log.setLevel(logging.INFO)
        #creamos el archivo donde se van a almacenar los registros
        fileHandler = logging.FileHandler('/var/log/shell/registro_movimientos.log')
        fileHandler.setLevel(logging.DEBUG)
        #le damos el formato deseado
        formato = logging.Formatter('%(asctime)s : %(message)s')
        fileHandler.setFormatter(formato)
        #agregamos al log
        log.addHandler(fileHandler)
        #establecemos el mensaje
        log.info(message)
        #cerramos el log
        log.removeHandler(fileHandler)
        fileHandler.flush()
        fileHandler.close()
	
def logTransferencias(status, message):
	#creamos/llamamos al log
        log = logging.getLogger('transferencias')
        log.setLevel(logging.INFO)
        #creamos el archivo donde se van a almacenar los registros
        fileHandler = logging.FileHandler('/var/log/shell/shell_transferencias.log')
        fileHandler.setLevel(logging.DEBUG)
        #le damos el formato deseado
        formato = logging.Formatter('%(asctime)s : %(message)s')
        fileHandler.setFormatter(formato)
        #agregamos al log
        log.addHandler(fileHandler)
        #establecemos el mensaje
        log.info(message)
        #cerramos el log
        log.removeHandler(fileHandler)
        fileHandler.flush()
        fileHandler.close()
    
def logusuarioHorarios(message):
	#creamos/llamamos al log
        log = logging.getLogger('usuariosHorarios')
        log.setLevel(logging.INFO)
        #creamos el archivo donde se van a almacenar los registros
        fileHandler = logging.FileHandler('/var/log/shell/usuarios_horarios.log')
        fileHandler.setLevel(logging.DEBUG)
        #le damos el formato deseado
        formato = logging.Formatter('%(asctime)s : %(message)s')
        fileHandler.setFormatter(formato)
        #agregamos al log
        log.addHandler(fileHandler)
        #establecemos el mensaje
        log.info(message)
        #cerramos el log
        log.removeHandler(fileHandler)
        fileHandler.flush()
        fileHandler.close()

def logRegistroDiario(message):
	#creamos/llamamos al log
        log = logging.getLogger('registroDiario')
        log.setLevel(logging.INFO)
        #creamos el archivo donde se van a almacenar los registros
        fileHandler = logging.FileHandler('/var/log/shell/registro_diario.log')
        fileHandler.setLevel(logging.DEBUG)
        #le damos el formato deseado
        formato = logging.Formatter('%(asctime)s : %(message)s')
        fileHandler.setFormatter(formato)
        #agregamos al log
        log.addHandler(fileHandler)
        #establecemos el mensaje
        log.info(message)
        #cerramos el log
        log.removeHandler(fileHandler)
        fileHandler.flush()
        fileHandler.close()

## VERIFICACIONES
	
#Funcion para validar el formato de la hora		
def validar_horario(hora):
    try:
        datetime.datetime.strptime(hora,'%H:%M')
    except Exception :
        return False
    else:
        return True

#Funcion para validar el user id del usuario
def validar_uid(uid):
	existeuid=0
	with open("/etc/passwd") as file: #Se verifica que el usuario este en la carpeta de usuarios
		for line in file:
			if uid in line: #Se obtiene la linea donde se encuentra la informacion del usuario
				existeuid = 1
	return existeuid

#Funcion que valida el group id	
def validar_gid(gid):
	existegid = 0
	with open("/etc/group") as file:
		for line in file:
			if gid in line: #Se obtiene la linea donde se encuentra la informacion del usuario
				existegid = 1
	return existegid


# Funcion que controla registra el horario de salida y entrada, y verfica los horarios e ips correspondientes
def control_horario(tiempo): 
	# Se obtiene la hora actual en el formato 00:00:00
	hora = time.strftime("%X") 
	hora = hora.split(":")
	hora = hora[0] + "." + hora[1]
	hora = float(hora)
	usuario = getpass.getuser() # Se obtiene el usuario
	linea = []
	try: 
		with open("/var/log/shell/registro_usuarios.log") as file: #Se verifica que el usuario este en la carpeta de usuarios
			for line in file:
				#Se obtiene la linea donde se encuentra la informacion del usuario
				if usuario in line: 
					linea.append(line)
			linea = str(linea) 
		linea = linea.split(sep = " ") # Se quitan los datos de la cadena donde se encuentra la informacion del usuario
		horaInicio = linea[7]
		horaInicio = horaInicio.split(sep = ":")
		horaInicio = horaInicio[0] + "." + horaInicio[1]
		horaInicio = float(horaInicio)
		horaSalida = linea[8]
		horaSalida = horaSalida.split(sep = ":")
		horaSalida = horaSalida[0] + "." + horaSalida[1]
		horaSalida = float(horaSalida[:5])
		ip_oficial = linea[6]
		ip_actual = getIp(0)

		if tiempo==0 :
			if hora < horaInicio or hora > horaSalida: # Se verifica y registra el horario de inicio de sesion
				mensaje = usuario + " inicio sesion fuera del rango del rango horario"
				print(mensaje)
				logusuarioHorarios(mensaje)
			else:
				mensaje = usuario +" :inicio sesion dentro del rango horario"
				print(mensaje)
				logRegistroDiario(mensaje)

			if ip_oficial != ip_actual:
				mensaje = "La ip no esta habilitada, ip: " + ip_actual
				print(mensaje)
				logRegistroDiario(mensaje)

			else: 
				mensaje = "Inicio sesion con la ip habilitada" + ip_actual
				print(mensaje)
				logRegistroDiario(mensaje)

		if tiempo==1 :
			if hora < horaInicio or hora > horaSalida: #Se verifica y registra el horario de cierre de sesion
				mensaje = usuario + " cerro sesion fuera del rango horario"
				print(mensaje)
				logusuarioHorarios(mensaje)
			else:
				mensaje = usuario + " :cerro sesion dentro del rango horario"
				print(mensaje)
				logRegistroDiario(mensaje)

	except:
		print("error")
		
def is_root():
    #Verifica si el usuario es root o tiene los privilegios de root
    #si os.getuid retorna true estonces es usuario root

	if os.getuid() == 0:
		return True
	else:
		return False

# ---COMANDOS--- #

#Funcion para listar un directorio -> listar o listar [path]
def cmdListar(cadena):
	# se listan los archivos del path actual
	if(len(cadena) == 6): 
		# se obtiene el path actual
		path = os.getcwd() 
		# se obtienen los archivos
		lista = os.listdir(path) 
		# se muestran los archivos
		print("Archivos en ", path, ":")
		print(lista)

		# Se guarda en el log de movimientos
		mensaje = "listar: se listaron los archivos de " + path 
		logMovimientos(mensaje)

	# se listan los archivos del path especificado
	else:
		cadena = cadena.split(sep=' ')
		# se guarda el path introducido
		path = cadena[1] 
		# se verifica que el path introducido existe
		if os.path.exists(path):
			# se obtienen los archivos
			lista = os.listdir(path) 
			# se muestran los archivos
			print("Archivos en ", path, ":")
			print(lista)

			# Se guarda en el log de movimientos
			mensaje = "listar: se listaron los archivos de " + path 
			logMovimientos(mensaje)
		else:
			print("El path ingresado es incorrecto")

			# Se guarda en el log de errores
			mensaje2 = "listar: El path ingresado es incorrecto"
			logErrores(mensaje2)

#Fucnion para crear un directorio -> creardir [path]
def cmdCrearDir(cadena):
	cadena=cadena.split(sep=' ')
	for i in range(0, len(cadena)):
		try:
			# se crea el directorio
			os.mkdir(os.path.abspath(cadena[i])) 
			print("se creo el directorio correctamente")

			# Se guarda en el log de movimientos
			mensaje1 = "creardir: se creo un directorio en " + cadena[i] 
			logMovimientos(mensaje1)

		# no se puede crear porque ya existe una carpeta con el mismo nombre	
		except FileExistsError:
			print("La carpeta ya existe")

			# Se guarda en el log de errores
			mensaje2 = "creardir: La carpeta ya existe"
			logErrores(mensaje2)

#Funcion para ir a un directorio -> ir [path]
def cmdIr(path):
	# se verifica el path introducido
	if os.path.exists(path): 
		try:
			# se cambia de directorio al path solicitado
			path_n=os.getcwd()
			os.chdir(os.path.abspath(path))  
			#path_n = os.getcwd() # se obtiene la nueva ubicacion 
			#print("El path actual es: ", path_n)

			# Se guarda en el log de movimientos
			mensaje1 = "ir: el usuario se movio desde " + path_n + " a " + path
			logMovimientos(mensaje1)
		except Exception:
			print("Error al cambiar de directorio")

			# Se guarda en el log de errores
			mensaje2 = "ir: Error al cambiar de directorio"
			logErrores(mensaje2)

	else:
		print("El path introducido es incorrecto")

		# Se guarda en el log de errores
		mensaje2 = "ir: El path ingresado es incorrecto"
		logErrores(mensaje2)

#Funcion para obtener el path del directorio actual -> pwd
def cmdPwd():
	# se obtiene el path actual
	path = os.getcwd() 
	# se imprime
	print("El path actual es: ", path) 

	# Se guarda en el log de movimientos
	mensaje1 = "pwd: se mostro " + path 
	logMovimientos(mensaje1)

#Funcion para cambiar los permisos de un directorio -> permisos [permisos en Octal] [path]
def cmdPermisos(cadena):
	cadena = cadena.split(sep = ' ')
	permisos = int(cadena[0], base=8)
	path = cadena[1]
	path_r=os.path.abspath(path)
	# se verifica que el path existe
	if os.path.exists(path_r):
		try:
			# se cambian los permisos
			os.chmod(path_r, permisos)
			# se muestran los permisos actuales del archivo
			status=os.stat(path_r)
			print("Los permisos del archivo son (en octal): ", oct(status.st_mode))

			# Se guarda en el log de movimientos
			mensaje1 = "permisos: se cambiaron los permisos de " + str(path_r) 
			logMovimientos(mensaje1)
		except Exception:
			print("Error al cambiar los permisos")

			# Se guarda en el log de errores
			mensaje2 = "permisos: Error al cambiar los permisos"
			logErrores(mensaje2)
	else:
		print("El path introducido es incorrecto")

		# Se guarda en el log de errores
		mensaje2 = "permisos: El path ingresado es incorrecto"
		logErrores(mensaje2)

#Funcion que imprime el historial de comandos
def cmdHistory(comandos): 
	print("El historial de comandos es:")
	for i in range(0, len(comandos)):
		print(i+1, ": ", comandos[i])

	# Se guarda en el log de movimientos
	mensaje = "historial: se mostraron los comandos del historial " 
	logMovimientos(mensaje)

#Funcion para ejecutar otros comandos de linux
def cmdEjecutar(cadena):
	try:
		if cadena=="exit":
			control_horario(1) 
		subprocess.run(cadena.split())

		# Se guarda en el log de movimientos
		mensaje = "ejecutar: se ejecuto " + cadena 
		logMovimientos(mensaje)
	except Exception:
		print("Comando no encontrado")

		# Se guarda en el log de errores
		mensaje = "ejecutar: comando no encontrado" + cadena
		logErrores(mensaje)

#Funcion para buscar una cadena dentro de un archivo  -> buscar "cadena a buscar"
def cmdPropietario(cadena):  #Funcion para cambiar de propietarios  Formato USUARIO:GRUPO
	cadena = cadena.split(sep=' ') #se separa la cadena
	path = cadena[0]
	ids = cadena[1]
	ids = ids.split(sep=':')
	uid = ids[0]
	gid = ids[1]
	print(path)
	print(uid)
	print(gid)
	existeuid = validar_uid(uid)
	existegid = validar_gid(gid)
	
	try:
		if(existeuid ==1 and existegid ==1):	
			uid = int(uid)
			gid = int(gid)				
			os.chown(path, uid, gid)
			print("Se cambio de propietario exitosamente")
			mensaje = "propietario: se cambio de propietario " + path
			logMovimientos(mensaje)
								
		if existeuid != 1:
			mensaje = "propietario: no existe el uid " + uid
			print(mensaje)
			logErrores(mensaje)
		if existegid != 1:
			mensaje = "propietario: no existe el gid " + gid
			print(mensaje)
		
	except Exception:
		mensaje = "propietario: error al cambiar propietario"
		logErrores(mensaje)
		
#Funcion para buscar una cadena dentro de un archivo  -> buscar "cadena a buscar"
def cmdBuscar(cadena):
	cadena = cadena.split(sep=' ')
	path = cadena[len(cadena)-1]
	palabra = cadena[0]
	for i in range(1,len(cadena)-1):
		palabra = palabra + " " + cadena[i]

	print(palabra)

	if(os.path.isfile(path)):
		a = open(path,"r") # se abre el archivo
		texto = a.read()  # se guarda el contenido en texto
		contador = 0
		existe = 0
		with open(path) as file: #Se accede al archivo donde se encuentran los usuarios
			for line in file:
				contador = contador + 1
				if palabra in line:
					print("La cadena existe en el archivo: linea " + str(contador))
					# Se guarda en el log de movimientos
					mensaje = "buscar: se encontro la cadena en el archivo"
					existe =1  
					logMovimientos(mensaje)
	else:
		print("No existe el archivo.")
		# Se guarda en el log de errores
		mensaje = "buscar: No existe el archivo."
		logErrores(mensaje)			

	if existe == 0:
		print("La cadena no existe en el archivo.")
	# Se guarda en el log de errores
		mensaje = "buscar: La cadena no existe en el archivo."
		logErrores(mensaje)

			# Se guarda en el log de movimientos
		mensaje = "buscar: no se encontro la cadena en el archivo"  
		logMovimientos(mensaje)

#Funcion para transferir archivos via ftp
def cmdTransferencia():
	# se solicita la informacion necesaria 
	while True:
		opcion1=int(input("OPCIONES \n1)Ingresar informacion(hostname, nombr de usuario, contrasena) \n2)Usar infomacion de prueba (https://dlptest.com/ftp-test/) \nElija una opcion: "))
		if opcion1==1:
			hostname=input("Ingrese el host: ")
			username=input("Ingrese le nombre de usuario: ")
			password=input("Ingrese la contrasena: ")

	# La contrasena puede cambiar -- VISITAR https://dlptest.com/ftp-test/ PARA INFO DE PRUEBA
		elif opcion1==2:
			hostname='ftp.dlptest.com'
			username='dlpuser'
			password='rNrKYTX9g7z3RgJRmxWuGHbeu'
		else:
			print("Opcion fuera de rango")

		try:
			# nos conectamos a un servidor FTP
			ftp_server=ftplib.FTP(hostname, username, password)
			break
		except:
			print("Error al conectar, vuelva a intentar")

	# forzamos que la codificacion sea en el formato Unicode
	ftp_server.encoding="utf-8"
	
	try:
		while True:
			# se le pregunta al usuario que desea hacer con el archivo
			opcion=int(input("OPCIONES:\n 1)Subir archivo \n 2)Descargar archivo \n 3)Ver lista de archivos del servidor \n 4) Salir \n SELECCIONE UNA OPCION: "))
			
			if opcion==1: 
				# se solicita el nomnbre del archivo con su respectiva extension
				archivo=input("Ingrese el nombre del archivo: ")
				# se lee el archivo en binario
				fp=open(archivo, 'rb')
				# se sube el archivo
				ftp_server.storbinary('STOR %s' % os.path.basename(archivo), fp, 1024)
				# se cierra el archivo
				fp.close()

				print("Se subio el archivo exitosamente")

				# se listan los archivos del servidor
				print("LISTA DE ARCHIVOS DEL SERVIDOR: ")
				ftp_server.dir()

				# Se informa en el log
				mensaje = "FTP UPLOAD: " + archivo
				status = 1
				logTransferencias(status, mensaje)

				# Se guarda en el log de movimientos
				mensaje2 = "transferencia: se subio el archivo " + archivo
				logMovimientos(mensaje2)

				# se cierra la conexion
				ftp_server.quit()

			if opcion==2:
				# se pide el nombre del archivo
				archivo=input("Ingrese el nombre del archivo: ")
				while True:
					path=input("Ingresa el path donde se descargara el archivo: ")
					if os.path.exists(path):
						break
					else:
						print("El path ingresado no es valido, vuelva a ingresar")
				path_descarga=os.path.abspath(path+"/"+archivo)
				with open(archivo, "wb") as file: # el archivo se escribe en binario
					ftp_server.retrbinary(f"RETR {archivo}", open(path_descarga, 'wb').write) # se descarga el archivo
				print("Se descargo el archivo exitosamente")

				# Se informa en el log
				mensaje3 = "FTP DOWNLOAD: " + archivo
				status = 1
				logTransferencias(status, mensaje3)

				# se cierra la conexion
				ftp_server.quit()

				# Se guarda en el log de movimientos
				mensaje2 = "transferencia: se descargo el archivo " + archivo
				logMovimientos(mensaje2)

			elif opcion==3:
				# Se listan los archivos en el servidor
				print("LISTA DE ARCHIVOS DEL SERVIDOR: ")
				ftp_server.dir()

			elif opcion==4:
				break

			else:
				print("Opcion fuera de rango, vuelva a ingresar")
	except:
		print("Ocurrio un error")

		# Se informa en el log
		mensaje3 = "FTP ERROR: error al subir/descargar archivo"
		status = 0
		logTransferencias(status, mensaje3)

		# se cierra la conexion
		ftp_server.quit() # se cierra la conexion

		# Se guarda en el log de errores
		mensaje2 = "transferencia: error en la transferencia del archivo " 
		logErrores(mensaje2)
def cmdKill():
	# el usuario elije el pid del proceso que quiere terminar
	while True:
		opcion = int(input("OPCIONES: \n 1) Ver lista de procesos corriendo \n 2) Terminar un proceso \n 3) Salir \n Elije una opcion: "))
		# se muestran los procesos que estan corriendo
		if opcion == 1:
			for proc in psutil.process_iter():
				try:
					processName = proc.name()
					processID = proc.pid
					print('PROCESO: ', processName , ' :::  PID = ', processID)
				except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
					pass

		# se termina un proceso			
		elif opcion == 2:
			try:
			# se le pide al usuario el PID del proceso
				pid=int(input("Ingresa el pid del proceso: "))
				os.kill(pid, signal.SIGKILL)
				print("Se termino el proceso con PID ", pid)

			# Se guarda en el log de movimientos
				mensaje = "kill: se termino el proceso " + str(pid) 
				logMovimientos(mensaje)
			except Exception:
				print("error al terminar el proceso")

				mensaje2 = "kill: error al terminar el proceso " 
				logErrores(mensaje2)

		elif opcion == 3:
			break

		else:
			print("Opcion fuera de rango, vuelva a ingresar")
	

# Funcion para copiar archivo(s) y/o directorio(s) a un path especifico -> copiar [archivos/directorios] [path_destino]
def cmdCopiar(cadena):
    # Se separa el argumento por los espacios
	cadena = cadena.split(sep = ' ')
	# El path de destino es el ultimo objeto del argumento
	destino = cadena[len(cadena)-1]
	for i in range(0, len(cadena)-1):
		# Se verifica que el path de origen existe
		if os.path.exists(cadena[i]):
			origen = cadena[i]
			cadena[i] = cadena[i].split(sep = '/')
			# Si lo que se quiere copiar es un directorio
			try:
				shutil.copytree(origen, destino + "/" + cadena[i][len(cadena[i])-1])
				print("Se copio exitosamente el directorio ", origen)
                		# Se escribe el mensaje en el log
				msg="copiar: Se copio exitosamente el directorio" + str(cadena[i])
				logMovimientos(msg)
			# Si lo que se quiere copiar es un archivo
			except OSError as err:
				# Se crea la carpeta de destino si no existe
				if (os.path.exists(destino) == False):
					os.makedirs(destino)
				# Se copia el archivo
				if err.errno==errno.ENOTDIR:
					shutil.copy2(origen, destino + "/" )
					print("Se copio exitosamente el archivo ", origen)
                    			# Se escribe el mensaje en el log
					msg = "copiar: Se copio exitosamente el archivo" + str(cadena[i])
					logMovimientos(msg)
				else:
					print("Error: %s" %err)
                    			# Se escribe el mensaje en el log
					msg="copiar:  " + str(err)
					logErrores(msg)
		else:
			print("No existe el directorio o archivo")
			msg="copiar: No existe el directorio o archivo"
			logErrores(msg)

# Funcion para renombrar un archivo o directorio -> renombrar [archivo_original] [archivo_con_nombre_nuevo]
def cmdRenombrar(cadena): 
	# Se separan los paths en arrays
	cadena = cadena.split(sep = ' ')
	original = cadena[0]
	nuevo = cadena[1] 

	# se verifica que el archivo/directorio exista
	if os.path.exists(original):
		try :
			# se renombra el archivo/directorio
			os.rename(original,nuevo)
			print("Se renombro exitosamente") 

			# Se guarda en el log de movimientos
			mensaje = "renombrar: se renombro exitosamente" 
			logMovimientos(mensaje)

		except:
			print("Error al renombrar ")
			# Se guarda en el log de errores
			mensaje = "renombrar: Error al renombrar " 
			logErrores(mensaje)


	else:
		print("No existe el archivo o directorio.")
		# Se guarda en el log de errores
		mensaje = "renombrar: No existe el archivo o directorio."
		logErrores(mensaje)

# Funcion para mover archivo/s y/o directorio/s a un path especifico -> mover [archivos/directorios] [path_destino]
def cmdMover(cadena): 
	#se separan los paths en arrays
	cadena = cadena.split(sep=' ') 

	# el path de destino es el ultimo elemento del array
	destino=cadena[len(cadena)-1]

	for i in range(0, len(cadena)-1):
		if os.path.exists(cadena[i]):
			try :
				# Se mueve al path de destino
				shutil.move(cadena[i], destino) 
				print("Se movio exitosamente ", str(cadena[i]))

				# Se guarda en el log de movimientos
				mensaje = "mover: se movio exitosamente" + str(cadena[i])
				logMovimientos(mensaje)

			except:
				print("Error al mover.")
				# Se guarda en el log de errores
				mensaje = "mover: Error al mover " + str(cadena[i])
				logErrores(mensaje)


		else:
			print("No existe el archivo o directorio ")	
			# Se guarda en el log de errores
			mensaje = "mover: No existe el archivo o directorio " + str(cadena[i])
			logErrores(mensaje)

# Funcion para cambiar la contrasena de username
def change_passwd(username):
    datos=[]
	# se le pide al usuario que ingrese la contrasena nueva y la reconfirme
    new_passwd=getpass.getpass("Ingresa la nueva contrasena:  ")

    new_passwd_r=getpass.getpass("Reconfirma la contrasena: ")

	# se verifica que las contrasenas coincidan
    if new_passwd==new_passwd_r:
		# se encripta la contrasena
        cryptedpasswd=crypt.crypt(new_passwd, crypt.mksalt(crypt.METHOD_SHA512))

        # Abrimos el archivo /etc/shadow
        with open("/etc/shadow", "r+") as file:
            # Guardamos toda la info de /etc/shadow en datos
            for linea in file:
                datos.append(linea.strip().split(":"))

        # Nos ubicamos al principio del archivo
            file.seek(0)

        # Buscamos la linea donde esta la info del usuario del que queremos cambiar la contra
            for i in range(len(datos)):
                if username==datos[i][0]:
                    # Se cambia por la nueva contrasena
                    datos[i][1]=cryptedpasswd
				# se guardan los nuevos datos en /etc/shadow
                datos[i]=":".join(datos[i])
                file.write(datos[i]+ "\n")

        print("Nueva contrasena establecida")

        # Se guarda el mensaje en el log
        msj="passwd: se establecio la contrasena de " + username
        logMovimientos(msj)

        
    else:
        print("Las contrasenas no coinciden")
        # Se guarda el mensaje en el log
        msj="password: no se pudo establecer contrasena porque al reconfimar no coinciden"
        logErrores(msj)

# Funcion para verificar la contrasena del usuario
def login():
	# Se pide el usuario del que se quiere cambiar la contrasena
	username=input("Ingresa el nombre de usuario: ")
	try:
		# Se obtiene la contrasena del archivo /etc/shadow
		actual_passwd=spwd.getspnam(username)
		cryptedpasswd=actual_passwd.sp_pwdp
		if cryptedpasswd:
		# Se verifica la contrasena actual
			passwd=getpass.getpass("Ingresa la contrasena actual del usuario: ")
		# se compara la contrasena ingresada con la que esta en /etc/shadow
			if compare_hash(crypt.crypt(passwd, cryptedpasswd), cryptedpasswd):
				print("Contrasena correcta")
			# se cambia la contrasena
				change_passwd(username)
			else:
				print("Contrasena incorrecta")
            # Se guarda el mensaje en el log
				msj="password: contrasena incorrecta al verificar usuario"
				logErrores(msj)
		else:
			print("Error: usuario no existe")
        # Se guarda el mensaje en el log
			msj="password: no existe el usuario"
			logErrores(msj)
	except Exception:
		print("Error: no tienes permisos para cambiar contrasena del usuario")
    

#Funcion para cambiar de propietarios  Formato USUARIO:GRUPO
def cmdPropietario(cadena):  
	cadena = cadena.split(sep=' ') #se separa la cadena
	path = cadena[0]
	ids = cadena[1]
	ids = ids.split(sep=':')
	uid = ids[0]
	gid = ids[1]
	print(path)
	print(uid)
	print(gid)
	existeuid = validar_uid(uid)
	existegid = validar_gid(gid)
	
	try:
		if(existeuid ==1 and existegid ==1):	
			uid = int(uid)
			gid = int(gid)				
			os.chown(path, uid, gid)
			print("Se cambio de propietario exitosamente")
			mensaje = "propietario: se cambio de propietario " + path
			logMovimientos(mensaje)
								
		if existeuid != 1:
			mensaje = "propietario: no existe el uid " + uid
			print(mensaje)
			#logErrores(mensaje)
		if existegid != 1:
			mensaje = "propietario: no existe el gid " + gid
			print(mensaje)
		
	except:
		mensaje = "propietario: error al cambiar propietario"
		#logErrores(mensaje)
		
def getIp(print_ip): #Funcion para obtener la ip del usuario
## getting the hostname by socket.gethostname() method
	hostname = socket.gethostname()
## getting the IP address using socket.gethostbyname() method
	ip_address = socket.gethostbyname(hostname)
	if print_ip == 1 :
		print(ip_address)
	return ip_address 

def assignid():
	with open("/etc/passwd") as file: #Se accede al archivo donde se encuentran los usuarios
			for line in file:
				pass
			last_line = line #Se guarda la id del ultimo usuario

	idchar = split("\D+", last_line)
	id = int(idchar[1])
	flag=0
	file = open("/etc/passwd", "r")
	while flag == 0:
		id = id +1 #Se le suma 1 a la id del usuario anterior para obtener una nueva id unica
		id = str(id)
		if id in file:
			flag = 0
		else:
			flag=1
	file.close()
	return id

#Funcion para agregar usuario
def cmdAddUser():
	if is_root():
		usuario = input("Nombre de usuario: ")
		#contrasena = input("Ingrese la contrasena: ")
		while True:
			contrasena = getpass.getpass("contrasena: ")
			contrasena2 = getpass.getpass("vuelva a ingresar la contrasena: ")
			if contrasena == contrasena2:
				break
		
		ip = input("Ingrese su ip: ")
		print("Introduzca el nuevo valor, o presione INTRO para el predeterminado")
		nombre = input("Nombre completo :")
		nrotel= input("Numero de Telefono :")
		otro= input("Otro[] :")
		print("Ingrese su horario de trabajo : ")
		id = assignid()

		while True:
			horario_de_entrada = input("Ingrese horario entrada(formato 00:00): ")
			if validar_horario(horario_de_entrada):
				break
			else:
				print("respete el formato: 00:00")
		while True:
			horario_de_salida = input("Ingrese horario salida(formato 00:00): ")
			if validar_horario(horario_de_salida):
				break
			else:
				print("respete el formato: 00:00")
		mensaje = usuario + " " + ip + " " + horario_de_entrada + " " + horario_de_salida
		print(mensaje)
		info = input("confirme los datos agregados [Y/N]: ")
		if info == "Y" or info == "y":
			try:
				usuario_file = usuario + ":x:" + id + ":" + id + ":"  
				other =  nombre + "," + nrotel + "," + otro + ":" 
				home_bash = "/home/" + usuario + ":/bin/bash" + "\n"
				string = usuario_file + other + home_bash
				archivo = open("/etc/passwd", "a") 
				archivo.writelines(string) #Se agrega el nuevo usuario en la ruta /etc/passwd
				archivo.close()
				grupo = usuario +":x:" + id +":" + "\n"
				archivo2 = open("/etc/group", "a")
				archivo2.writelines(grupo) #Se le asigna un grupo al nuevo usuario en la ruta /etc/group
				archivo2.close()
				shutil.copytree("/etc/skel", "/home/" + usuario)
				usuario_file = usuario + ":" + crypt.crypt(contrasena2,crypt.mksalt(crypt.METHOD_SHA512)) + ":18944:0:99999:7:::\n"
				with open("/etc/shadow", "a") as file:
					file.write(usuario_file)
					file.close()
				mensaje = "adduser: se agrego el usuario " + usuario
				print(mensaje)
				logMovimientos(mensaje)
				msj=usuario + ' ' + ip + ' ' + horario_de_entrada + ' ' + horario_de_salida
				logRegistroUsuarios(msj)

			except:
				mensaje = "Error al agregar usuario"
				print(mensaje)
				logErrores(mensaje)
		else:
			mensaje = "adduser: se cancelo el registro de usuario"
			print(mensaje)
			logErrores(mensaje)
	else:
		mensaje = "adduser: solo root puede agregar usuarios"
		print(mensaje)
		#logErrores(mensaje)

	
def demonio(args):
    # Argument verifications
    args = args.split(sep = " ")
    if len(args) > 3:
        print("demonio: Too many arguments")
        ##sysError_logger.error("contrasenha: Too many arguments")
    elif len(args) < 2:
        print("demonio: Missing arguments")
        ##sysError_logger.error("demonio: Missing arguments")
    else:
        if(args[0]=='levantar'):
            try:
                subprocess.Popen("python3 "+args[1], shell=True)
                ##userCommands('demonio '+args[0]+' '+args[1])
            except Exception as e:
                print(e)
                #sysError_logger.error(e)
                print('Demonio: Non valid argument.')


def cmdAyuda():
	print("listar [path]: Se listan los archivos en path \nlistar: se listan los archivos en el path actual \nir [path_del_directorio]: nos movemos al directorio especificado")
	print("copiar [nombre de archivos/directorios] [path de destino]: se copian los archivos/directorios en el destino \nmover [nombre de los archivos/directorios] [path de destino]: Se mueven los archivos/directorios al destino")
	print("renombrar [nombre original] [nuevo nombre]: Se renombra el archivo o directorio \ncreardir [path del directorio]: Se crea un nuevo directorio \npwd: se imprime el path actual")
	print("kill: Comando para terminar un proceso \nadduser: comando para agregar un nuevo usuario \ntransfer: comando para subir/descargar un archivo de un servidor FTP \npassword: comando para cambiar la contrasena de un usuario")
	print("permisos [permisos en octal] [archivo]: se cambian los permisos del archivo \nhistorial: se muestra el historial de comandos \nbuscar [palabra] [archivo]: se busca la palabra dentro del archivo \ngetip: Se muestra la direccion IP del usuario actual")
	print("propietario [directorio] []: Se cambia el propietario del directorio \nlevantar: se levanta un demonio \nejecutar [otro_comando]: Se ejecuta el otro comando \n salir: se sale de la shell")



#Funcion main
def main():
	historial=[]
	tiempo = 0
	control_horario(tiempo)
	print("Bienvenido a BashCamiChris 1.0")
	while True:
		user=getpass.getuser()
		path=os.getcwd()
		hostname=socket.gethostname()
		comando = input("%s@%s:%s$ "%(user, hostname, path))

		if (comando[:6] == "listar"): 
			cmdListar(comando)
			historial.append("listar")

		elif (comando[:8] == "creardir"): 
			cmdCrearDir(comando[9:])
			historial.append("creardir")

		elif (comando == "pwd"): 
			cmdPwd()
			historial.append("pwd")
			
		elif (comando[:2] == "ir"): 
			cmdIr(comando[3:])
			historial.append("ir")
			
		elif (comando == "salir"):
			tiempo = 1
			control_horario(tiempo)
			break

		elif (comando[:8] == "permisos"):
			cmdPermisos(comando[9:])
			historial.append(comando)
			
		elif (comando[:9] == "historial"):
			cmdHistory(historial)
			historial.append(comando)
			
		elif (comando[:8] == "ejecutar"):
			cmdEjecutar(comando[8:])
			historial.append(comando)

		elif (comando[:6] == "copiar"):
			cmdCopiar(comando[7:])
			historial.append(comando)

		elif (comando[:9] == "renombrar"):
			cmdRenombrar(comando[10:])
			historial.append(comando)

		elif (comando[:5] == "mover"):
			cmdMover(comando[6:])
			historial.append(comando)

		elif (comando[:6] == "buscar"):
			cmdBuscar(comando[7:])
			historial.append(comando)

		elif (comando[:8]=="transfer"):
			cmdTransferencia()
			historial.append(comando)

		elif (comando[:4]=="kill") :
			cmdKill()
			historial.append(comando)
		
		elif (comando[:7] == "adduser"): #agregar usuario
			cmdAddUser()
			historial.append(comando)

		elif(comando == "hora"): #esta de prueba
			control_horario()

		elif (comando[:11] == "propietario"):
			cmdPropietario(comando[12:])
			historial.append(comando)
				
		elif(comando[:5] == "getip"):
			getIp(1)
		
		elif(comando[:8]=="password"):
			login()
			historial.append(comando)
		
		elif(comando[:8] == "levantar"):
			demonio(comando)
			historial.append(comando)

		elif(comando=="ayuda" ):
			cmdAyuda()
		else:
			print("Comando no reconocido, ejecuta 'ayuda' para ver la lista de comandos ")

if __name__ == "__main__":
    main()
