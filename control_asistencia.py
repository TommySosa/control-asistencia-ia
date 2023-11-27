from tkinter import *
import os
import cv2
from matplotlib import pyplot
from mtcnn.mtcnn import MTCNN
import numpy as np
import requests

#------------------------ funcion para registrar el usuario ---------------------

def registrar_usuario():
    usuario_info = usuario.get() #Obetnemos la informacion almcenada en usuario
    contra_info = contra.get() #Obtenemos la informacion almacenada en contra

    archivo = open(usuario_info, "w") #Abriremos la informacion en modo escritura
    archivo.write(usuario_info + "\n")   #escribimos la info
    archivo.write(contra_info)
    archivo.close()

    #Limpiaremos los text variable
    usuario_entrada.delete(0, END)
    contra_entrada.delete(0, END)

    Label(pantalla1, text = "Registro Convencional Exitoso", fg = "green", font = ("Calibri",11)).pack()
    
#--------------------------- Funcion para almacenar el registro facial --------------------------------------
    
def registro_facial():
    #Capturar del rostro
    cap = cv2.VideoCapture(0)               #Elegimos la camara con la que vamos a hacer la deteccion
    while(True):
        ret,frame = cap.read()              #Leemos el video
        cv2.imshow('Registro Facial',frame)         #Mostramos el video en pantalla
        if cv2.waitKey(1) == 27:            #Cuando oprimamos "Escape" saca la foto del video
            break
    usuario_img = usuario.get()
    cv2.imwrite(usuario_img+".jpg",frame)       #Guardamos la ultima captura del video como imagen y asignamos el dni del usuario
    cap.release()                               
    cv2.destroyAllWindows()

    usuario_entrada.delete(0, END) 
    contra_entrada.delete(0, END)
    Label(pantalla1, text = "Registro Facial Exitoso", fg = "green", font = ("Calibri",11)).pack()

    #----------------- Detectamos el rostro y exportamos los pixeles --------------------------
    
    def reg_rostro(img, lista_resultados):
        data = pyplot.imread(img)
        for i in range(len(lista_resultados)):
            x1,y1,ancho, alto = lista_resultados[i]['box']
            x2,y2 = x1 + ancho, y1 + alto
            pyplot.subplot(1, len(lista_resultados), i+1)
            pyplot.axis('off')
            cara_reg = data[y1:y2, x1:x2]
            cara_reg = cv2.resize(cara_reg,(150,200), interpolation = cv2.INTER_CUBIC) #Guardamos la imagen con un tamaño de 150x200
            cv2.imwrite(usuario_img+".jpg",cara_reg)
            pyplot.imshow(data[y1:y2, x1:x2])
        pyplot.show()

    img = usuario_img+".jpg"
    pixeles = pyplot.imread(img)
    detector = MTCNN()
    caras = detector.detect_faces(pixeles)
    reg_rostro(img, caras)   
    
#------------------------Crearemos una funcion para asignar al boton registro --------------------------------
def registro():
    global usuario
    global contra
    global usuario_entrada
    global contra_entrada
    global pantalla1

    pantalla1 = Toplevel(pantalla)
    pantalla1.title("Registro")
    ancho_pantalla = pantalla1.winfo_screenwidth()
    altura_pantalla = pantalla1.winfo_screenheight()

    x = (ancho_pantalla - 500) // 2 
    y = (altura_pantalla - 350) // 2 

    pantalla1.geometry(f"500x350+{x}+{y}")

    # Variables para almacenar la información
    usuario = StringVar()
    contra = StringVar()

    Label(pantalla1, text="Registro facial: debe asignar un usuario.", bg="darkcyan", width=60, height=1, font=("Verdana", 13), bd=5, relief="flat").pack()
    Label(pantalla1, text="Registro tradicional: debe asignar usuario y contraseña.", bg="darkcyan", width=60, height=1, font=("Verdana", 13), bd=5, relief="flat").pack()
    Label(pantalla1, text="").pack()

    # Entrada de dni
    Label(pantalla1, text="DNI * ").pack()
    usuario_entrada = Entry(pantalla1, textvariable=usuario)
    usuario_entrada.pack()
    Label(pantalla1, text="").pack()

    # Entrada de contraseña
    Label(pantalla1, text="Contraseña * ").pack()
    contra_entrada = Entry(pantalla1, textvariable=contra, show="*")
    contra_entrada.pack()
    Label(pantalla1, text="").pack()

    # Funcion para verificar y mostrar advertencia si el DNI está vacío
    def verificar_vacios():
        dni = usuario.get()
        contraseña = contra.get()
        if not dni or not contraseña:
            advertencia_label.config(text="No dejes campos vacios!", fg="red")
        else:
            advertencia_label.config(text="")
            registrar_usuario()  # Llama a la función de registro solo si el DNI no está vacío

    # Botón para registro tradicional
    Button(pantalla1, text="Registro Tradicional", width=15, height=1, command=verificar_vacios).pack()
    advertencia_label = Label(pantalla1, text="", fg="red", font=("Calibri", 11))
    advertencia_label.pack()

    # Espacio entre los botones
    Label(pantalla1, text="").pack()
    Label(pantalla1, text="").pack()

    # Botón para registro facial
    def verificar_dni():
        dni = usuario.get()
        if not dni:
            advertencia_label.config(text="Ingresa el dni!", fg="red")
        else:
            advertencia_label.config(text="")
            registro_facial()
    Button(pantalla1, text="Registro Facial", width=15, height=1, command=verificar_dni).pack()


#------------------------------------------- Funcion para verificar los datos ingresados al login ------------------------------------
    
def verificacion_login():
    log_usuario = verificacion_usuario.get()
    log_contra = verificacion_contra.get()

    usuario_entrada2.delete(0, END)
    contra_entrada2.delete(0, END)

    lista_archivos = os.listdir()   #Vamos a importar la lista de archivos con la libreria os
    if log_usuario in lista_archivos:   #Comparamos los archivos con el que nos interesa
        archivo2 = open(log_usuario, "r")  #Abrimos el archivo en modo lectura
        verificacion = archivo2.read().splitlines()  #leera las lineas dentro del archivo ignorando el resto
        if log_contra in verificacion:
            # enviar los datos a la API de express
            api_url = "http://localhost:4001/api/mark-attendance"
            payload = {"dni": log_usuario}

            try:
                response = requests.post(api_url, json=payload)
                data = response.json()
                name = data.get("name", "No se encontró el nombre")
                surname = data.get("surname", "No se encontró el apellido")

                if response.status_code == 200:
                    print("Solicitud a la API exitosa")      

                    label_bienvenida = Label(pantalla2, text = f"Bienvenido {name} {surname}!", fg = "green", font = ("Calibri",11))
                    label_bienvenida.pack()
                    pantalla2.after(5000, lambda: label_bienvenida.pack_forget())

                else:
                    print(f"Error en la solicitud a la API: {response.status_code}")

            except Exception as e:
                print(f"Error al realizar la solicitud: {e}")
                
            print("Acceso correcto, pero no hay registrado un usuario con ese DNI en el campus")
        else:
            print("Contraseña incorrecta, ingrese de nuevo")
            label_password = Label(pantalla2, text = "Contraseña Incorrecta", fg = "red", font = ("Calibri",11))
            label_password.pack()
            pantalla2.after(5000,lambda: label_password.pack_forget())
    else:
        print("Usuario no encontrado")
        label_usuario = Label(pantalla2, text = "Usuario no encontrado", fg = "red", font = ("Calibri",11))
        label_usuario.pack()
        pantalla2.after(5000,lambda: label_usuario.pack_forget())
    
#--------------------------Funcion para el Login Facial --------------------------------------------------------
def login_facial():
#------------------------------Vamos a capturar el rostro-----------------------------------------------------
    cap = cv2.VideoCapture(0)               #Elegimos la camara
    while(True):
        ret,frame = cap.read()              #Leemos el video
        cv2.imshow('Login Facial',frame)         #Mostramos el video en pantalla
        if cv2.waitKey(1) == 27:            #Cuando oprimamos "Escape" saca foto del video
            break
    usuario_login = verificacion_usuario.get()    #Con esta variable vamos a guardar la foto pero con otro nombre para no sobreescribir
    cv2.imwrite(usuario_login+"LOG.jpg",frame)       #Guardamos la ultima captura del video como imagen y asignamos el nombre del usuario
    cap.release()                               #Cerramos
    cv2.destroyAllWindows()

    usuario_entrada2.delete(0, END) 
    contra_entrada2.delete(0, END)

    #----------------- Funcion para guardar el rostro --------------------------
    
    def log_rostro(img, lista_resultados):
        data = pyplot.imread(img)
        for i in range(len(lista_resultados)):
            x1,y1,ancho, alto = lista_resultados[i]['box']
            x2,y2 = x1 + ancho, y1 + alto
            pyplot.subplot(1, len(lista_resultados), i+1)
            pyplot.axis('off')
            cara_reg = data[y1:y2, x1:x2]
            cara_reg = cv2.resize(cara_reg,(150,200), interpolation = cv2.INTER_CUBIC) #Guardamos la imagen 150x200
            cv2.imwrite(usuario_login+"LOG.jpg",cara_reg)
            return pyplot.imshow(data[y1:y2, x1:x2])
        pyplot.show()

    #-------------------------- Detectamos el rostro-------------------------------------------------------
    
    img = usuario_login+"LOG.jpg"
    pixeles = pyplot.imread(img)
    detector = MTCNN()
    caras = detector.detect_faces(pixeles)
    log_rostro(img, caras)

    #-------------------------- Funcion para comparar los rostros --------------------------------------------
    def orb_sim(img1,img2):
        orb = cv2.ORB_create()  #Creamos el objeto de comparacion
 
        kpa, descr_a = orb.detectAndCompute(img1, None)  #Creamos descriptor 1 y extraemos puntos claves
        kpb, descr_b = orb.detectAndCompute(img2, None)  #Creamos descriptor 2 y extraemos puntos claves

        comp = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck = True) #Creamos comparador de fuerza

        matches = comp.match(descr_a, descr_b)  #Aplicamos el comparador a los descriptores

        regiones_similares = [i for i in matches if i.distance < 70] #Extraemos las regiones similares en base a los puntos claves
        if len(matches) == 0:
            return 0
        return len(regiones_similares)/len(matches)  #Exportamos el porcentaje de similitud
        
    #---------------------------- Importamos las imagenes y llamamos la funcion de comparacion ---------------------------------
    
    im_archivos = os.listdir()   #Vamos a importar la lista de archivos con la libreria os
    if usuario_login+".jpg" in im_archivos:   #Comparamos los archivos con el que nos interesa

        rostro_reg = cv2.imread(usuario_login+".jpg",0)     #Importamos el rostro del registro
        rostro_log = cv2.imread(usuario_login+"LOG.jpg",0)  #Importamos el rostro del inicio de sesion
        similitud = orb_sim(rostro_reg, rostro_log)
        if similitud >= 0.95:
            label_exitoso = Label(pantalla2, text = "Verificacion de rostro exitoso", fg = "green", font = ("Calibri",11))
            label_exitoso.pack()
            pantalla2.after(5000, lambda: label_exitoso.pack_forget())
            
            api_url = "http://localhost:4001/api/mark-attendance"
            payload = {"dni": usuario_login}

            try:
                #Peticion post con los datos del usuario para marcar la asistencia
                response = requests.post(api_url, json=payload)
                data = response.json()
                name = data.get("name", "No se encontró el nombre")
                surname = data.get("surname", "No se encontró el apellido")

                if response.status_code == 200:
                    print("Solicitud a la API exitosa")
                    label_bienvenida = Label(pantalla2, text = f"Bienvenido {name} {surname}!", fg = "green", font = ("Calibri",11))
                    label_bienvenida.pack()
                    pantalla2.after(5000, lambda: label_bienvenida.pack_forget())
                else:
                    label_error = Label(pantalla2,text = "Error al marcar la asistencia, intenta nuevamente", fg = "green", font = ("Calibri",11))
                    label_error.pack()
                    pantalla2.after(5000, lambda: label_error.pack_forget())
                    print(f"Error en la solicitud a la API: {response.status_code}")
                    print(response.text) 

            except Exception as e:
                print(f"Error al realizar la solicitud: {e}")
                
            print("Bienvenido al sistema: ",usuario_login)
            print("Compatibilidad con la foto del registro: ",similitud)
        else:
            print("Rostro incorrecto, verifique su dni")
            print("Compatibilidad con la foto del registro: ",similitud)
            label_rostro = Label(pantalla2, text = "Incompatibilidad de rostros, intente nuevamente", fg = "red", font = ("Calibri",11))
            label_rostro.pack()
            pantalla2.after(5000, lambda: label_rostro.pack_forget())

    else:
        print("Usuario no encontrado")
        label_usuario = Label(pantalla2, text = "Usuario no encontrado", fg = "red", font = ("Calibri",11))
        label_usuario.pack()
        pantalla2.after(5000,lambda: label_usuario.pack_forget())
#------------------------Funcion que asignaremos al boton login -------------------------------------------------
        
def login():
    global pantalla2
    global verificacion_usuario
    global verificacion_contra
    global usuario_entrada2
    global contra_entrada2

    pantalla2 = Toplevel(pantalla)
    pantalla2.title("Login")

    ancho_pantalla = pantalla2.winfo_screenwidth()
    altura_pantalla = pantalla2.winfo_screenheight()

    x = (ancho_pantalla - 500) // 2 
    y = (altura_pantalla - 350) // 2

    pantalla2.geometry(f"500x350+{x}+{y}")

    Label(pantalla2, text="Login facial: debe asignar un usuario:", bg="darkcyan", width=60, height=1, font=("Verdana", 13), bd=5, relief="flat").pack()
    Label(pantalla2, text="Login tradicional: debe asignar usuario y contraseña:", bg="darkcyan", width=60, height=1, font=("Verdana", 13), bd=5, relief="flat").pack()
    Label(pantalla2, text="").pack()

    verificacion_usuario = StringVar()
    verificacion_contra = StringVar()

    Label(pantalla2, text="DNI * ").pack()
    usuario_entrada2 = Entry(pantalla2, textvariable=verificacion_usuario)
    usuario_entrada2.pack()

    Label(pantalla2, text="Contraseña * ").pack()
    contra_entrada2 = Entry(pantalla2, textvariable=verificacion_contra)
    contra_entrada2.pack()

    Label(pantalla2, text="").pack()
    Button(pantalla2, text="Con forma Tradicional", width=20, height=1, command=verificacion_login).pack()

    Label(pantalla2, text="").pack()
    Button(pantalla2, text="Con Reconocimiento Facial", width=20, height=1, command=login_facial).pack()
        
#------------------------- Funcion de nuestra pantalla principal ------------------------------------------------
    
def pantalla_principal():
    global pantalla
    pantalla = Tk()

    ancho_pantalla = pantalla.winfo_screenwidth()
    altura_pantalla = pantalla.winfo_screenheight()

    x = (ancho_pantalla - 500) // 2 
    y = (altura_pantalla - 350) // 2 

    pantalla.geometry(f"500x350+{x}+{y}")

    pantalla.title("Registro de Asistencia Campus")
    Label(text="Control de asistencia", bg="darkcyan", width=60, height=2, font=("Verdana", 13), bd=5, relief="flat").pack()
    Label(text="").pack()
    Label(text="").pack()

    Button(text="Marcar asistencia", height=2, width=30, command=login, bd=3, relief="raised").pack()
    Label(text="").pack()
    Label(text="").pack()

    Button(text="Registro", height=2, width=30, command=registro, bd=3, relief="raised").pack()

    pantalla.mainloop()

pantalla_principal()
