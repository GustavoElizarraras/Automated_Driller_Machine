from tkinter import *
from PIL import Image
from PIL import ImageTk
import random
import time
from threading import Thread
raiz=Tk()
raiz.title("Barrenadora")
raiz.resizable(0,0)
raiz.geometry("1150x720")

imagen=PhotoImage(file="Circuito.png")
basura=PhotoImage(file="basura.png")
reciclar=PhotoImage(file="reciclar.png")
warning=PhotoImage(file="warning.png")

xcircuito=50
ycircuito=100

Agregarbarreno=(xcircuito+400-8,ycircuito+250-8)
BarrenosOrigenales=[(xcircuito+random.randint(0,800),ycircuito+random.randint(0,500)),(xcircuito+random.randint(0,800),ycircuito+random.randint(0,500)),(xcircuito+random.randint(0,800),ycircuito+random.randint(0,500))]
BarrenosAgregados=[]
BarrenosEliminados=[]
CuadradoPrincipales=[]
CuadradoAgregados=[]
CuadradosEliminados=[]
BarrenoNuevo=None
primer_triangulo = Image.open("triangulo.png")
trianguloDerecha=ImageTk.PhotoImage(primer_triangulo.rotate(90))
trianguloIzquierda=ImageTk.PhotoImage(primer_triangulo.rotate(270))
trianguloArriba=ImageTk.PhotoImage(primer_triangulo.rotate(180))
trianguloAbajo=ImageTk.PhotoImage(primer_triangulo)

def destruirBarreno(barreno):
    barreno[0].destroy()
    barreno[1].destroy()
    barreno[2].destroy()
    barreno[3].destroy()

def dibujarCuadrado(master,color,dupla):
    lineahorizontal=Image.new("RGB",(16,1))
    lineahorizontal = ImageTk.PhotoImage(lineahorizontal)
    lineavertical=Image.new("RGB",(1,16))
    lineavertical = ImageTk.PhotoImage(lineavertical)
    CuadradoArriba=Label(master, image=lineahorizontal,bg=color)
    CuadradoArriba.place(x=dupla[0],y=dupla[1])
    CuadradoAbajo=Label(master, image=lineavertical,bg=color)
    CuadradoAbajo.place(x=dupla[0],y=dupla[1])
    CuadradoIzquierda=Label(master, image=lineahorizontal,bg=color)
    CuadradoIzquierda.place(x=dupla[0],y=dupla[1]+lineahorizontal.width()-lineahorizontal.height())
    CuadradoDerecha=Label(master, image=lineavertical,bg=color)
    CuadradoDerecha.place(x=dupla[0]+lineahorizontal.width()-lineahorizontal.height(),y=dupla[1])
    return CuadradoArriba,CuadradoAbajo,CuadradoDerecha,CuadradoIzquierda

def presionAgregar():
    global Agregarbarreno,BarrenosAgregados,CuadradoAgregados,BarrenoNuevo
    BarrenosAgregados.append(Agregarbarreno)
    ListAgregar.insert(END,"BN"+str(ListAgregar.size()))
    CuadradoAgregados.append(dibujarCuadrado(Principal,"green",Agregarbarreno))
    Agregarbarreno=(xcircuito+400,ycircuito+250)
    destruirBarreno(BarrenoNuevo)
    BarrenoNuevo=dibujarCuadrado(Principal,"blue",Agregarbarreno)

def SeleccionarNuevo(event):
    global CuadradoAgregados
    BotTacheAgregar.place(x=1010,y=100)
    i=0
    for barreno in BarrenosAgregados:
        destruirBarreno(CuadradoAgregados[i])           
        CuadradoAgregados[i]=dibujarCuadrado(Principal,"green",barreno)
        i=i+1
    destruirBarreno(CuadradoAgregados[ListAgregar.curselection()[0]])   
    CuadradoAgregados[ListAgregar.curselection()[0]]=dibujarCuadrado(Principal,"yellow",BarrenosAgregados[ListAgregar.curselection()[0]])
def eliminar():
    global CuadradoAgregados,BarrenosAgregados
    destruirBarreno(CuadradoAgregados[ListAgregar.curselection()[0]])
    CuadradoAgregados.pop(ListAgregar.curselection()[0])
    BarrenosAgregados.pop(ListAgregar.curselection()[0])
    ListAgregar.delete(0,END)
    BotTacheAgregar.pack()
    BotTacheAgregar.pack_forget()
    i=0
    for barreno in CuadradoAgregados:
        ListAgregar.insert(END,"BN"+str(i))
        i=i+1

def salirAgregar():
    global BarrenosAgregados,BarrenosOrigenales,CuadradoAgregados
    BarrenosOrigenales.extend(BarrenosAgregados)          
    BarrenosAgregados=[]
    ListAgregar.delete(0,END)
    transicion(2,1)

def MoverArriba():
    global Agregarbarreno,BarrenoNuevo   
    if Agregarbarreno[1]-Eslaider.get()>=ycircuito:
        Agregarbarreno=(Agregarbarreno[0],Agregarbarreno[1]-Eslaider.get())
    else:
        Agregarbarreno=(Agregarbarreno[0],ycircuito)
    destruirBarreno(BarrenoNuevo)    
    BarrenoNuevo=dibujarCuadrado(Principal,"blue",Agregarbarreno)
    
def MoverAbajo():
    global Agregarbarreno,BarrenoNuevo 
    if Agregarbarreno[1]+Eslaider.get()<=(ycircuito+484):  
        Agregarbarreno=(Agregarbarreno[0],Agregarbarreno[1]+Eslaider.get())
    else:
        Agregarbarreno=(Agregarbarreno[0],ycircuito+484)
    destruirBarreno(BarrenoNuevo)
    BarrenoNuevo=dibujarCuadrado(Principal,"blue",Agregarbarreno)     
def MoverIzquierda():
    global Agregarbarreno,BarrenoNuevo 
    if Agregarbarreno[0]-Eslaider.get()>=(xcircuito):  
        Agregarbarreno=(Agregarbarreno[0]-Eslaider.get(),Agregarbarreno[1])
    else:
        Agregarbarreno=(xcircuito,Agregarbarreno[1])
    destruirBarreno(BarrenoNuevo)
    BarrenoNuevo=dibujarCuadrado(Principal,"blue",Agregarbarreno)  
def MoverDerecha():
    global Agregarbarreno,BarrenoNuevo   
    if Agregarbarreno[0]+Eslaider.get()<=(xcircuito+786):  
        Agregarbarreno=(Agregarbarreno[0]+Eslaider.get(),Agregarbarreno[1])
    else:
        Agregarbarreno=(xcircuito+786,Agregarbarreno[1])
    destruirBarreno(BarrenoNuevo)
    BarrenoNuevo=dibujarCuadrado(Principal,"blue",Agregarbarreno)    
        
def SeleccionarEliminar(event):
    global CuadradoPrincipales    
    i=0
    for barreno in BarrenosOrigenales:
        destruirBarreno(CuadradoPrincipales[i])           
        CuadradoPrincipales[i]=dibujarCuadrado(Principal,"red",barreno)
        i=i+1
    if not ListEliminar1.curselection()==():
        destruirBarreno(CuadradoPrincipales[ListEliminar1.curselection()[0]])   
        CuadradoPrincipales[ListEliminar1.curselection()[0]]=dibujarCuadrado(Principal,"yellow",BarrenosOrigenales[ListEliminar1.curselection()[0]])
        BotTacheEliminar.place(x=1010,y=150)

def eliminar1():
    global CuadradosEliminados,CuadradoPrincipales,BarrenosOrigenales,BarrenosEliminados
    destruirBarreno(CuadradoPrincipales[ListEliminar1.curselection()[0]])
    BarrenosEliminados.append(BarrenosOrigenales[ListEliminar1.curselection()[0]])
    CuadradoPrincipales.pop(ListEliminar1.curselection()[0])
    BarrenosOrigenales.pop(ListEliminar1.curselection()[0])
    BotTacheEliminar.pack()
    BotTacheEliminar.pack_forget()
    ListEliminar1.delete(0,END)
    CuadradosEliminados.append(dibujarCuadrado(Principal,"black",BarrenosEliminados[-1]))
    i=0
    for barreno in CuadradoPrincipales:
        ListEliminar1.insert(END,"BN"+str(i))
        i=i+1
    ListEliminar2.delete(0,END)
    i=0
    for barreno in BarrenosEliminados:
        ListEliminar2.insert(END,"BN"+str(i))
        i=i+1

def SeleccionarRehacer(event):
    global CuadradosEliminados,BarrenosEliminados
    i=0
    for barreno in BarrenosEliminados:
        destruirBarreno(CuadradosEliminados[i])           
        CuadradosEliminados[i]=dibujarCuadrado(Principal,"black",barreno)
        i=i+1
    if not ListEliminar2.curselection()==():
        BotTacheEliminar2.place(x=1010,y=350)
        destruirBarreno(CuadradosEliminados[ListEliminar2.curselection()[0]]) 
        CuadradosEliminados[ListEliminar2.curselection()[0]]=dibujarCuadrado(Principal,"cyan",BarrenosEliminados[ListEliminar2.curselection()[0]])

def eliminar2():
    global CuadradosEliminados,CuadradoPrincipales,BarrenosOrigenales,BarrenosEliminados
    destruirBarreno(CuadradosEliminados[ListEliminar2.curselection()[0]])
    BarrenosOrigenales.append(BarrenosEliminados[ListEliminar2.curselection()[0]])
    CuadradosEliminados.pop(ListEliminar2.curselection()[0])
    BarrenosEliminados.pop(ListEliminar2.curselection()[0])
    BotTacheEliminar2.pack()
    BotTacheEliminar2.pack_forget()
    ListEliminar1.delete(0,END)
    CuadradoPrincipales.append(dibujarCuadrado(Principal,"red",BarrenosOrigenales[-1]))
    i=0
    for barreno in CuadradoPrincipales:
        ListEliminar1.insert(END,"BN"+str(i))
        i=i+1
    ListEliminar2.delete(0,END)
    i=0
    for barreno in BarrenosEliminados:
        ListEliminar2.insert(END,"BN"+str(i))
        i=i+1

def salirEliminar():
    global BarrenosEliminados      
    ListEliminar1.delete(0,END)          
    BarrenosEliminados=[]
    ListEliminar2.delete(0,END)
    transicion(3,1)

def transicion(antiguo,nuevo):
    global CuadradoPrincipales,BarrenoNuevo,CuadradoAgregados,Agregarbarreno,BarrenosOrigenales,CuadradosEliminados
    if antiguo==0:
        BotEscanear.pack()
        BotEscanear.pack_forget()
        EtiCircuito.pack()
        EtiCircuito.pack_forget()
        ImaCircuito.pack()
        ImaCircuito.pack_forget()
        
    elif antiguo==1:
        EtiCircuito.pack()
        EtiCircuito.pack_forget()
        ImaCircuito.pack()
        ImaCircuito.pack_forget()
        BotMas.pack()
        BotVolver.pack()
        BotMenos.pack()
        BotPalomita.pack()
        BotMas.pack_forget()
        BotVolver.pack_forget()
        BotMenos.pack_forget()
        BotPalomita.pack_forget()
        for barreno in CuadradoPrincipales:
            destruirBarreno(barreno)           
        CuadradoPrincipales=[]
        for barreno in CuadradoAgregados:
            destruirBarreno(barreno)
        CuadradoAgregados=[]
    elif antiguo==2:
        EtiCircuito.pack()
        EtiCircuito.pack_forget()
        ImaCircuito.pack()
        ImaCircuito.pack_forget()
        BotSalir.pack()
        BotIzquierda.pack()
        BotDerecha.pack()
        BotArriba.pack()
        BotAbajo.pack()
        BotAgregar.pack()
        BotSalir.pack_forget()
        BotIzquierda.pack_forget()
        BotDerecha.pack_forget()
        BotArriba.pack_forget()
        BotAbajo.pack_forget()
        BotAgregar.pack_forget()
        destruirBarreno(BarrenoNuevo)
        Eslaider.pack()
        Eslaider.pack_forget()
        ListAgregar.pack()
        scrollbar.pack()
        ListAgregar.pack_forget()
        scrollbar.pack_forget()
        BotTacheAgregar.pack()
        BotTacheAgregar.pack_forget()
        for barreno in CuadradoPrincipales:
            destruirBarreno(barreno)
        CuadradoPrincipales=[]
        for barreno in CuadradoAgregados:
            destruirBarreno(barreno)
        CuadradoAgregados=[]
    elif antiguo==3:
        for barreno in CuadradoPrincipales:
            destruirBarreno(barreno)
        EtiCircuito.pack()
        EtiCircuito.pack_forget()
        ImaCircuito.pack()
        ImaCircuito.pack_forget()
        BotSalir1.pack()
        BotSalir1.pack_forget()
        ListEliminar1.pack()
        ListEliminar1.pack_forget()
        scrollbar2.pack()
        scrollbar2.pack_forget()
        BotTacheEliminar.pack()
        BotTacheEliminar.pack_forget()
        ListEliminar2.pack()
        ListEliminar2.pack_forget()
        scrollbar3.pack()
        scrollbar3.pack_forget()
        BotTacheEliminar2.pack()
        BotTacheEliminar2.pack_forget()
        for barreno in CuadradosEliminados:
            destruirBarreno(barreno)
        for barreno in CuadradoPrincipales:
            destruirBarreno(barreno)
        CuadradoPrincipales=[]
        CuadradosEliminados=[]
    elif antiguo==4:
        ImaCircuito.pack()
        EtiCircuito.pack()
        EtiTrabajando=Label(Principal,fg="green",bg="white",font=("Arial",15),text="Perforando "+str(len(BarrenosOrigenales))+" barrenos...")
        EtiTrabajando.pack()
        BotParo.pack()
        EtiTrabajando.pack_forget()
        BotParo.pack_forget()
        ImaCircuito.pack_forget()
        EtiCircuito.pack_forget()
        for barreno in CuadradoPrincipales:
            destruirBarreno(barreno)
        CuadradoPrincipales=[]
    elif antiguo==5:
        Etiwarning.pack()
        BotReanudar.pack()
        EtiTrabajando=Label(Principal,fg="green",bg="white",font=("Arial",15),text="Perforando "+str(len(BarrenosOrigenales))+" barrenos...")
        EtiTrabajando.pack()
        Etiwarning.pack_forget()
        BotReanudar.pack_forget()
        EtiTrabajando.pack_forget()


    if nuevo==0:
        BotEscanear.place(x=920,y=200)
        ImaCircuito.place(x=xcircuito,y=ycircuito)  
        EtiCircuito.place(x=400,y=50)
    elif nuevo==1:
        ImaCircuito.place(x=xcircuito,y=ycircuito)  
        EtiCircuito.place(x=400,y=50)
        BotMas.place(x=1020,y=300)
        BotVolver.place(x=920,y=200)
        BotMenos.place(x=950,y=300)
        BotPalomita.place(x=970,y=380)
        for barreno in BarrenosOrigenales:
            CuadradoPrincipales.append(dibujarCuadrado(Principal,"red",barreno))
    elif nuevo==2:
        ImaCircuito.place(x=xcircuito,y=ycircuito)  
        EtiCircuito.place(x=400,y=50)
        BotSalir.place(x=100,y=625)
        BotIzquierda.place(x=875,y=350)
        BotDerecha.place(x=1025,y=350)
        BotArriba.place(x=950,y=280)
        BotAbajo.place(x=950,y=420)
        BotAgregar.place(x=951,y=349)
        BarrenoNuevo=dibujarCuadrado(Principal,"blue",Agregarbarreno)
        Eslaider.place(x=875,y=550)
        ListAgregar.place(x=875,y=100)
        scrollbar.place(x=995,y=100)
        for barreno in BarrenosOrigenales:
            CuadradoPrincipales.append(dibujarCuadrado(Principal,"red",barreno))
        for barreno in BarrenosAgregados:
            CuadradoAgregados.append(dibujarCuadrado(Principal,"green",barreno))
    elif nuevo==3:
        ImaCircuito.place(x=xcircuito,y=ycircuito)  
        EtiCircuito.place(x=400,y=50)
        for barreno in BarrenosOrigenales:
            ListEliminar1.insert(END,"BN"+str(ListEliminar1.size()))
            CuadradoPrincipales.append(dibujarCuadrado(Principal,"red",barreno))
        ListEliminar1.place(x=875,y=150)
        scrollbar2.place(x=995,y=150)
        BotSalir1.place(x=100,y=625)
        ListEliminar2.place(x=875,y=350)
        scrollbar3.place(x=995,y=350)
    elif nuevo==4:
        ImaCircuito.place(x=xcircuito,y=ycircuito)  
        EtiCircuito.place(x=400,y=50)
        EtiTrabajando=Label(Principal,fg="green",bg="white",font=("Arial",15),text="Perforando "+str(len(BarrenosOrigenales))+" barrenos...")
        EtiTrabajando.place(x=875,y=150)
        BotParo.place(x=875,y=250)
        for barreno in BarrenosOrigenales:
            CuadradoPrincipales.append(dibujarCuadrado(Principal,"red",barreno))
    elif nuevo==5:
        Etiwarning.place(x=200,y=200)
        BotReanudar.place(x=400,y=625)

        
        
Principal=Frame(raiz,width=1150, height=720,bg="white")
Principal.pack()
EtiCircuito=Label(Principal,text="Circuito", fg="blue",bg="white",font=("Arial",30))
EtiCircuito.place(x=400,y=50)
ImaCircuito=Label(Principal, image=imagen,width=800, height=500)
ImaCircuito.place(x=xcircuito,y=ycircuito)
BotEscanear=Button(Principal,text="Escanear",bg="green",font=("Arial",25),command=lambda: transicion(0,1))
BotEscanear.place(x=920,y=200)

BotVolver=Button(Principal,text="Volver",bg="yellow",font=("Arial",25),command=lambda: transicion(1,0))
BotMas=Button(Principal,text="+",bg="cyan",font=("Arial",20),command=lambda: transicion(1,2))
BotMenos=Button(Principal,text="-",bg="cyan",font=("Arial",20),command=lambda: transicion(1,3))
BotPalomita=Button(Principal,text="✓",bg="red",font=("Arial",25),command=lambda: transicion(1,4))

BotSalir=Button(Principal,text="Salir y Confirmar",bg="yellow",font=("Arial",20),command=lambda: salirAgregar())
BotIzquierda=Button(Principal,image=trianguloIzquierda,command=lambda: MoverIzquierda())
BotDerecha=Button(Principal,image=trianguloDerecha,command=lambda: MoverDerecha())
BotArriba=Button(Principal,image=trianguloArriba,command=lambda: MoverArriba())
BotAbajo=Button(Principal,image=trianguloAbajo,command=lambda: MoverAbajo())
BotAgregar=Button(Principal,text="Agregar",bg="green",font=("Arial",12),height=3,command=lambda: presionAgregar())
Eslaider=Scale(Principal,label="Intensidad",orient=HORIZONTAL,from_=1,to=30,length=200)
ListAgregar=Listbox(Principal,height=8)
scrollbar = Scrollbar(Principal,orient='vertical',command=ListAgregar.yview)
ListAgregar['yscrollcommand'] = scrollbar.set
ListAgregar.bind('<<ListboxSelect>>', SeleccionarNuevo)
BotTacheAgregar=Button(Principal,image=basura,bg="white",command=lambda: eliminar())

ListEliminar1=Listbox(Principal,height=10)
scrollbar2 = Scrollbar(Principal,orient='vertical',command=ListEliminar1.yview)
ListEliminar1['yscrollcommand'] = scrollbar2.set
ListEliminar1.bind('<<ListboxSelect>>', SeleccionarEliminar)
BotTacheEliminar=Button(Principal,image=basura,bg="red",command=lambda: eliminar1())
BotSalir1=Button(Principal,text="Salir y Confirmar",font=("Arial",20),bg="yellow",command=lambda: salirEliminar())

ListEliminar2=Listbox(Principal,height=10)
scrollbar3 = Scrollbar(Principal,orient='vertical',command=ListEliminar2.yview)
ListEliminar2['yscrollcommand'] = scrollbar3.set
ListEliminar2.bind('<<ListboxSelect>>', SeleccionarRehacer)
BotTacheEliminar2=Button(Principal,image=reciclar,bg="white",command=lambda: eliminar2())

EtiTrabajando=Label(Principal,fg="green",bg="white",font=("Arial",15),text="Perforando "+str(len(BarrenosOrigenales))+" barrenos...")
BotParo=Button(Principal,text="Paro",bg="red",font=("Arial",40),command=lambda: transicion(4,5))

Etiwarning=Label(Principal,image=warning)
BotReanudar=Button(Principal,text="Reanudar",bg="green",font=("Arial",30),command=lambda: transicion(5,4))


raiz.mainloop()