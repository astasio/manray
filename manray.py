#!/usr/bin/env python
# -*- coding: utf-8 -*-
title='Manray'
version='versione: 02/03/2013'
author='autore: Antonio Stasio - astasio@gmail.com'

from gobject import timeout_add
import os
import gio
import atk
import gtk
import cairo
import pango
import pangocairo
import sqlite3
import time
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import *
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

ui=gtk.Builder()
ui.add_from_file("gui.ui")
win=ui.get_object("window1")
toolbar=ui.get_object("toolbar1")
gnew=ui.get_object("toolbutton1")
gcancel=ui.get_object("toolbutton2")
grefresh=ui.get_object("toolbutton3")
gclear=ui.get_object("toolbutton4")
gprint=ui.get_object("toolbutton5")
ginfo=ui.get_object("toolbutton6")
gquit=ui.get_object("toolbutton7")
gadd=ui.get_object("toolbutton8")
ghave=ui.get_object("toolbutton9")
glav=ui.get_object("toolbutton12")
gesc=ui.get_object("toolbutton13")
gbilancio=ui.get_object("toolbutton14")
scroll=ui.get_object("scrolledwindow1")
status=ui.get_object("statusbar1")
label1=ui.get_object("label1")
hbox1=ui.get_object("hbox1")
entry=ui.get_object("entry1")
query=ui.get_object("button1")
treeview=gtk.TreeView()

def warning(message):
  d=gtk.MessageDialog(None,0,gtk.MESSAGE_INFO,gtk.BUTTONS_OK,message)
  d.connect("response",lambda *w:d.destroy())
  d.run()
  
#----------------------------------------------------#      

def creazione_guidata():
  
  def insert():
    if entry.get_text()=="":
      warning("inserisci un nome!")
    else:
      mod.append([entry.get_text(),combo.get_active_text()])
      entry.set_text("")
      combo.set_active(0)
  
  def remove():
    model,iter=tree.get_selection().get_selected()
    if iter:
      if model.get_value(iter,0)=="Cliente" or model.get_value(iter,0)=="Prezzo Servizio":
	warning("Il campo non può essere eliminato!")
      else:
	model.remove(iter)
	warning("campo eliminato!")
  
  def su():
    model,iter=tree.get_selection().get_selected()
    if iter:
      row=model.get_path(iter)[0]
      if row > 0:
	campo=model[row][0]
	tipo=model[row][1]
	prev_campo=model[row-1][0]
	prev_tipo=model[row-1][1]
	model[row-1][0]=campo
	model[row-1][1]=tipo
	model[row][0]=prev_campo
	model[row][1]=prev_tipo
	tree.get_selection().select_path(row-1)
  
  def giu():
    model,iter=tree.get_selection().get_selected()
    if iter:
      model.move_after(iter,model.iter_next(iter))
  
  def applica():
    cols=[]
    iter=mod.get_iter_first()
    while iter:
      cols.append([mod.get_value(iter,0),mod.get_value(iter,1)])
      iter=mod.iter_next(iter)
    query="CREATE TABLE servizi(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"
    for i in range(len(cols)):
      query=query+cols[i][0].replace(" ","_")+" text,"
    query=query[:-1]
    query=query+")"
    sql=sqlite3
    db=sql.connect("manray.db")
    cur=sql.Cursor(db)
    cur.execute(query)
    db.commit()
    cur.execute("CREATE TABLE acconti(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,id_cliente INTEGER,cliente TEXT,data TEXT, acconto TEXT)")
    db.commit()
    query="CREATE TABLE impostazioni(tipo TEXT)"
    cur.execute(query)
    db.commit()
    cur.execute("INSERT INTO impostazioni values('TESTO')")
    db.commit()
    for i in range(len(cols)):
      query="INSERT INTO impostazioni values('"
      query=query+cols[i][1]+"')"
      cur.execute(query)
      db.commit()
    query="CREATE TABLE uscite(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,causale TEXT,data TEXT,valore TEXT)"
    cur.execute(query)
    db.commit()
    db.close()
    treeview.show()
    win.show_all()
    servizi()
    cg.hide()
  
  def annulla():
    esci()
  
  cg=gtk.Assistant()
  cg.set_size_request(640,480)
  cg.connect("apply",lambda *w:applica(),"apply")
  cg.connect("cancel",lambda *w:annulla(),"cancel")
  cg.set_title(title+" - "+version)
  
  intro=gtk.VBox()
  cg.append_page(intro)
  cg.set_page_title(intro,"Creazione guidata database")
  lbl1=gtk.Label("Questo processo ti guiderà\n nella creazione del tuo database personalizzato\n clicca avanti per continuare:")
  intro.add(lbl1)
  cg.set_page_type(intro,gtk.ASSISTANT_PAGE_INTRO)
  cg.set_page_complete(intro,True)
  
  content=gtk.HBox()
  scr=gtk.ScrolledWindow()
  content.add(scr)
  content.set_child_packing(scr,1,1,1,gtk.PACK_START)
  mod=gtk.ListStore(str,str)
  mod.append(["Cliente","TESTO"])
  mod.append(["Data Servizio","DATA"])
  mod.append(["Data Anteprima","DATA"])
  mod.append(["Tipologia Servizio","TESTO"])
  mod.append(["Album","TESTO"])
  mod.append(["Formato Fotografico","TESTO"])
  mod.append(["Film","TESTO"])
  mod.append(["Poster","TESTO"])
  mod.append(["Dimensioni Poster","TESTO"])
  mod.append(["Gadgets","TESTO"])
  mod.append(["Inviti","TESTO"])
  mod.append(["Fermaposto","TESTO"])
  mod.append(["Prezzo Servizio","EURO"])
  tree=gtk.TreeView(mod)
  scr.add(tree)
  cell1=gtk.CellRendererText()
  cell1.set_property('background','yellow')
  col1=gtk.TreeViewColumn("campi db",cell1,text=0)
  tree.append_column(col1)
  cell2=gtk.CellRendererText()
  cell2.set_property('background','light green')
  col2=gtk.TreeViewColumn("Tipo",cell2,text=1)
  tree.append_column(col2)
  vb0=gtk.VBox()
  content.add(vb0)
  up=gtk.Button(stock=gtk.STOCK_GO_UP)
  vb0.add(up)
  up.connect("clicked",lambda *w: su())
  dwn=gtk.Button(stock=gtk.STOCK_GO_DOWN)
  vb0.add(dwn)
  dwn.connect("clicked",lambda *w: giu())
  content.set_child_packing(vb0,0,0,0,gtk.PACK_START)
  vb=gtk.VBox()
  content.add(vb)
  content.set_child_packing(vb,0,0,0,gtk.PACK_END)
  lbl=gtk.Label("aggiungi campo database")
  vb.set_child_packing(lbl,0,0,0,gtk.PACK_START)
  vb.add(lbl)
  h=gtk.HBox()
  vb.add(h)
  entry=gtk.Entry()
  h.add(entry)
  vb.set_child_packing(h,0,0,0,gtk.PACK_START)
  cmod=gtk.ListStore(str)
  combo=gtk.ComboBox(cmod)
  cell=gtk.CellRendererText()
  combo.pack_start(cell, expand=True)
  combo.add_attribute(cell,'text',0)
  combo.append_text("TESTO")
  combo.append_text("DATA")
  combo.append_text("EURO")
  combo.set_active(0)
  h.add(combo)
  btn=gtk.Button(stock=gtk.STOCK_OK)
  vb.add(btn)
  vb.set_child_packing(btn,0,0,0,gtk.PACK_START)
  btn.connect("clicked",lambda *w: insert())
  btn2=gtk.Button(stock=gtk.STOCK_DELETE)
  vb.add(btn2)
  vb.set_child_packing(btn2,0,0,0,gtk.PACK_END)
  btn2.connect("clicked",lambda *w: remove())
  cg.append_page(content)
  cg.set_page_title(content,"personalizza i campi del database:")
  cg.set_page_type(content,gtk.ASSISTANT_PAGE_CONTENT)
  cg.set_page_complete(content,True)
  
  confirm=gtk.VBox()
  cg.append_page(confirm)
  cg.set_page_title(confirm,"salvare il nuovo database?")
  cg.set_page_type(confirm,gtk.ASSISTANT_PAGE_CONFIRM)
  cg.set_page_complete(confirm,True)
  cg.show_all() 

def esci():
    gtk.main_quit()

def new():
  sql=sqlite3
  db=sql.connect("manray.db")
  cur=sql.Cursor(db)
  if label1.get_text().split()[0]=="Acconti":
    cur.execute("SELECT Cliente FROM servizi")
    if not cur.fetchall(): 
      warning("Non ci sono clienti di cui registrare gli acconti!")
      return
    else:
      query="INSERT INTO acconti DEFAULT VALUES"
      cur.execute(query)
      db.commit()
    db.close()
  elif label1.get_text()=="Avere":
    pass
  elif label1.get_text()=="Servizi":
    query="INSERT INTO servizi DEFAULT VALUES"
    cur.execute(query)
    db.commit()
    db.close()
  elif label1.get_text()=="Uscite":
    query="INSERT INTO uscite DEFAULT VALUES"
    cur.execute(query)
    db.commit()
    db.close()
  popolate()

def delrow():
  sql=sqlite3
  db=sql.connect("manray.db")
  cur=sql.Cursor(db)
  model,iter=scroll.get_child().get_selection().get_selected()
  if iter:
    if label1.get_text().split()[0]=="Acconti":
      query="DELETE FROM acconti WHERE ID='"+model.get_value(iter,0)+"'"
      cur.execute(query)
      db.commit()
    elif label1.get_text()=="Avere":
      pass
    elif label1.get_text()=="Servizi":
      id_cliente=model.get_value(iter,0)
      query="DELETE FROM servizi WHERE ID='"+model.get_value(iter,0)+"'"
      cur.execute(query)
      db.commit()
      query="DELETE FROM acconti WHERE id_cliente='"+id_cliente+"'"
      cur.execute(query)
      db.commit()
    elif label1.get_text()=="Uscite":
      query="DELETE FROM uscite WHERE ID='"+model.get_value(iter,0)+"'"
      cur.execute(query)
      db.commit()
    db.close()
    model.remove(iter)
    warning("riga cancellata correttamente")

def popolate():
  sql=sqlite3
  db=sql.connect("manray.db")
  cur=sql.Cursor(db)
  model=scroll.get_child().get_model()
  if label1.get_text().split()[0]=="Acconti":
    cur.execute("select * from acconti")
  elif label1.get_text()=="Avere":
    return
  elif label1.get_text()=="Servizi":
    cur.execute("select * from servizi")
  elif label1.get_text()=="Uscite":
    cur.execute("select * from uscite")
  model.clear()
  for i in cur:
    model.append(i)   
  db.close()

def pulisci():
  if label1.get_text()=="Avere":
    pass
  else:  
    model=scroll.get_child().get_model()
    model.clear()

def edited_calendar(cell,path,text,num_column,column):  
    def ret_dat():
      sql=sqlite3
      db=sql.connect("manray.db")
      cur=sql.Cursor(db)
      data=cal.get_date()
      w.destroy()
      win.set_sensitive(True)
      data=str(data[2])+"/"+str(data[1]+1)+"/"+str(data[0])
      model,iter=scroll.get_child().get_selection().get_selected()
      if iter:
	model.set(iter,num_column,data)
      if label1.get_text().split()[0]=="Acconti":
	query="UPDATE acconti SET "+column.get_title()+"='"+data+"' WHERE ID='"+model.get_value(iter,0)+"'"
      elif label1.get_text()=="Servizi":
	query="UPDATE servizi SET "+column.get_title()+"='"+data+"' WHERE ID='"+model.get_value(iter,0)+"'"
      elif label1.get_text()=="Uscite":
	query="UPDATE uscite SET "+column.get_title()+"='"+data+"' WHERE ID='"+model.get_value(iter,0)+"'"
      cur.execute(query)
      db.commit()
      db.close()
    win.set_sensitive(False)  
    w=gtk.Window(gtk.WINDOW_POPUP)
    w.set_position(gtk.WIN_POS_CENTER)
    cal=gtk.Calendar()
    w.add(cal)
    cal.show()
    cal.connect("day-selected-double-click",lambda *w:ret_dat())
    w.show()
    
def edited_callback(cell,path,text,num_column,column):
  sql=sqlite3
  db=sql.connect("manray.db")
  cur=sql.Cursor(db)
  model,iter=scroll.get_child().get_selection().get_selected()
  if iter:
    model.set(iter,num_column,text)
  if label1.get_text().split()[0]=="Acconti":
    query="UPDATE acconti SET "+column.get_title()+"='"+text+"' WHERE ID='"+model.get_value(iter,0)+"'"
  elif label1.get_text()=="Servizi":
    query="UPDATE servizi SET "+column.get_title()+"='"+text+"' WHERE ID='"+model.get_value(iter,0)+"'"
  elif label1.get_text()=="Uscite":
    query="UPDATE uscite SET "+column.get_title()+"='"+text+"' WHERE ID='"+model.get_value(iter,0)+"'"
  cur.execute(query)
  db.commit()
  db.close()
      
def edited_cliente(cell,path,text,num_column,column):  
    def get_cliente():
      mod,iter=tree1.get_selection().get_selected()
      cliente=mod.get_value(iter,1)
      id_cliente=mod.get_value(iter,0)
      model,iter=scroll.get_child().get_selection().get_selected()
      if iter:
	model.set(iter,1,id_cliente)
	model.set(iter,num_column,cliente)
	query="UPDATE acconti SET id_cliente="+id_cliente+","+column.get_title()+"='"+cliente+"' WHERE ID='"+model.get_value(iter,0)+"'"
	sql=sqlite3
	db=sql.connect("manray.db")
	cur=sql.Cursor(db)
	cur.execute(query)
	db.commit()
	db.close()
	w.hide()
	win.set_sensitive(True)
    win.set_sensitive(False)  
    w=gtk.Window(gtk.WINDOW_POPUP)
    w.set_position(gtk.WIN_POS_CENTER)
    m=gtk.ListStore(str,str)
    sql=sqlite3
    db=sql.connect("manray.db")
    cur=sql.Cursor(db)
    cur.execute("SELECT id,cliente FROM servizi")
    for i in cur:
      m.append(i)
    db.close()
    tree1=gtk.TreeView(m)
    w.add(tree1)
    c=gtk.CellRendererText()
    c.set_property('editable',False)
    col=gtk.TreeViewColumn("id_cliente",c,text=0)
    tree1.append_column(col)
    c=gtk.CellRendererText()
    c.set_property('editable',True)
    col=gtk.TreeViewColumn("lista Clienti",c,text=1)
    tree1.append_column(col)
    c.connect("editing-started",lambda *w:get_cliente())
    tree1.show()
    w.show()
    
def edited_money(cell,path,text,num_column,column):  
    def annulla():
      w.hide()
      win.set_sensitive(True)
    def set_price():
      sql=sqlite3
      db=sql.connect("manray.db")
      cur=sql.Cursor(db)
      price=spin.get_text().replace(",",".")
      model,iter=scroll.get_child().get_selection().get_selected()
      if model.get_value(iter,3)=="totale:":
	pass
      else:
        if iter:
	  model.set(iter,num_column,price)
	  if label1.get_text().split()[0]=="Acconti":
	    query="UPDATE acconti SET "+column.get_title()+"='"+price+"' WHERE ID='"+model.get_value(iter,0)+"'"
	  elif label1.get_text()=="Servizi":
	    query="UPDATE servizi SET "+column.get_title()+"='"+price+"' WHERE ID='"+model.get_value(iter,0)+"'"
	  elif label1.get_text()=="Uscite":
	    query="UPDATE uscite SET "+column.get_title()+"='"+price+"' WHERE ID='"+model.get_value(iter,0)+"'"	 
	  cur.execute(query)
	  db.commit()
	db.close()
	w.hide()
	win.set_sensitive(True)
    win.set_sensitive(False)  
    w=gtk.Window()
    w.set_position(gtk.WIN_POS_CENTER)
    w.set_size_request(320,100)
    v=gtk.VBox()
    w.add(v)
    spin=gtk.SpinButton()
    spin.set_digits(2)
    spin.set_editable(True)
    adj=gtk.Adjustment(0.0, 0.0, 100000.0, 0.1, 10, 0)
    spin.set_adjustment(adj)
    v.add(spin)
    b=gtk.Button(stock=gtk.STOCK_OK)
    v.add(b)
    b.connect("clicked",lambda *w:set_price())
    w.connect("destroy",lambda *w: annulla())
    w.show_all()

#-----------------------------------------------------------------

def servizi():
  try:
    scroll.get_child().destroy()
  except:
    pass
  sql=sqlite3
  db=sql.connect("manray.db")
  cur=sql.Cursor(db)
  cur.execute("PRAGMA table_info(servizi)")
  cols_name=[]
  for i in cur:
    cols_name.append(i[1])
  treeview=gtk.TreeView()
  scroll.add(treeview)
  treeview.show()
  model=gtk.ListStore(*[str]*len(cols_name))
  treeview.set_model(model)
  treeview.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)
  imp=[]
  cur.execute("SELECT * FROM impostazioni")
  for i in cur:
    imp.append(i[0])
  db.close()
  for i in range(len(cols_name)):
    cell=gtk.CellRendererText()    
    if i==0:
      cell.set_property('editable',False)
      cell.set_property("cell-background","orange")
    else:
      cell.set_property('editable',True)
      cell.set_property("cell-background","yellow")      
    column=gtk.TreeViewColumn(cols_name[i],cell,text=i)
    treeview.append_column(column)
    if imp[i]=='DATA':
      cell.connect("editing-started",edited_calendar,i,column)
    elif imp[i]=='EURO':
      cell.connect("editing-started",edited_money,i,column)
    elif imp[i]=='TESTO':
      cell.connect("edited",edited_callback,i,column)
    else:
      pass
  label1.set_text("Servizi")    
  popolate()
  
def acconti():
  try:
    scroll.get_child().destroy()
  except:
    pass
  sql=sqlite3
  db=sql.connect("manray.db")
  cur=sql.Cursor(db)
  cur.execute("PRAGMA table_info(acconti)")
  cols_name=[]
  for i in cur:
    cols_name.append(i[1])
  treeview=gtk.TreeView()
  scroll.add(treeview)
  treeview.show()
  model=gtk.ListStore(*[str]*len(cols_name))  
  treeview.set_model(model)
  treeview.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)
  cell=gtk.CellRendererText()
  cell.set_property("cell-background","dark green")
  cell.set_property('editable',False)
  column=gtk.TreeViewColumn("id",cell, text=0)
  treeview.append_column(column)
  cell=gtk.CellRendererText()
  cell.set_property("cell-background","dark green")
  cell.set_property('editable',False)
  column=gtk.TreeViewColumn("id_cliente",cell, text=1)
  treeview.append_column(column)
  cell=gtk.CellRendererText()
  cell.set_property("cell-background","light green")
  cell.set_property('editable',True)
  column=gtk.TreeViewColumn("Cliente",cell, text=2)
  treeview.append_column(column)
  cell.connect("editing-started",edited_cliente,2,column)  
  cell=gtk.CellRendererText()
  cell.set_property("cell-background","light green")
  cell.set_property('editable',True)
  column=gtk.TreeViewColumn("Data",cell,text=3)
  treeview.append_column(column)
  cell.connect("editing-started",edited_calendar,3,column)
  cell=gtk.CellRendererText()
  cell.set_property("cell-background","light green")
  cell.set_property('editable',True)
  column=gtk.TreeViewColumn("Acconto",cell,text=4)
  treeview.append_column(column)
  cell.connect("editing-started",edited_money,4,column)  
  label1.set_text("Acconti") 
  db.close()
  popolate()
  a={}
  iter = model.get_iter_first()
  a["totale"]=0.00
  while iter:
    a["totale"]=a["totale"]+float(model.get_value(iter,4))
    iter=model.iter_next(iter)
  a["totale"]="%.2f" %a["totale"]
  label1.set_text("Acconti - totale acconti: "+a["totale"])

def avere():
  try:
    scroll.get_child().destroy()
  except:
    pass
  sql=sqlite3
  db=sql.connect("manray.db")
  cur=sql.Cursor(db)
  model=gtk.ListStore(str,str)
  treeview=gtk.TreeView()
  scroll.add(treeview)
  treeview.show()
  treeview.set_model(model)
  treeview.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)
  cell=gtk.CellRendererText()
  cell.set_property("cell-background","blue")
  cell.set_property('editable',False)
  column=gtk.TreeViewColumn("Cliente",cell,text=0)
  treeview.append_column(column)
  cell=gtk.CellRendererText()
  cell.set_property("cell-background","aquamarine")
  cell.set_property('editable',False)
  column=gtk.TreeViewColumn("Avere",cell, text=1)
  treeview.append_column(column)
  label1.set_text("Avere")
  a={}
  cur.execute("SELECT Cliente,Prezzo_servizio FROM servizi")
  if not cur.fetchall():
    return
  else:
    cur.execute("SELECT Cliente,Prezzo_servizio FROM servizi")
    for i in cur:
      if i[1]==None:
	a[i[0]]="0.00"
      else:
	a[i[0]]=i[1]
  cur.execute("SELECT Cliente,acconto FROM acconti")
  if not cur.fetchall():
    pass
  else:
    cur.execute("SELECT Cliente,acconto FROM acconti")
    for i in cur:
      if i[0]==None:
	pass
      else:
	a[i[0]]=float(a[i[0]])-float(i[1])
	a[i[0]]="%.2f"%float(a[i[0]])
  db.close()
  for i in a.keys():
    model.append([i,a[i]])
  iter = model.get_iter_first()
  a["totale"]=0.00
  while iter:
    a["totale"]=a["totale"]+float(model.get_value(iter,1))
    iter=model.iter_next(iter)
  a["totale"]="%.2f" %a["totale"]
  model.append(["totale:",a["totale"]])

def uscite():
  try:
    scroll.get_child().destroy()
  except:
    pass
  sql=sqlite3
  db=sql.connect("manray.db")
  cur=sql.Cursor(db)
  cur.execute("PRAGMA table_info(uscite)")
  cols_name=[]
  for i in cur:
    cols_name.append(i[1])
  treeview=gtk.TreeView()
  scroll.add(treeview)
  treeview.show()
  model=gtk.ListStore(*[str]*len(cols_name))
  treeview.set_model(model)
  treeview.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)
  for i in range(len(cols_name)):
    if i==0:
      cell=gtk.CellRendererText()
      cell.set_property('editable',False)
      cell.set_property("cell-background","brown")      
      column=gtk.TreeViewColumn(cols_name[i],cell,text=i)
      treeview.append_column(column)
    else:
      cell=gtk.CellRendererText()
      cell.set_property('editable',True)
      cell.set_property("cell-background","red")      
      column=gtk.TreeViewColumn(cols_name[i],cell,text=i)
      treeview.append_column(column)
    if i==2:
      cell.connect("editing-started",edited_calendar,i,column)
    elif i==3:
      cell.connect("editing-started",edited_money,i,column)
    elif i==1:
      cell.connect("edited",edited_callback,i,column)
    else:
      pass
  label1.set_text("Uscite")    
  popolate()
  db.close()

def bilancio():
  W=700
  H=240
  def indietro():
    win.set_sensitive(True)
    w.destroy()
    
  def expose(widget,event,acconti,uscite,picco): 
    cr=screen.window.cairo_create()
    cr.set_source_rgb(0.5,0.5,0.5)
    cr.set_line_width(0.4)
    cr.move_to(0,0)
    for i in range(24):
      cr.move_to(0,i*10)
      cr.line_to(600,i*10)
    cr.move_to(0,0)
    for i in range(60):
      cr.move_to(i*10,0)
      cr.line_to(i*10,240)
    cr.stroke()
    cr.move_to(2,205)
    cr.select_font_face("Serif",cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    cr.set_font_size(12.0)
    cr.show_text("0.0")
    cr.stroke()
    cr.set_line_width(2.0)
    
    cr.set_source_rgb(0,1,0)
    cr.rectangle(10,10,50,20)
    cr.fill()
    cr.move_to(70,20)
    cr.show_text("Entrate")
    
    cr.move_to(0,205)
    for i in acconti:
      cr.rel_line_to(600/acconti.__len__(),int(185*i/picco)-int(185*i/picco)*2)
    cr.move_to(0,205)
    cr.stroke()
    
    cr.set_source_rgb(1,0,0)
    cr.rectangle(10,40,50,20)
    cr.fill()
    cr.move_to(70,50)
    cr.show_text("Uscite")
    
    cr.move_to(0,205)
    for i in uscite:
      cr.rel_line_to(600/uscite.__len__(),int(185*i/picco)-int(185*i/picco)*2)
    cr.move_to(0,205)
    cr.stroke()
    
  sql=sqlite3
  db=sql.connect("manray.db")
  cur=sql.Cursor(db)  
  acconti=[]
  uscite=[]
  cur.execute("SELECT acconto FROM acconti")
  if not cur.fetchall():
    pass
  else:
    cur.execute("SELECT acconto FROM acconti")	  
    for i in cur:
      if i[0]!=None:
        acconti.append(float(i[0]))
  cur.execute("SELECT valore FROM uscite")
  if not cur.fetchall():
    pass
  else:
    cur.execute("SELECT valore FROM uscite")  
    for i in cur:
      if i[0]!=None:
        uscite.append(float(i[0]))
  a=[]
  cur.execute("SELECT Prezzo_servizio FROM servizi")
  if not cur.fetchall():
    pass
  else:
    cur.execute("SELECT Prezzo_servizio FROM servizi")
    for i in cur:
      if i[0]==None:
	a.append("0.00")
      else:
	a.append("%.2f"%float(i[0]))      
  db.close()
  picco=0.00
  for i in a:
    picco=picco+float(i)
  for i in uscite:
	  picco=picco+float(i)
  
  win.set_sensitive(False)
  w=gtk.Window()
  w.set_title("Bilancio")
  w.set_resizable(False)
  w.set_size_request(W,H)
  w.connect("destroy",lambda *w: indietro())
  w.set_position(gtk.WIN_POS_CENTER_ALWAYS)
  vb=gtk.VBox()
  w.add(vb)
  screen=gtk.DrawingArea()
  screen.set_size_request(600,151)
  vb.add(screen)	
  vb.set_child_packing(screen,expand=True,fill=True, padding=0,pack_type=gtk.PACK_START)
  screen.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse("#fff")) 
  screen.connect('expose_event',expose,acconti,uscite,picco)
  b=gtk.Button(stock=gtk.STOCK_OK)
  vb.add(b)
  vb.set_child_packing(b,expand=False,fill=False, padding=0,pack_type=gtk.PACK_END)
  b.connect("clicked",lambda *w: indietro() )
  w.show_all()
 
  
#-------------------------------------------------------------  
  
def reporting():
  a=time.localtime()
  data=str(a.tm_mday)+"/"+str(a.tm_mon)+"/"+str(a.tm_year)+" "+str(a.tm_hour)+":"+str(a.tm_min)	
  elements = []
  dati=[]
  styles = getSampleStyleSheet()
  doc = SimpleDocTemplate('report.pdf')
  l=doc.pagesize[0]
  r=doc.pagesize[1]
  doc.pagesize=[r,l]
  elements.append(Paragraph(title,styles['Title']))
  elements.append(Paragraph('<i>'+version+'</i>',styles['Normal']))
  #elements.append(Paragraph('<i>'+author+'</i>',styles['Normal']))
  elements.append(Paragraph("<b>Report eseguito in data: "+data+"</b>" ,styles['Normal']))
  model=scroll.get_child().get_model()
  sql=sqlite3
  db=sql.connect("manray.db")
  cur=sql.Cursor(db)
  intestazione=[]
  if label1.get_text().split()[0]=="Acconti":
    ts =[('ALIGN', (0,0), (-1,-1), 'LEFT'),
      ('BOX', (0,0), (-1, -1),1, colors.gray),
      ('INNERGRID', (0,0), (-1, -1),1, colors.gray),
      ('FONT', (-1,-1), (-1,-1), 'Times-Roman'),
      ('FONTSIZE', (0,0), (-1, -1), 14),
      ('PADDING',(0,0),(-1,-1),0)]
    elements.append(Paragraph('<b>'+label1.get_text().split()[0]+'<b>',styles['Normal']))  
    cur.execute("PRAGMA table_info(acconti)")
    for i in cur:
      intestazione.append(i[1])  
  elif label1.get_text()=="Avere":
    ts =[('ALIGN', (0,0), (-1,-1), 'LEFT'),
      ('BOX', (0,0), (-1, -1),1, colors.gray),
      ('INNERGRID', (0,0), (-1, -1),1, colors.gray),
      ('FONT', (-1,-1), (-1,-1), 'Times-Roman'),
      ('FONTSIZE', (0,0), (-1, -1), 14),
      ('PADDING',(0,0),(-1,-1),0)]
    elements.append(Paragraph('<b>'+label1.get_text()+'<b>',styles['Normal']))  
    intestazione=["Cliente","Avere"]
  elif label1.get_text()=="Servizi":
    ts =[('ALIGN', (0,0), (-1,-1), 'LEFT'),
      ('BOX', (0,0), (-1, -1),1, colors.gray),
      ('INNERGRID', (0,0), (-1, -1),1, colors.gray),
      ('FONT', (-1,-1), (-1,-1), 'Times-Roman'),
      ('FONTSIZE', (0,0), (-1, -1), 7),
      ('PADDING',(0,0),(-1,-1),0)]
    elements.append(Paragraph('<b>'+label1.get_text()+'<b>',styles['Normal'])) 
    cur.execute("PRAGMA table_info(servizi)")
    for i in cur:
      intestazione.append(i[1])
  elif label1.get_text()=="Uscite":
    ts =[('ALIGN', (0,0), (-1,-1), 'LEFT'),
      ('BOX', (0,0), (-1, -1),1, colors.gray),
      ('INNERGRID', (0,0), (-1, -1),1, colors.gray),
      ('FONT', (-1,-1), (-1,-1), 'Times-Roman'),
      ('FONTSIZE', (0,0), (-1, -1), 14),
      ('PADDING',(0,0),(-1,-1),0)]
    elements.append(Paragraph('<b>'+label1.get_text()+'<b>',styles['Normal'])) 
    cur.execute("PRAGMA table_info(uscite)")
    for i in cur:
      intestazione.append(i[1])
  db.close()
  dati.append(intestazione)
  iter = model.get_iter_first()
  while iter:
    rigo=[]
    for i in range(len(intestazione)):
      rigo.append(model.get_value(iter,i))
    dati.append(rigo)
    iter=model.iter_next(iter)
  t=Table(dati,style=ts)
  elements.append(t) 
  doc.build(elements)
  os.system('report.pdf')
#  os.system('okular report.pdf') 

def exec_query():
  sql=sqlite3
  db=sql.connect("manray.db")
  cur=sql.Cursor(db)
  query=entry.get_text()
  entry.set_text("")
  try:
    cur.execute(query)
    col=[]
    for i in cur:
      col.append(i)  
    model=gtk.ListStore(*[str]*len(col[0]))
    w=gtk.Window()
    w.set_title(query)
    w.set_size_request(640,480)
    scr=gtk.ScrolledWindow()
    w.add(scr)
    treeview=gtk.TreeView(model)
    scr.add(treeview)
    treeview.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)
    for i in range(len(col[0])):
      cell=gtk.CellRendererText()
      column=gtk.TreeViewColumn("",cell,text=i)
      treeview.append_column(column)
    model.clear()
    for i in col:
      model.append(i)
    w.show_all()
  except:
    warning("Query errata!")

def putdata():
  a=time.localtime()
  data=str(a.tm_mday)+"/"+str(a.tm_mon)+"/"+str(a.tm_year)+" "+str(a.tm_hour)+":"+str(a.tm_min) +":"+str(a.tm_sec) 
  status.push(1,data)
  timeout_add(1000,putdata)  

def credit():
  c=gtk.MessageDialog(None,0,gtk.MESSAGE_INFO,gtk.BUTTONS_OK,title+"\n"+version+"""\nCopyright (C) 2009 
Stasio Antonio - astasio@gmail.com
This program comes with ABSOLUTELY NO WARRANTY;
This is free software,
and you are welcome to redistribute it 
under certain conditions""")
  c.connect("response",lambda *w:c.destroy())
  image=gtk.Image()
  image.set_from_file("logo.png")
  c.set_image(image)
  image.show()
  c.run()
 
win.set_title(title+" - "+version)
win.set_size_request(780,560)
win.connect("destroy",lambda w: esci())
toolbar=gtk.Toolbar()
toolbar.set_style(gtk.TOOLBAR_BOTH)
toolbar.set_orientation(gtk.ORIENTATION_HORIZONTAL)
toolbar.set_icon_size(gtk.ICON_SIZE_LARGE_TOOLBAR)

gnew.connect("clicked",lambda *w: new())
gcancel.connect("clicked",lambda *w: delrow())
grefresh.connect("clicked",lambda *w: popolate())
gclear.connect("clicked",lambda *w: pulisci())
gprint.connect("clicked",lambda *w:reporting())
ginfo.connect("clicked",lambda *w: credit())
gquit.connect("clicked",lambda *w: esci())
glav.connect("clicked",lambda *w:servizi())
gadd.connect("clicked",lambda *w:acconti())
ghave.connect("clicked",lambda *w: avere())
gesc.connect("clicked",lambda *w: uscite())
query.connect("clicked",lambda *w: exec_query())
gbilancio.connect("clicked",lambda *w: bilancio())

try:
  f=open("manray.db","r")
  f.close()
  timeout_add(1000,putdata)
  win.show_all()
  servizi()
except:
  win.hide()
  creazione_guidata()

gtk.main()
