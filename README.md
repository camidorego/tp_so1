# Bash_CamiChris

Desarrollamos esta shell para nuestro sistema LFS 
La documentación del LFS se puede leer [aquí](https://drive.google.com/file/d/19v0TT7eucYRGho_KtLao71PmBHS32aAh/view?usp=sharing)
El pdf del manual de instrucciones se puede ver [aquí](https://drive.google.com/file/d/1-gOU7tg9mlGrJXEG5-KnSH_Ih2hLkoqb/view?usp=sharing)


##  Pre-requisitos
Antes de instalar la shell, se recomienda instalar la siguiente librería

    sudo apt install python3-pip
    pip install psutil

También se deben crear los logs donde se guardarán los movimientos del usuario

    mkdir /var/log/shell
    
    touch /var/log/shell/registro_diario.log
    touch /var/log/shell/registro_usuarios.log
    touch /var/log/shell/usuario_horarios.log
    touch /var/log/shell/registro_movimientos.log
    touch /var/log/shell/sistema_error.log
    touch /var/log/shell/shell_transferencias.log
Cambiamos los permisos del directorio para evitar cualquier error

    chmod -R 777 /var/log/shell

## Instalación

Primero creamos la ubicación de la shell

    mkdir /shell
Cambiamos los permisos del directorio

    chmod -R 777 /shell
Podemos clonar directamente el repositorio

    cd /shell
    git clone https://github.com/SO1Cami-Christian/tp-so1.git

Creamos el script de ejecución de la shell

    cd /
    
    vi shell.sh
    # !/bin/bash
    cd /shell/tp-so1
    python3 bash_CamiChris.py

Agregamos el archivo a /etc/profile

    echo “bash /shell.sh” >> /etc/profile

Y por último reiniciamos el sistema

    shutdown -r now




## Uso de la Shell

Para conocer los comandos se puede ejecutar

    ayuda

Listar los archivos y carpetas dentro de un directorio

    listar [path del directorio]
 Si no se especifica el path, se lista el contenido del directorio actual
 

    listar
   Copiar archivo(s) y/o directorio(s) 
   

    copiar [path del archivo/directorio][path de destino]
   Mover archivo(s) y/o directorio(s)
   

    mover [path del archivo/directorio][path de destino]
   Renombrar un archivo o directorio
   

    renombrar [nombre del archivo/directorio] [nuevo nombre del archivo/directorio]

 Crear un directorio: Crea uno o varios directorios.

    creardir [nombre del directorio]

 Cambiar de directorio: Permite moverse de un directorio a otro
    
    ir [path del directorio]
  
Cambiar los permisos de un archivo o directorio: Los permisos deben ir en su forma octual
    

    permisos [permisos en Octal] [nombre del archivo o directorio]

Cambiar los propietarios de un archivo o directorio: Se cambia el propietario del archivo o directorio
    

    propietario [path del archivo/directorio] [id del nuevo usuario] [id del grupo]

Cambiar contraseña: Se cambia la contraseña de un usuario específico (se debe ser usuario root)
    

    password

Agregar un usuario: Se agrega un usuario y se registran sus datos personales
    

    adduser


> Se piden los siguientes datos:
> - Nombre de usuario
> -   Contraseña
> -   Dirección IP
> -   Horario entrada (en formato HH:MM)
> -   Horario Salida (en formato HH:MM)

Imprimir el directorio actual: Se imprime el path del directorio actual
    

    pwd

Terminar un proceso: Se debe ingresar el PID del proceso a terminar
    

    kill

Buscar: se busca un string dentro del archivo solicitado
    

    buscar [string] [nombre del archivo]

Historial: Se imprime el historial de comandos que ejecutó el usuario
    

    historial

Levantar demonios: Se levantan y apagan demonios dentro del sistema
    

    levantar

Ejecutar otros comandos del sistema:
    

    ejecutar [comando]

Transferencia FTP: Se realiza la transferencia FTP de un archivo.
    

    transferencia

> Se deben especificar los siguiente datos:
> -   Hostname: dirección del servidor al cual se desea acceder
> -   User: nombre de usuario de la dirección del servidor
> -   Contraseña: contraseña del usuario
> Se realiza la conexión con el servidor y si esta es exitosa se le pide al usuario el nombre del archivo con su respectiva extensión


    

    

    





