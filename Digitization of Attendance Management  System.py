
#*****************************************************LOGIN PAGE************************************************************************************************************************
from tkinter import *
from PIL import Image, ImageTk
from tkinter import ttk, messagebox
import pymysql, os
import credentials as cr

class SignUp:
    def __init__(self, root):
        self.window = root
        self.window.title("Sign Up")
        self.window.geometry("1280x800+0+0")
        self.window.config(bg = "white")

        self.bg_img = ImageTk.PhotoImage(file="C:\\Users\\User\\Pictures\\Saved Pictures\\forest.jpg")
        background = Label(self.window,image=self.bg_img).place(x=0,y=0,relwidth=1,relheight=1)


        frame = Frame(self.window, bg="white")
        frame.place(x=350,y=100,width=500,height=550)

        title1 = Label(frame, text="You can Sign in from here", font=("times new roman",25,"bold"),fg="Green",bg="White").place(x=20, y=10)
        title2 = Label(frame, text="Stay connected with us!", font=("times new roman",13),bg="white", fg="gray").place(x=20, y=50)

        f_name = Label(frame, text="First name", font=("helvetica",15,"bold"),bg="white",fg="Purple").place(x=20, y=100)
        l_name = Label(frame, text="Last name", font=("helvetica",15,"bold"),bg="white",fg="Purple").place(x=240, y=100)

        self.fname_txt = Entry(frame,font=("arial"))
        self.fname_txt.place(x=20, y=130, width=200)

        self.lname_txt = Entry(frame,font=("arial"))
        self.lname_txt.place(x=240, y=130, width=200)

        email = Label(frame, text="Enter your email id!", font=("helvetica",15,"bold"),bg="white",fg="Orange").place(x=20, y=180)

        self.email_txt = Entry(frame,font=("arial"))
        self.email_txt.place(x=26, y=210, width=420)

        a= Label(frame, text="Enter class grade", font=("helvetica",15,"bold"),bg="white",fg="Yellow").place(x=20, y=250)
        
        self.a = Entry(frame,font=("arial"))
        self.a.place(x=20, y=290, width=220)

        password =  Label(frame, text="New password", font=("helvetica",15,"bold"),bg="white").place(x=20, y=340)

        self.password_txt = Entry(frame,font=("arial"))
        self.password_txt.place(x=20, y=370, width=420)

        self.terms = IntVar()
        terms_and_con = Checkbutton(frame,text="I Agree The Terms & Conditions",variable=self.terms,onvalue=1,offvalue=0,bg="white",font=("times new roman",12)).place(x=20,y=420)
        self.signup = Button(frame,text="Sign Up",command=self.signup_func,font=("times new roman",18, "bold"),bd=0,cursor="hand2",bg="green2",fg="white").place(x=120,y=470,width=250)

    def signup_func(self):
        if self.fname_txt.get()=="" or self.lname_txt.get()=="" or self.email_txt.get()=="" or self.a.get()=="" or self.password_txt.get() == "":
            messagebox.showerror("Error!","Sorry!, All fields are required",parent=self.window)

        elif self.terms.get() == 0:
            messagebox.showerror("Error!","Please Agree with our Terms & Conditions",parent=self.window)

        else:
            try:
                connection = pymysql.connect(host=cr.host, user=cr.user, password=cr.password, database=cr.database)
                cur = connection.cursor()
                cur.execute("select * from student_register where email=%s",self.email_txt.get())
                row=cur.fetchone()

                # Check if th entered email id is already exists or not.
                if row!=None:
                    messagebox.showerror("Error!","The email id is already exists, please try again with another email id",parent=self.window)
                else:
                    cur.execute("insert into student_register (f_name,l_name,email,question,answer,password) values(%s,%s,%s,%s,%s,%s)",
                                    (
                                        self.fname_txt.get(),
                                        self.lname_txt.get(),
                                        self.email_txt.get(),
                                        self.questions.get(),
                                        self.answer_txt.get(),
                                        self.password_txt.get()
                                    ))
                    connection.commit()
                    connection.close()
                    messagebox.showinfo("Congratulations!","Register Successful",parent=self.window)
                    self.reset_fields()
            except Exception as e:
                messagebox.showerror("Error!",f"Error due to {str(e)}",parent=self.window)

    def reset_fields(self):
        self.fname_txt.delete(0, END)
        self.lname_txt.delete(0, END)
        self.email_txt.delete(0, END)
        self.questions.current(0)
        self.answer_txt.delete(0, END)
        self.password_txt.delete(0, END)

if __name__ == "__main__":
    root = Tk()
    obj = SignUp(root)
    root.mainloop()

#****************************************************************************Register page****************************************************
    from tkinter import *
from PIL import Image, ImageTk
from tkinter import ttk, messagebox
import pymysql, os
import credentials as cr
import mysql.connector

class SignUp:
    def __init__(self, root):
        self.window = root
        self.window.title("Sign Up")
        self.window.geometry("1280x800+0+0")
        self.window.config(bg = "white")

        self.bg_img = ImageTk.PhotoImage(file="C:\\Users\\User\\Pictures\\Saved Pictures\\forest.jpg")
        background = Label(self.window,image=self.bg_img).place(x=0,y=0,relwidth=1,relheight=1)


        frame = Frame(self.window, bg="white")
        frame.place(x=350,y=100,width=500,height=550)

        title1 = Label(frame, text="You can Sign in from here", font=("times new roman",25,"bold"),fg="Green",bg="White").place(x=20, y=10)
        title2 = Label(frame, text="Stay connected with us!", font=("times new roman",13),bg="white", fg="gray").place(x=20, y=50)

        f_name = Label(frame, text="First name", font=("helvetica",15,"bold"),bg="white",fg="Purple").place(x=20, y=100)
        l_name = Label(frame, text="Last name", font=("helvetica",15,"bold"),bg="white",fg="Purple").place(x=240, y=100)

        self.fname_txt = Entry(frame,font=("arial"))
        self.fname_txt.place(x=20, y=130, width=200)

        self.lname_txt = Entry(frame,font=("arial"))
        self.lname_txt.place(x=240, y=130, width=200)

        email = Label(frame, text="Enter your email id!", font=("helvetica",15,"bold"),bg="white",fg="Orange").place(x=20, y=180)

        self.email_txt = Entry(frame,font=("arial"))
        self.email_txt.place(x=26, y=210, width=420)

        a= Label(frame, text="Enter class grade", font=("helvetica",15,"bold"),bg="white",fg="Yellow").place(x=20, y=250)
        
        self.a = Entry(frame,font=("arial"))
        self.a.place(x=20, y=290, width=220)

        password =  Label(frame, text="New password", font=("helvetica",15,"bold"),bg="white").place(x=20, y=340)

        self.password_txt = Entry(frame,font=("arial"))
        self.password_txt.place(x=20, y=370, width=420)

        self.terms = IntVar()
        terms_and_con = Checkbutton(frame,text="I Agree The Terms & Conditions",variable=self.terms,onvalue=1,offvalue=0,bg="white",font=("times new roman",12)).place(x=20,y=420)
        self.signup = Button(frame,text="Sign Up",command=self.signup_func,font=("times new roman",18, "bold"),bd=0,cursor="hand2",bg="green2",fg="white").place(x=120,y=470,width=250)

    def signup_func(self):
        if self.fname_txt.get()=="" or self.lname_txt.get()=="" or self.email_txt.get()=="" or self.a.get()=="" or self.password_txt.get() == "":
            messagebox.showerror("Error!","Sorry!, All fields are required",parent=self.window)

        elif self.terms.get() == 0:
            messagebox.showerror("Error!","Please Agree with our Terms & Conditions",parent=self.window)

        else:
            try:
                fn = self.fname_txt.get()
                ln = self.lname_txt.get()
                em =  self.email_txt.get()
                a = self.a.get()
                p = self.password_txt.get()
                print(fn)
                print(ln)
                print(em)
                print(a)
                print(p)
                connection = mysql.connector.connect(user='root',password='password',port='3306',host='localhost',database='student_database')
                cur = connection.cursor()
                cur.execute("select * from student_register where email=%s",[em])
                row=cur.fetchone()

                # Check if th entered email id is already exists or not.
                if row!=None:
                    messagebox.showerror("Error!","The email id is already exists, please try again with another email id",parent=self.window)
                else:
                    cur.execute("insert into student_register (f_name,l_name,email,a,password) values(%s,%s,%s,%s,%s)",[fn,ln,em,a,p])
                    connection.commit()
                    connection.close()
                    messagebox.showinfo("Congratulations!","Register Successful",parent=self.window)
                    self.reset_fields()
            except Exception as e:
                messagebox.showerror("Error!",f"Error due to {str(e)}",parent=self.window)

    def reset_fields(self):
        self.fname_txt.delete(0, END)
        self.lname_txt.delete(0, END)
        self.email_txt.delete(0, END)
        self.a_txt.delete(0, END)
        self.password_txt.delete(0, END)

if __name__ == "__main__":
    root = Tk()
    obj = SignUp(root)
    root.mainloop()

###########################################################################Page for Marking Attendance####################################################
    from tkinter import Scale, Tk, Frame, Label, Button
from tkinter.ttk import Notebook,Entry

def getValue(value):
    print(value)

def getValue2(value):
    print(scale2.get())



window=Tk()
window.title("student details")
window.geometry("800x500")


frame2=Frame(window)
frame2.pack(fill="both")

tablayout=Notebook(frame2)

#tab1
#tab1=Frame(tablayout)
#tab1.pack(fill="both")



#tablayout.add(tab1,text="TAB 1")

#tab2
tab1=Frame(tablayout)
tab1.pack(fill="both")

#adding table into tab
def showData(btn):
    row=btn.grid_info()['row']
    column=btn.grid_info()['column']
    print("Column : "+str(column)+" Row : "+str(row))
    widget=tab1.grid_slaves(row=row,column=0)[0]
    widget2=tab1.grid_slaves(row=row,column=1)[0]
    widget3=tab1.grid_slaves(row=row,column=2)[0]
    widget4=tab1.grid_slaves(row=row,column=3)[0]
    print("Value at Column 1 : "+widget.cget("text") +" Column 2 : "+widget2.cget("text") + " Column 3 : "+widget3.cget("text")+" Column 4 : "+widget4.cget("text"))

    #updating value of label
    widget.config(text="New Data Click")


for row in range(5):
    for column in range(6):
        if row==0:
            if column==5:
                label = Label(tab1, text="Action", bg="white", fg="black", padx=3, pady=3)
                label.config(font=('Arial', 14))
                label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                tab1.grid_columnconfigure(column, weight=1)
            else:
                label = Label(tab1, text="Student : " + str(column), bg="white", fg="black", padx=3, pady=3)
                label.config(font=('Arial', 14))
                label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                tab1.grid_columnconfigure(column, weight=1)

        else:
            if column==5:
                button=Button(tab1,text="Edit",bg="blue",fg="white",padx=3,pady=3)
                button.grid(row=row,column=column,sticky="nsew",padx=1,pady=1)
                button['command']=lambda btn=button:showData(btn)
                tab1.grid_columnconfigure(column,weight=1)
            else:
                label=Label(tab1,text="Day "+str(row)+" "+str(row),bg="black",fg="white",padx=3,pady=3)
                label.grid(row=row,column=column,sticky="nsew",padx=1,pady=1)
                tab1.grid_columnconfigure(column,weight=1)





tablayout.add(tab1,text="TAB 1")

tablayout.pack(fill="both")

window.mainloop()

#####################################################################Entering Student Details###########################################################
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from tkinter import *

def GetValue(event):
    e1.delete(0, END)
    e2.delete(0, END)
    e3.delete(0, END)
    e4.delete(0, END)
    row_id = listBox.selection()[0]
    select = listBox.set(row_id)
    e1.insert(0,select['id'])
    e2.insert(0,select['empname'])
    e3.insert(0,select['mobile'])
    e4.insert(0,select['salary'])


def Add():
    studid = e1.get()
    studname = e2.get()
    coursename = e3.get()
    feee = e4.get()

    mysqldb=mysql.connector.connect(host="localhost",user="root",password="password",database="payroll")
    mycursor=mysqldb.cursor()

    try:
       sql = "INSERT INTO  registration (id,empname,mobile,salary) VALUES (%s, %s, %s, %s)"
       val = (studid,studname,coursename,feee)
       mycursor.execute(sql, val)
       mysqldb.commit()
       lastid = mycursor.lastrowid
       messagebox.showinfo("information", "Student details inserted successfully...")
       e1.delete(0, END)
       e2.delete(0, END)
       e3.delete(0, END)
       e4.delete(0, END)
       e1.focus_set()
    except Exception as e:
       print(e)
       mysqldb.rollback()
       mysqldb.close()


def update():
    studid = e1.get()
    studname = e2.get()
    coursename = e3.get()
    feee = e4.get()
    mysqldb=mysql.connector.connect(host="localhost",user="root",password="password",database="payroll")
    mycursor=mysqldb.cursor()

    try:
       sql = "Update  registation set empname= %s,mobile= %s,salary= %s where id= %s"
       val = (studname,coursename,feee,studid)
       mycursor.execute(sql, val)
       mysqldb.commit()
       lastid = mycursor.lastrowid
       messagebox.showinfo("information", "Record Updateddddd successfully...")

       e1.delete(0, END)
       e2.delete(0, END)
       e3.delete(0, END)
       e4.delete(0, END)
       e1.focus_set()

    except Exception as e:

       print(e)
       mysqldb.rollback()
       mysqldb.close()

def delete():
    studid = e1.get()

    mysqldb=mysql.connector.connect(host="localhost",user="root",password="password",database="payroll")
    mycursor=mysqldb.cursor()

    try:
       sql = "delete from registration where id = %s"
       val = (studid,)
       mycursor.execute(sql, val)
       mysqldb.commit()
       lastid = mycursor.lastrowid
       messagebox.showinfo("information", "Record Deleteeeee successfully...")

       e1.delete(0, END)
       e2.delete(0, END)
       e3.delete(0, END)
       e4.delete(0, END)
       e1.focus_set()

    except Exception as e:

       print(e)
       mysqldb.rollback()
       mysqldb.close()

def show():
        mysqldb = mysql.connector.connect(host="localhost", user="root", password="password", database="payroll")
        mycursor = mysqldb.cursor()
        mycursor.execute("SELECT id,empname,mobile,salary FROM registration")
        records = mycursor.fetchall()
        print(records)

        for i, (id,stname, course,fee) in enumerate(records, start=1):
            listBox.insert("", "end", values=(id, stname, course, fee))
            mysqldb.close()

root = Tk()
root.geometry("800x500")
global e1
global e2
global e3
global e4

tk.Label(root, text="Student Registration", fg="orange", font=(None, 30)).place(x=300, y=5)

tk.Label(root, text=" ID").place(x=10, y=10)
Label(root, text=" Name").place(x=10, y=40)
Label(root, text="Mobile").place(x=10, y=70)
Label(root, text="Class").place(x=10, y=100)

e1 = Entry(root)
e1.place(x=140, y=10)

e2 = Entry(root)
e2.place(x=140, y=40)

e3 = Entry(root)
e3.place(x=140, y=70)

e4 = Entry(root)
e4.place(x=140, y=100)

Button(root, text="Add",command = Add,height=3, width= 13).place(x=30, y=130)
Button(root, text="update",command = update,height=3, width= 13).place(x=140, y=130)
Button(root, text="Delete",command = delete,height=3, width= 13).place(x=250, y=130)

cols = ('ID', 'Name', 'Mobile','Class')
listBox = ttk.Treeview(root, columns=cols, show='headings' )

for col in cols:
    listBox.heading(col, text=col)
    listBox.grid(row=1, column=0, columnspan=2)
    listBox.place(x=10, y=200)

show()
listBox.bind('<Double-Button-1>',GetValue)

root.mainloop()

###################################################################################Signup page##########################################################
from tkinter import *
from tkinter import  messagebox

root=Tk()
root.title('Login')
root.geometry('925x500+300+200')
root.configure(bg="#fff")
root.resizable(False,False)

def signin():
    username=user.get()
    password=code.get()

    if username=='afshan' and password=='987':
        screen=Toplevel(root)
        screen.title("App")
        screen.geometry('925x500+300+200')
        screen.config(bg="white")

        Label(screen,text='Welcome!',bg='#fff',font=('Calibri(Body)',50,'bold')).pack(expand=True)

        screen.mainloop()

    elif username!='afshan' and password!='987':
        messagebox.showerror("Invalid","invalid username and password")

    elif password!="987":
        messagebox.showerror("Invalid","Invalid  password")

    elif username!='afshan':
        messagebox.showerror("Invalid","Invalid username")

#img=PhotoImage(file='C:\\Users\\User\\Pictures\\Saved Pictures\\wallpaper.jpg')
#Label(root,image=img,bg='white').place(x=50,y=50)

frame=Frame(root,width=350,height=350,bg="white")
frame.place(x=480,y=70)

heading=Label(frame,text='Sign in',fg='#57a1f8',bg='white',font=('Microsoft YaHei UI Light',23,'bold'))
heading.place(x=100,y=5)

def on_enter(e):
    user.delete(0,'end')

def on_leave(e):
    name=user.get()
    if name=='':
        user.insert(0,'username')

user=Entry(frame,width=25,fg='black',border=0,bg="white",font=('Microsoft YaHei UI Light',11))
user.place(x=30,y=80)
user.insert(0,'Username')
user.bind('<FocusIn>',on_enter)
user.bind('<FocusOut>',on_leave)

Frame(frame,width=295,height=2,bg='black').place(x=25,y=107)

def on_enter(e):
    code.delete(0,'end')

def on_leave(e):
    name=user.get()
    if name=='':
        code.insert(0,'password')


code=Entry(frame,width=25,fg='black',border=0,bg="white",font=('Microsoft YaHei UI Light',11))
code.place(x=30,y=150)
code.insert(0,'Password')
code.bind('<FocusIn>',on_enter)
code.bind('<FocusOut>',on_leave)

Frame(frame,width=295,height=2,bg='black').place(x=25,y=177)

Button(frame,width=39,pady=7,text='Sign in',bg='#57a1f8',fg='white',border=0,command=signin).place(x=35,y=204)
label=Label(frame,text="Don't have an account?",fg="black",bg="white",font=('Microsoft YaHei UI Light',9))
label.place(x=25,y=270)

sign_up=Button(frame,width=6,text='Sign up',border=0,bg='white',cursor='hand2',fg='#57a1f8')
sign_up.place(x=215,y=270)



root.mainloop()


 #############################################################################################################################################################################################
