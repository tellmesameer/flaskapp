import os
import random as rd
import smtplib as sp
import pyodbc
from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, session
import pandas as pd
from datetime import  date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
today = date.today().strftime('%m-%d-%Y')
# this is a dotenv commands.jgvhgc

load_dotenv()
ser = os.getenv('db_ser')
db_server = os.getenv('server')
db_user = os.getenv('username')
db_password = os.getenv('password')
datebase_name = os.getenv('database')
email_id = os.getenv('email_id')
email_id_password = os.getenv('email_id_password')

# flask app start from here
app = Flask(__name__)
app.secret_key = "super secret key"
app.config["DEBUG"] = True


# connection details for azure DB
try:
    mydb = pyodbc.connect(driver="ODBC Driver 18 for SQL Server",
                        host="erewardsportal001.database.windows.net", database="giftportal",
                        uid="dbadmin", pwd="Password@123")
except pyodbc.Error as drror:
        if drror.args[0] == "42000":
            print('Try again later because your internet is slow and the database is timed out.')
        else:
            print('Add Your Ip first .')

# Starting cursor to fetch all the details
mycursor = mydb.cursor()
mycursor.execute("SELECT * FROM [dbo].[User]")
mycursor.execute("SELECT [Email],[PhoneNumber] FROM [dbo].[Recipient]")
res_result = mycursor.fetchall()


# Upload folder
UPLOAD_FOLDER = 'static/files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    return render_template('newlogin.html')

# verification page for user

@app.route('/goe', methods=["post"])
def goe():
    try:
        mycursor.execute("SELECT * FROM [dbo].[User]")
        myresult = mycursor.fetchall()
    except pyodbc.Error as drror:
        if drror.args[0] == "08S01":
            flash('Try again later because your internet is slow and the database is timed out.')
            return render_template('newlogin.html')
    except:
        flash('Because of a database-related issue, try again later.')
        return render_template('newlogin.html')
               
    global mail
    global admin
    global auth
    global resi
    global phno
    global comp
    mail = request.form['email']
    try:
        for (uid, emails, usrpwd, giftcycleid, comp) in myresult:
            if (emails == mail):
                if (comp == 'I'):
                    otp = ''.join([str(rd.randint(0, 9)) for x in range(6)])
                    auth = otp
                    text = 'verification code is '+otp
                    print(text)
                    message = MIMEMultipart("alternatives")
                    message['Subject']='Verification-Code'
                    html="""
                    <html>
                    <head>
                    <meta charset="utf-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1">  
                    
                    </head>
                    <body style="background-color:White;">
                    
                    <h1>
                        eGiftPortal
                        </h1>
                        <p>Dear User,</p>
                        <b >
                        Enter the OTP for email validation : %s
                        </b>
                        <p> Do not share this OTP with anyone.</p>
                        <hr>
                    
                        <p style="text-align:center; margin-top:5px;">
                        If you have any questions,reply to this email or contact us at %s
                        </p>
                        </body>
                    </html>
                    """%(otp,email_id,)
                    htmlpart=MIMEText(html,'html')
                    message.attach(htmlpart)


                    server = sp.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(email_id, email_id_password)
                    server.sendmail(email_id, mail, message.as_string())
                    server.quit()
                    admin = uid
                    return render_template('newlogin.html', otps=otp, admin=0, otp=0, mail=mail, smt=1,otpw=otp)
                else:
                    auth = usrpwd
                    if (uid == 0):
                        admin = uid
                        return render_template('newlogin.html', otp=usrpwd, admin=1, otps=0, mail=mail)
                    else:
                        admin = uid
                        return render_template('newlogin.html', otp=usrpwd, admin=0, otps=0, mail=mail)
    except NameError:
        flash("Internal error occurred (NameError) .")
        return render_template('newlogin.html')
    flash(mail+' is not found')
    return render_template('newlogin.html')


@app.route('/rewards', methods=["post"])
def rewards():
    global resid
    global name_res
    # y yha s theeek krna h kabhi kabhi admin error deta h
    try:
        if session['loggedin'] == True:
            try:
                if (admin):
                    mycursor.execute(
                        '''SELECT  [RecipientId],[Name],[PhoneNumber],[RecipientGiftStatus] FROM [dbo].[Recipient] where [Email]='%s' ''' % (mail))
                    nameph = mycursor.fetchall()
                    for (reid, name_r, ph, cartsts) in nameph:
                        name_res = name_r
                        phno = ph
                        cartss = cartsts
                        resid = reid
                    mycursor.execute("SELECT * FROM [dbo].[GiftCycle]")
                    gift = mycursor.fetchall()
                    mycursor.execute(
                        '''Select [OrderId],[OrderNumber],[OrderDate],[RecipientId],[GiftCycleId],[ShippingAddress],[ShippingCity],[ShippingState],[ShippingZIP],[ShippingCountry],[DeliveryURL],[DockerNumber],[DockerDateUpdated],[ShippingDate],[CreateUserId],[UpdateUserId],[CreateDate],[UpdateDate] from [dbo].[Order] where [RecipientId]='%s' ''' % (resid))
                    orders = mycursor.fetchall()
                    mycursor.execute(
                    '''SELECT [reason] FROM [dbo].[OrderStatus] left join [dbo].[Order] on [dbo].[OrderStatus].OrderId=[dbo].[Order].OrderId where [dbo].[Order].RecipientId='%s' ''' % (resid,))
                    reason = mycursor.fetchall()  
                    for (GiftCycleId, GiftCycleDesc, GiftDesc, StartDate, EndDate) in gift:
                        return render_template('dashboard.html', mail=mail, naam=name_res, phno=phno, giftcycledecr=GiftCycleDesc, carts=cartss, orders=orders,reason=reason)

                else:
                    global counts
                    global bus
                    global totalorders
                    global count_query
                    global mys
                    temp_admin = 5
                    try:
                        mycursor.execute(
                            '''SELECT [RecipientId],[Name],[Email],[PhoneNumber],[RecipientGiftStatus] FROM [dbo].[Recipient] ''')
                        resi = mycursor.fetchall()
                        mycursor.execute(
                            '''SELECT  [id],[file_naam],[file_desc],[query_used] FROM [dbo].[csv_data] where [id] !=%d order by [id]''' % (6,))
                        bus = mycursor.fetchall()
                        mycursor.execute('''SELECT * FROM[dbo].[GiftCycle] ''')
                        gfcycle = mycursor.fetchall()
                        mycursor.execute(
                            ''' select [OrderNumber],[Name],[Email],[DeliveryURL],[ShippingDate] from [dbo].[Order] LEFT JOIN [dbo].[Recipient] ON [dbo].[Order].RecipientId = [dbo].[Recipient].RecipientId where OrderNumber is not null ''')
                        totalorders = mycursor.fetchall()
                        counts = []
                        mycursor.execute(
                            '''SELECT [query_used_count] FROM [dbo].[csv_data] where [id] !=%d  order by [id]''' % (6,))
                        count_query = mycursor.fetchall()

                        mycursor.execute('''  select [dbo].[Recipient].[RecipientId], [Name]  ,[Email] ,[PhoneNumber] ,[RecipientGiftStatus],[OrderNumber] from [dbo].[Recipient]  left join [dbo].[Order] on [dbo].[Recipient].RecipientId=[dbo].[Order].[RecipientId] where [RecipientGiftStatus]!='N' and [RecipientGiftStatus]!='C' and [RecipientGiftStatus]!='A'  ''')
                        ordered=mycursor.fetchall()
                    except:
                        session['_flashes'].clear()
                        session.pop('loggedin', None)
                        
                        session.pop('mail', None)
                        session.clear()
                        flash('Unexpected error occurred in databse ')
                        return render_template('newlogin.html')
                    for (x,) in count_query:
                        y = str(x)
                        if (y != 'None'):
                            mycursor.execute(y)
                            count = mycursor.fetchall()
                            for (c,) in count:
                                counts.append(c)
                        else:
                            counts.append(1)
                    x = 'select [OrderNumber],[Name],[Email],[DeliveryURL],[ShippingDate] from [dbo].[Order] LEFT JOIN [dbo].[Recipient]ON [dbo].[Order].RecipientId = [dbo].[Recipient].RecipientId where OrderNumber is not null'
                    filename = 'static/files/total_orders.csv'
                    realname = 'total_orders.csv'
                    sql_query = pd.read_sql_query(x, mydb)
                    df = pd.DataFrame(sql_query)
                    df.to_csv(filename, index=False)
                    mycursor.execute(
                        '''SELECT [file_desc] FROM [dbo].[csv_data] where [id] !=%d order by [id]''' % (6,))
                    mys = mycursor.fetchall()
                    try:
                        return render_template('admin.html', mail=mail, resi=resi, gcycle=gfcycle, thambu=bus, temp=temp_admin, toos=totalorders, counts=counts, mys=mys, fn=realname,ordered=ordered)
                    except:
                        flash('A update was made in the backend, so you signed out. ')
                        return render_template('newlogin.html')
                        
            except:
                flash('Session has been terminated. So login again ')
                return render_template('newlogin.html')
        else:
                flash(' u logged out')
                return render_template('newlogin.html')
    except:
        flash(' You logged out')
        return render_template('newlogin.html',mrd=1)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('mail', None)
    session.clear()
    flash('You are successfully logged out')
    return render_template('newlogin.html',mrd=1)


@app.route('/dashboardbutton/<int:id_data>', methods=['GET'])
def dashboardbutton(id_data):
    global realname
    temp_admin = 5
    mycursor.execute(
        '''SELECT [RecipientId],[Name],[Email],[PhoneNumber],[RecipientGiftStatus] FROM [dbo].[Recipient] ''')
    resi = mycursor.fetchall()
    mycursor.execute(
        '''SELECT  [id],[file_naam],[file_desc],[query_used] FROM [dbo].[csv_data] where [id] !=%d order by [id]''' % (6,))
    bus = mycursor.fetchall()
    mycursor.execute('''SELECT * FROM[dbo].[GiftCycle] ''')
    gfcycle = mycursor.fetchall()

    mycursor.execute(
        '''SELECT [file_naam], [query_used] FROM [dbo].[csv_data] where [id] =%d order by [id]''' % (id_data,))
    lhs = mycursor.fetchall()
    mycursor.execute('''select [dbo].[Recipient].[RecipientId], [Name]  ,[Email] ,[PhoneNumber] ,[RecipientGiftStatus],[OrderNumber] from [dbo].[Recipient]  left join [dbo].[Order] on [dbo].[Recipient].RecipientId=[dbo].[Order].[RecipientId] where [RecipientGiftStatus]!='N' and [RecipientGiftStatus]!='C' and [RecipientGiftStatus]!='A' ''')
    ordered=mycursor.fetchall()

    for (a, x,) in lhs:
        y = str(x)
        z = str(a)
        if (y != 'None'):
            mycursor.execute(x)
            totalorders = mycursor.fetchall()
            filename = 'static/files/'+z
            realname = z
            sql_query = pd.read_sql_query(x, mydb)
            df = pd.DataFrame(sql_query)
            df.to_csv(filename, index=False)

    counts = []
    if (id_data != 1):
        mycursor.execute(
            '''SELECT [query_used_count] FROM [dbo].[csv_data] where  [id] =%d or [id] =%d order by [id]''' % (1, int(id_data),))
        count_query = mycursor.fetchall()
    else:
        mycursor.execute(
            '''SELECT [query_used_count] FROM [dbo].[csv_data] where [id] !=%d  order by [id]''' % (6,))
        count_query = mycursor.fetchall()
    for (x,) in count_query:
        y = str(x)
        if (y != 'None'):
            mycursor.execute(y)
            count = mycursor.fetchall()
            for (c,) in count:
                counts.append(c)
        else:
            counts.append(0)
            
    if (id_data == 1):
        mycursor.execute(
            '''SELECT [file_desc] FROM [dbo].[csv_data] where [id] !=%d order by [id]''' % (6,))
    else:
        mycursor.execute(
            '''SELECT [file_desc] FROM [dbo].[csv_data] where [id] =%d or [id] =%d  order by [id]''' % (1, int(id_data),))
    mys = mycursor.fetchall()

    return render_template('admin.html', mail=mail, resi=resi, gcycle=gfcycle, thambu=bus, temp=temp_admin, toos=totalorders, counts=counts, mys=mys, fn=realname,ide=id_data,ordered=ordered)


@app.route('/confirm', methods=["post"])
def confirm():
    name = request.form['name']
    mob = request.form['phno']
    address = request.form['address']
    country = request.form['country']
    state = request.form['state']
    city = request.form['city']
    pincode = request.form['pincode']
    mycursor.execute(''' insert into [dbo].[order] ([RecipientId],[GiftCycleId], [ShippingAddress]  ,[ShippingCity]  ,[ShippingState],[ShippingZIP]  ,[ShippingCountry]) values('%s',1,'%s','%s','%s','%s','%s') ''' % (
        resid, address, city, state, pincode, country,))
    try:
        mycursor.execute(
            '''Update [dbo].[Recipient] set [RecipientGiftStatus]='A' where [RecipientId]='%s' ''' % (resid,))
        mydb.commit()
    except:
        try:
            mycursor.execute(
            '''SELECT [Name],[PhoneNumber],[RecipientGiftStatus] FROM [dbo].[Recipient] where [Email]='%s' ''' % (mail))
            nameph = mycursor.fetchall()
            for (name_r, ph, cartsts) in nameph:
                name_res = name_r
                phno = ph
                cartss = cartsts
            mycursor.execute("SELECT * FROM [dbo].[GiftCycle]")
            gift = mycursor.fetchall()
            mycursor.execute(
                '''Select [OrderId],[OrderNumber],[OrderDate],[RecipientId],[GiftCycleId],[ShippingAddress],[ShippingCity],[ShippingState],[ShippingZIP],[ShippingCountry],[DeliveryURL],[DockerNumber],[DockerDateUpdated],[ShippingDate],[CreateUserId],[UpdateUserId],[CreateDate],[UpdateDate] from [dbo].[Order] where [RecipientId]='%s' ''' % (resid))
            orders = mycursor.fetchall()
            mycursor.execute(
                '''SELECT [reason] FROM [dbo].[OrderStatus] left join [dbo].[Order] on [dbo].[OrderStatus].OrderId=[dbo].[Order].OrderId where [dbo].[Order].RecipientId='%s' ''' % (resid,))
            reason = mycursor.fetchall()
            flash('Currrently not handle this request please try again later')
            for (GiftCycleId, GiftCycleDesc, GiftDesc, StartDate, EndDate) in gift:
                return render_template('dashboard.html', mail=mail, naam=name_res, phno=phno, giftcycledecr=GiftCycleDesc, carts=cartss, orders=orders, reason=reason)
        except:
            session['_flashes'].clear()
            session.pop('loggedin', None)
            session.pop('mail', None)
            session.clear()
            flash('Unexpected error occurred in databse ')
            return render_template('newlogin.html')
            
    mycursor.execute(
        '''SELECT [Name],[PhoneNumber],[RecipientGiftStatus] FROM [dbo].[Recipient] where [Email]='%s' ''' % (mail))
    nameph = mycursor.fetchall()
    for (name_r, ph, cartsts) in nameph:
        name_res = name_r
        phno = ph
        cartss = cartsts
    mycursor.execute("SELECT * FROM [dbo].[GiftCycle]")
    gift = mycursor.fetchall()
    mycursor.execute(
        '''Select [OrderId],[OrderNumber],[OrderDate],[RecipientId],[GiftCycleId],[ShippingAddress],[ShippingCity],[ShippingState],[ShippingZIP],[ShippingCountry],[DeliveryURL],[DockerNumber],[DockerDateUpdated],[ShippingDate],[CreateUserId],[UpdateUserId],[CreateDate],[UpdateDate] from [dbo].[Order] where [RecipientId]='%s' ''' % (resid))
    orders = mycursor.fetchall()
    mycursor.execute(
                '''SELECT [reason] FROM [dbo].[OrderStatus] left join [dbo].[Order] on [dbo].[OrderStatus].OrderId=[dbo].[Order].OrderId where [dbo].[Order].RecipientId='%s' ''' % (resid,))
    reason = mycursor.fetchall()
    for (GiftCycleId, GiftCycleDesc, GiftDesc, StartDate, EndDate) in gift:
        return render_template('dashboard.html', mail=mail, naam=name_res, phno=phno, giftcycledecr=GiftCycleDesc, carts=cartss, orders=orders,reason=reason)


@app.route('/save', methods=["post"])
def save():
    name = request.form['name']
    mob = request.form['phno']
    address = request.form['address']
    country = request.form['country']
    state = request.form['state']
    city = request.form['city']
    pincode = request.form['pincode']
    try:
        
        mycursor.execute(''' update [dbo].[order] set [GiftCycleId]=1 ,[ShippingAddress]='%s'  ,[ShippingCity]='%s',[ShippingState]='%s',[ShippingZIP]='%s'  ,[ShippingCountry]='%s' where [RecipientId]='%s' ''' % (
        address, city, state, pincode, country, resid,))
        mydb.commit()
    except:
        try:
            mycursor.execute(
                '''SELECT [Name],[PhoneNumber],[RecipientGiftStatus] FROM [dbo].[Recipient] where [Email]='%s' ''' % (mail))
            nameph = mycursor.fetchall()
            for (name_r, ph, cartsts) in nameph:
                name_res = name_r
                phno = ph
                cartss = cartsts
            mycursor.execute("SELECT * FROM [dbo].[GiftCycle]")
            gift = mycursor.fetchall()
            mycursor.execute(
                '''Select [OrderId],[OrderNumber],[OrderDate],[RecipientId],[GiftCycleId],[ShippingAddress],[ShippingCity],[ShippingState],[ShippingZIP],[ShippingCountry],[DeliveryURL],[DockerNumber],[DockerDateUpdated],[ShippingDate],[CreateUserId],[UpdateUserId],[CreateDate],[UpdateDate] from [dbo].[Order] where [RecipientId]='%s' ''' % (resid))
            orders = mycursor.fetchall()
            mycursor.execute(
                '''SELECT [reason] FROM [dbo].[OrderStatus] left join [dbo].[Order] on [dbo].[OrderStatus].OrderId=[dbo].[Order].OrderId where [dbo].[Order].RecipientId='%s' ''' % (resid,))
            reason = mycursor.fetchall()
            for (GiftCycleId, GiftCycleDesc, GiftDesc, StartDate, EndDate) in gift:
                return render_template('dashboard.html', mail=mail, naam=name_res, phno=phno, giftcycledecr=GiftCycleDesc, carts=cartss, orders=orders,reason=reason)
        except:
            session['_flashes'].clear()
            session.pop('loggedin', None)
            session.pop('mail', None)
            session.clear()
            flash('Unexpected error occurred in databse ')
            return render_template('newlogin.html')
            

        
    mycursor.execute(
        '''SELECT [Name],[PhoneNumber],[RecipientGiftStatus] FROM [dbo].[Recipient] where [Email]='%s' ''' % (mail))
    nameph = mycursor.fetchall()
    for (name_r, ph, cartsts) in nameph:
        name_res = name_r
        phno = ph
        cartss = cartsts
    mycursor.execute("SELECT * FROM [dbo].[GiftCycle]")
    gift = mycursor.fetchall()
    mycursor.execute(
        '''Select [OrderId],[OrderNumber],[OrderDate],[RecipientId],[GiftCycleId],[ShippingAddress],[ShippingCity],[ShippingState],[ShippingZIP],[ShippingCountry],[DeliveryURL],[DockerNumber],[DockerDateUpdated],[ShippingDate],[CreateUserId],[UpdateUserId],[CreateDate],[UpdateDate] from [dbo].[Order] where [RecipientId]='%s' ''' % (resid))
    orders = mycursor.fetchall()
    mycursor.execute(
                '''SELECT [reason] FROM [dbo].[OrderStatus] left join [dbo].[Order] on [dbo].[OrderStatus].OrderId=[dbo].[Order].OrderId where [dbo].[Order].RecipientId='%s' ''' % (resid,))
    reason = mycursor.fetchall()
    for (GiftCycleId, GiftCycleDesc, GiftDesc, StartDate, EndDate) in gift:
        return render_template('dashboard.html', mail=mail, naam=name_res, phno=phno, giftcycledecr=GiftCycleDesc, carts=cartss, orders=orders,reason=reason)


@app.route('/placeorder', methods=["post"])
def placeorder():
    try:
        mycursor.execute(
            ''' update [dbo].[Recipient] set RecipientGiftStatus='O' where [RecipientId]='%s' ''' % (resid,))
        mydb.commit()
    except:
        try:
            mycursor.execute(
                '''SELECT [Name],[PhoneNumber],[RecipientGiftStatus] FROM [dbo].[Recipient] where [Email]='%s' ''' % (mail))
            nameph = mycursor.fetchall()
            mycursor.execute("SELECT * FROM [dbo].[GiftCycle]")
            gift = mycursor.fetchall()
            mycursor.execute(
                '''Select  [OrderId],[OrderNumber] from [dbo].[Order] where [OrderNumber] IS NOT NULL ''')
            biggestno = mycursor.fetchall()
            for (name_r, ph, cartsts) in nameph:
                name_res = name_r
                phno = ph
                cartss = cartsts
            mycursor.execute(
            '''Select [OrderId],[OrderNumber],[OrderDate],[RecipientId],[GiftCycleId],[ShippingAddress],[ShippingCity],[ShippingState],[ShippingZIP],[ShippingCountry],[DeliveryURL],[DockerNumber],[DockerDateUpdated],[ShippingDate],[CreateUserId],[UpdateUserId],[CreateDate],[UpdateDate] from [dbo].[Order] where [RecipientId]='%s' ''' % (resid))
            orders = mycursor.fetchall()
            mycursor.execute(
                '''SELECT [reason] FROM [dbo].[OrderStatus] left join [dbo].[Order] on [dbo].[OrderStatus].OrderId=[dbo].[Order].OrderId where [dbo].[Order].RecipientId='%s' ''' % (resid,))
            reason = mycursor.fetchall()
    
            for (GiftCycleId, GiftCycleDesc, GiftDesc, StartDate, EndDate) in gift:
                flash("Because of an error, your purchase was not placed, try again later")
                return render_template('dashboard.html', mail=mail, naam=name_res, phno=phno, giftcycledecr=GiftCycleDesc, carts=cartss, orders=orders,reason=reason)
            
        except:
            session['_flashes'].clear()
            session.pop('loggedin', None)
            session.pop('mail', None)
            session.clear()
            flash('Unexpected error occurred in databse ')
            return render_template('newlogin.html')
    mycursor.execute(
        '''SELECT [Name],[PhoneNumber],[RecipientGiftStatus] FROM [dbo].[Recipient] where [Email]='%s' ''' % (mail))
    nameph = mycursor.fetchall()
    mycursor.execute("SELECT * FROM [dbo].[GiftCycle]")
    gift = mycursor.fetchall()
    mycursor.execute(
        '''Select  [OrderId],[OrderNumber] from [dbo].[Order] where [OrderNumber] IS NOT NULL ''')
    biggestno = mycursor.fetchall()
    for (name_r, ph, cartsts) in nameph:
        name_res= name_r
        phno = ph
        cartss = cartsts
    
    zeb = 0
    prev = 0
    for (id, no) in biggestno:
        if (zeb):
            x = int((no[-4:]))
            Gift_Cycle_Id = int((no[3:5]))
            if (Gift_Cycle_Id == 1):
                if (prev < x):
                    prev = x
        else:
            x = int((no[-4:]))
            prev = x
            zeb = 1
    prev = str(prev+1)
    cal = 10-len(prev)

    # yha gift cycle ko lena h db s abhi nhi kiya y
    gfcycle = '1'
    if (len(gfcycle) == 1):
        orderid = 'O#-0'+gfcycle+'-0000'
    if (len(gfcycle) == 2):
        orderid = 'O#-'+gfcycle+'-0000'
    neworderid = orderid[0:cal]+prev
    try:
        mycursor.execute(
        '''Select [ShippingAddress],[ShippingCity],[ShippingState],[ShippingZIP],[ShippingCountry] from [dbo].[Order] where [RecipientId]='%s' ''' % (resid))
        mul = mycursor.fetchall()
        for(sad,scity,sstaet,szip,scon) in mul:

            message = MIMEMultipart("alternatives")
            message['Subject']='Order Confirmation'
            html="""
            <html>
                <head>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                </style>
                </head>
                <body>
                <div>
                    <h1>eGiftPortal</h1>
                    <h3>Thank you for your purchase!</h3>
                    <b>Your Order Number is: %s</b>
                    <p>We're getting your order ready to be shipped.We will notify you when it has<br> been sent.</p>
                    <p>Login to see your order</p>
                    <a href="http://rewards.centralindia.cloudapp.azure.com:5000/"
                        style="height:200px; background-color:blue; color:white; text-decoration:none; padding:8px; margin-bottom:10px; border: 1px solid  black;">
                        Login</a>
                    <br>
                    <br>
                    <h4>Order summary</h4>
                    <hr>
                    <table>
                        <tr>
                            <td style="height: 60px;">
                            <img src=""  alt="gift" style="height: 50px; border: 1px solid black;">
                            </td>
                            <td style="height:60px;">
                            <p>Appreciation Reward</p>
                            </td>
                        </tr>
                    </table>
                    <table>
                        <tr>
                            <h4>Shipping Information</h4>
                        </tr>
                        <tr>
                            <td>
                            <b>%s</b>
                            </td>
                        </tr>
                        <tr>
                            <td>
                            <p>%s %s %s %s %s</p>
                            </td>
                        </tr>
                    </table >
                    
                    <hr>
                    
                    <p style="text-align:center; margin-top:5px;">
                    If you have any questions,reply to this email or contact us at %s
                    </p>
                </div>
                </body>
            </html>
            """%(neworderid,name_res,sad,scity,sstaet,szip,scon,email_id,)
        htmlpart=MIMEText(html,'html')
        message.attach(htmlpart)
        server = sp.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_id, email_id_password)
        server.sendmail(email_id, mail, message.as_string())
        server.quit()
    except:
        mycursor.execute(
            ''' update [dbo].[Recipient] set RecipientGiftStatus='A' where [RecipientId]='%s' ''' % (resid,))
        mydb.commit()
        mycursor.execute(
        '''Select [OrderId],[OrderNumber],[OrderDate],[RecipientId],[GiftCycleId],[ShippingAddress],[ShippingCity],[ShippingState],[ShippingZIP],[ShippingCountry],[DeliveryURL],[DockerNumber],[DockerDateUpdated],[ShippingDate],[CreateUserId],[UpdateUserId],[CreateDate],[UpdateDate] from [dbo].[Order] where [RecipientId]='%s' ''' % (resid))
        orders = mycursor.fetchall()
        mycursor.execute(
                '''SELECT [reason] FROM [dbo].[OrderStatus] left join [dbo].[Order] on [dbo].[OrderStatus].OrderId=[dbo].[Order].OrderId where [dbo].[Order].RecipientId='%s' ''' % (resid,))
        reason = mycursor.fetchall()
        for (GiftCycleId, GiftCycleDesc, GiftDesc, StartDate, EndDate) in gift:
            flash("Because of an error, your purchase was not placed, try again later")
            return render_template('dashboard.html', mail=mail, naam=name_res, phno=phno, giftcycledecr=GiftCycleDesc, carts=cartss, orders=orders,reason=reason)

    try:   
        mycursor.execute('''Update [dbo].[Order] set [OrderDate]='%s',[OrderNumber]='%s'  where [RecipientId]='%s' ''' % (
            today,neworderid, resid))
        mydb.commit()
    except:
        mycursor.execute(
        '''Select [OrderId],[OrderNumber],[OrderDate],[RecipientId],[GiftCycleId],[ShippingAddress],[ShippingCity],[ShippingState],[ShippingZIP],[ShippingCountry],[DeliveryURL],[DockerNumber],[DockerDateUpdated],[ShippingDate],[CreateUserId],[UpdateUserId],[CreateDate],[UpdateDate] from [dbo].[Order] where [RecipientId]='%s' ''' % (resid))
        orders = mycursor.fetchall()
        # x=list(orders[0])
        # x[1]='ok'
        # print(x)
        mycursor.execute(
                '''SELECT [reason] FROM [dbo].[OrderStatus] left join [dbo].[Order] on [dbo].[OrderStatus].OrderId=[dbo].[Order].OrderId where [dbo].[Order].RecipientId='%s' ''' % (resid,))
        reason = mycursor.fetchall()
        for (GiftCycleId, GiftCycleDesc, GiftDesc, StartDate, EndDate) in gift:
            flash("Because of an error, your purchase was not placed, try again later")
            return render_template('dashboard.html', mail=mail, naam=name_res, phno=phno, giftcycledecr=GiftCycleDesc, carts=cartss, orders=orders,reason=reason)

        
    mycursor.execute(
        '''Select [OrderId],[OrderNumber],[OrderDate],[RecipientId],[GiftCycleId],[ShippingAddress],[ShippingCity],[ShippingState],[ShippingZIP],[ShippingCountry],[DeliveryURL],[DockerNumber],[DockerDateUpdated],[ShippingDate],[CreateUserId],[UpdateUserId],[CreateDate],[UpdateDate] from [dbo].[Order] where [RecipientId]='%s' ''' % (resid))
    orders = mycursor.fetchall()
    mycursor.execute(
                '''SELECT [reason] FROM [dbo].[OrderStatus] left join [dbo].[Order] on [dbo].[OrderStatus].OrderId=[dbo].[Order].OrderId where [dbo].[Order].RecipientId='%s' ''' % (resid,))
    reason = mycursor.fetchall()
    # x=list(orders[0])
    # x[1]='ok'
    # print(x)
    for (GiftCycleId, GiftCycleDesc, GiftDesc, StartDate, EndDate) in gift:
        return render_template('dashboard.html', mail=mail, naam=name_res, phno=phno, giftcycledecr=GiftCycleDesc, carts=cartss, orders=orders,reason=reason)


@app.route('/addcart', methods=["post"])
def addcart():
    mails = request.form['vlan']
    try:     
        mycursor.execute(
        '''Update [dbo].[Recipient] set [RecipientGiftStatus]='C' where [Email]='%s' ''' % (mails,))
        mydb.commit()
    except:
        try:
            mycursor.execute(
                '''SELECT [Name],[PhoneNumber],[RecipientGiftStatus] FROM [dbo].[Recipient] where [Email]='%s' ''' % (mail))
            nameph = mycursor.fetchall()
            for (name_r, ph, cartsts) in nameph:
                name_res = name_r
                phno = ph
                cartss = cartsts
            mycursor.execute("SELECT * FROM [dbo].[GiftCycle]")
            gift = mycursor.fetchall()
            mycursor.execute(
                '''SELECT [reason] FROM [dbo].[OrderStatus] left join [dbo].[Order] on [dbo].[OrderStatus].OrderId=[dbo].[Order].OrderId where [dbo].[Order].RecipientId='%s' ''' % (resid,))
            reason = mycursor.fetchall()
            for (GiftCycleId, GiftCycleDesc, GiftDesc, StartDate, EndDate) in gift:
                flash('The cart has not been changed due to a error, try again later')
                return render_template('dashboard.html', mail=mail, naam=name_res, phno=phno, giftcycledecr=GiftCycleDesc, carts=cartss,reason=reason)
        except:
            session['_flashes'].clear()
            session.pop('loggedin', None)
            session.pop('mail', None)
            session.clear()
            flash('Unexpected error occurred in databse ')
            return render_template('newlogin.html')

        
    mycursor.execute(
        '''SELECT [Name],[PhoneNumber],[RecipientGiftStatus] FROM [dbo].[Recipient] where [Email]='%s' ''' % (mail))
    nameph = mycursor.fetchall()
    for (name_r, ph, cartsts) in nameph:
        name_res = name_r
        phno = ph
        cartss = cartsts
    mycursor.execute("SELECT * FROM [dbo].[GiftCycle]")
    gift = mycursor.fetchall()
    mycursor.execute(
                '''SELECT [reason] FROM [dbo].[OrderStatus] left join [dbo].[Order] on [dbo].[OrderStatus].OrderId=[dbo].[Order].OrderId where [dbo].[Order].RecipientId='%s' ''' % (resid,))
    reason = mycursor.fetchall()
    for (GiftCycleId, GiftCycleDesc, GiftDesc, StartDate, EndDate) in gift:
        return render_template('dashboard.html', mail=mail, naam=name_res, phno=phno, giftcycledecr=GiftCycleDesc, carts=cartss,reason=reason)


@app.route('/verification', methods=["post"])
def verification():
    new_pwd = request.form['pwds']
    if (comp == 'I'):
        mssg = 'OTP'
        if(new_pwd==auth):
            return render_template('newlogin.html', otp=0, admin=0, otps=0, mail=mail, cpas=1, cpwd='1', comp=1, mssg=mssg)
        else:
             return render_template('newlogin.html', otp=1, admin=0, otps=0, mail=mail, cpas=1, cpwd='0')

    if ((new_pwd == auth)):
        if (admin):
            # session start
            session['loggedin'] = True
            session['mail'] = mail
            mssg = 'Password'
            return render_template('newlogin.html', otp=1, admin=0, otps=0, mail=mail, cpas=1, cpwd='1', mssg=mssg)
        else:
            # session start
            session['loggedin'] = True
            session['mail'] = mail
            mssg = 'Password'
            return render_template('newlogin.html', otp=1, admin=1, otps=0, mail=mail, cpas=1, cpwd='1', mssg=mssg)
    else:
        return render_template('newlogin.html', otp=1, admin=0, otps=0, mail=mail, cpas=1, cpwd='0')


@app.route('/forgot_pwd', methods=["post"])
def forgot_pwd():
    email = request.form['email']
    try:
        mycursor.execute(
            '''SELECT [UserEmail] FROM [dbo].[User] where [UserEmail]='%s' ''' % (email))
        forgot = mycursor.fetchone()
    except:
            session['_flashes'].clear()
            session.pop('loggedin', None)
            session.pop('mail', None)
            session.clear()
            flash('Unexpected error occurred in databse ')
            return render_template('newlogin.html')
    if (forgot):
        otp = ''.join([str(rd.randint(0, 9)) for x in range(6)])
        auth = otp
        global ab
        global em
        em = email
        ab = otp
        text = 'verification code is '+otp
        try:
             message = MIMEMultipart("alternatives")
             message['Subject']='OTP-Verification'
             html="""
             <html>
             <head>
             <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">  
            
             </head>
             <body style="background-color:White;">
            
             <h1>
                eGiftPortal
                </h1>
                <p>Dear User,</p>
                <b >
                Enter the OTP for email validation : %s
                </b>
                <p> Do not share this OTP with anyone.</p>
                <hr>
            
                <p style="text-align:center; margin-top:5px;">
                If you have any questions,reply to this email or contact us at %s
                </p>
                </body>
             </html>
             """%(otp,email_id,)
             htmlpart=MIMEText(html,'html')
             message.attach(htmlpart)


             server = sp.SMTP('smtp.gmail.com', 587)
             server.starttls()
             server.login(email_id, email_id_password)
             server.sendmail(email_id, mail, message.as_string())
             server.quit()
        except:
            flash('The verification code has not been sent.')
            return render_template('newlogin.html')
            
        return render_template('newlogin.html', otps=0, admin=0, otp=otp, mail=email, smt=1, ld=1 ,otimp=otp)

    else:

        return render_template('newlogin.html', otp=1, admin=0, otps=0, mail=mail, ld=0)


@app.route('/veri', methods=["post"])
def veri():
    otp = request.form['otp']
    if (otp == ab):

        return render_template('newlogin.html', otps=0, admin=0, otp=otp, mail=mail, smt=1, ld=2)
    else:

        return render_template('newlogin.html', otp=1, admin=0, otps=0, mail=mail, ld=4)


@app.route('/setpwd', methods=["post"])
def setpwd():
    passw = request.form['pwd']
    cpasw = request.form['cpwds']
    if (passw == cpasw):
        try:
            mycursor.execute(
                '''Update [dbo].[User] set [UserPassword]='%s' where [UserEmail]='%s' ''' % (passw, em,))
            mydb.commit()
        except:
            flash('Unexpected error occurred in databse ')
            return render_template('newlogin.html')
            
        return render_template('newlogin.html', admin=0, otp=0, mail=mail, smt=1, ld=3)
    else:
        return render_template('newlogin.html', otp=1, admin=0, otps=0, mail=mail)


@app.route('/ship_inti', methods=["post"])
def ship_inti():
    temp_admin = '4'
    usr='1'
    try:
        getdatacmd = 'SELECT [OrderId],[OrderNumber],[OrderDate],[RecipientId],[GiftCycleId],[ShippingAddress],[ShippingCity],[ShippingState],[ShippingZIP],[ShippingCountry],[DeliveryURL],[DockerNumber],[DockerDateUpdated],[ShippingDate],[CreateUserId],[UpdateUserId],[CreateDate],[UpdateDate] FROM [dbo].[Order] where [OrderNumber] IS NOT NULL AND [DeliveryURL] IS NULL'
        filename = 'static/files/shipment_pending_delivery.csv'
        realname = 'shipment_pending_delivery.csv'
        sql_query = pd.read_sql_query(getdatacmd, mydb)
        df = pd.DataFrame(sql_query)
        df.to_csv(filename, index=False)
    except:
        try:
            usr='2'
            mycursor.execute(
                '''Select [file_naam] ,[file_desc] from [dbo].[csv_data] where [id]=%d''' % (6,))
            csvname = mycursor.fetchall()
            mycursor.execute(getdatacmd)
            held = mycursor.fetchall()
            mycursor.execute(
                '''SELECT [RecipientId],[Name],[Email],[PhoneNumber],[RecipientGiftStatus] FROM [dbo].[Recipient] ''')
            resi = mycursor.fetchall()
            mycursor.execute('''SELECT * FROM[dbo].[GiftCycle] ''')
            gfcycle = mycursor.fetchall()

            mycursor.execute('''  select [dbo].[Recipient].[RecipientId], [Name]  ,[Email] ,[PhoneNumber] ,[RecipientGiftStatus],[OrderNumber] from [dbo].[Recipient]  left join [dbo].[Order] on [dbo].[Recipient].RecipientId=[dbo].[Order].[RecipientId] where [RecipientGiftStatus]!='N' and [RecipientGiftStatus]!='C' and [RecipientGiftStatus]!='A'  ''')
            ordered=mycursor.fetchall()
            flash('Not Generating CSV Attempt once more')
            return render_template('admin.html', mail=mail, resi=resi, gcycle=gfcycle, thambu=bus, temp=temp_admin, toos=totalorders, counts=counts, mys=mys, cs=csvname, held=held,usrq=usr,ordered=ordered)
        except:
            session['_flashes'].clear()
            session.pop('loggedin', None)
            session.pop('mail', None)
            session.clear()
            flash('Unexpected error occurred in databse ')
            return render_template('newlogin.html')
                
    mycursor.execute(
        '''Select [file_naam] ,[file_desc] from [dbo].[csv_data] where [id]=%d''' % (6,))
    csvname = mycursor.fetchall()
    mycursor.execute(getdatacmd)
    held = mycursor.fetchall()
    mycursor.execute(
        '''SELECT [RecipientId],[Name],[Email],[PhoneNumber],[RecipientGiftStatus] FROM [dbo].[Recipient] ''')
    resi = mycursor.fetchall()
    mycursor.execute('''SELECT * FROM[dbo].[GiftCycle] ''')
    gfcycle = mycursor.fetchall()
    mycursor.execute('''  select [dbo].[Recipient].[RecipientId], [Name]  ,[Email] ,[PhoneNumber] ,[RecipientGiftStatus],[OrderNumber] from [dbo].[Recipient]  left join [dbo].[Order] on [dbo].[Recipient].RecipientId=[dbo].[Order].[RecipientId] where [RecipientGiftStatus]!='N' and [RecipientGiftStatus]!='C' and [RecipientGiftStatus]!='A'  ''')
    ordered=mycursor.fetchall()
    return render_template('admin.html', mail=mail, resi=resi, gcycle=gfcycle, thambu=bus, temp=temp_admin, toos=totalorders, counts=counts, mys=mys, cs=csvname, held=held,usrq=usr,ordered=ordered)


@app.route('/back', methods=["post"])
def back():
    mycursor.execute("SELECT * FROM [dbo].[User]")
    myresult = mycursor.fetchall()
    temp = 0
    return render_template('newlogin.html', temp=temp)



@app.route('/pwds', methods=["post"])
def pwds():
    pwd = request.form['password']
    email = request.form['email']
    full_name = request.form['full_name']
    phno = int(request.form['phno'])
    try:
        mycursor.execute(
            '''Update [dbo].[User] set [UserPassword]='%s',[UserAuthenticationStatus]='%c' where [UserEmail]='%s' ''' % (pwd, 'C', email,))
        mycursor.execute('''Update [dbo].[Recipient] set [Name]='%s',[PhoneNumber]=%d where [Email]='%s' ''' % (
            full_name, phno, email,))
        mydb.commit()
    except:
        flash(email+' your Password is not  created')
        return render_template('newlogin.html')
        
    
    flash(email+' your Password is sucessfully created')
    return render_template('newlogin.html',mrd=1)


# admin page m Employee m kholna h value=2
@app.route('/dele/<string:id_data>', methods=['GET'])
def dele(id_data):
    temp_admin = '2'
    data_user = id_data
    try:
        add_user = '''DELETE FROM [dbo].[Recipient] WHERE [Email]='%s' ''' % data_user
        mycursor.execute(add_user)
        add_user = '''DELETE FROM [dbo].[User] WHERE [UserEmail]='%s' ''' % data_user
        mycursor.execute(add_user)
        mydb.commit()
    except:
        try:
            mycursor.execute(
            '''SELECT [RecipientId],[Name],[Email],[PhoneNumber],[RecipientGiftStatus] FROM [dbo].[Recipient] ''')
            resi = mycursor.fetchall()
            mycursor.execute('''SELECT * FROM[dbo].[GiftCycle] ''')
            gfcycle = mycursor.fetchall()
            mycursor.execute('''  select [dbo].[Recipient].[RecipientId], [Name]  ,[Email] ,[PhoneNumber] ,[RecipientGiftStatus],[OrderNumber] from [dbo].[Recipient]  left join [dbo].[Order] on [dbo].[Recipient].RecipientId=[dbo].[Order].[RecipientId] where [RecipientGiftStatus]!='N' and [RecipientGiftStatus]!='C' and [RecipientGiftStatus]!='A'  ''')
            ordered=mycursor.fetchall()
            flash("No record has been removed because of delete query")
            return render_template('admin.html', mail=mail, resi=resi, gcycle=gfcycle, thambu=bus, temp=temp_admin, toos=totalorders, counts=counts, mys=mys,ordered=ordered)
        except:
            session['_flashes'].clear()
            session.pop('loggedin', None)
            session.pop('mail', None)
            session.clear()
            flash('Unexpected error occurred in databse ')
            return render_template('newlogin.html')
        
    mycursor.execute(
        '''SELECT [RecipientId],[Name],[Email],[PhoneNumber],[RecipientGiftStatus] FROM [dbo].[Recipient] ''')
    resi = mycursor.fetchall()
    mycursor.execute('''SELECT * FROM[dbo].[GiftCycle] ''')
    gfcycle = mycursor.fetchall()
    mycursor.execute('''  select [dbo].[Recipient].[RecipientId], [Name]  ,[Email] ,[PhoneNumber] ,[RecipientGiftStatus],[OrderNumber] from [dbo].[Recipient]  left join [dbo].[Order] on [dbo].[Recipient].RecipientId=[dbo].[Order].[RecipientId] where [RecipientGiftStatus]!='N' and [RecipientGiftStatus]!='C' and [RecipientGiftStatus]!='A'  ''')
    ordered=mycursor.fetchall()
    flash("Record Has Been Deleted Successfully")
    return render_template('admin.html', mail=mail, resi=resi, gcycle=gfcycle, thambu=bus, temp=temp_admin, toos=totalorders, counts=counts, mys=mys,ordered=ordered)


# admin page m giftcycle m kholna h vaue=3
@app.route('/delete/<int:id_data>', methods=['GET'])
def delete(id_data):
    temp_admin = '3'
    mails = mail
    data_user = id_data
    try:
        add_user = '''DELETE FROM [dbo].[GiftCycle] WHERE [GiftCycleId]=%d''' % data_user
        mycursor.execute(add_user)
        mydb.commit()
    except:
        try:
            mycursor.execute(
            '''SELECT [RecipientId],[Name],[Email],[PhoneNumber],[RecipientGiftStatus] FROM [dbo].[Recipient] ''')
            resi = mycursor.fetchall()
            mycursor.execute('''SELECT * FROM[dbo].[GiftCycle] ''')
            gfcycle = mycursor.fetchall()
            mycursor.execute('''  select [dbo].[Recipient].[RecipientId], [Name]  ,[Email] ,[PhoneNumber] ,[RecipientGiftStatus],[OrderNumber] from [dbo].[Recipient]  left join [dbo].[Order] on [dbo].[Recipient].RecipientId=[dbo].[Order].[RecipientId] where [RecipientGiftStatus]!='N' and [RecipientGiftStatus]!='C' and [RecipientGiftStatus]!='A'  ''')
            ordered=mycursor.fetchall()
            flash("No record has been removed")
            return render_template('admin.html', mail=mail, resi=resi, gcycle=gfcycle, thambu=bus, temp=temp_admin, toos=totalorders, counts=counts, mys=mys,ordered=ordered)
        except:
            session['_flashes'].clear()
            session.pop('loggedin', None)
            session.pop('mail', None)
            session.clear()
            flash('Unexpected error occurred in databse ')
            return render_template('newlogin.html')
    mycursor.execute(
        '''SELECT [RecipientId],[Name],[Email],[PhoneNumber],[RecipientGiftStatus] FROM [dbo].[Recipient] ''')
    resi = mycursor.fetchall()
    mycursor.execute('''SELECT * FROM[dbo].[GiftCycle] ''')
    gfcycle = mycursor.fetchall()
    mycursor.execute('''  select [dbo].[Recipient].[RecipientId], [Name]  ,[Email] ,[PhoneNumber] ,[RecipientGiftStatus],[OrderNumber] from [dbo].[Recipient]  left join [dbo].[Order] on [dbo].[Recipient].RecipientId=[dbo].[Order].[RecipientId] where [RecipientGiftStatus]!='N' and [RecipientGiftStatus]!='C' and [RecipientGiftStatus]!='A'  ''')
    ordered=mycursor.fetchall()
    flash("Record Has Been Deleted Successfully")
    return render_template('admin.html', mail=mail, resi=resi, gcycle=gfcycle, thambu=bus, temp=temp_admin, toos=totalorders, counts=counts, mys=mys,ordered=ordered)

# admin page m Employee m kholna h value=5
@app.route('/delet/<string:id_data>', methods=['GET','POST'])
def delet(id_data):
    temp_admin = '5'
    data_user = id_data
    try:
        add_user = '''DELETE FROM [dbo].[Order] WHERE [RecipientId]='%s' ''' % data_user
        mycursor.execute(add_user)
        add_user = '''Update  [dbo].[Recipient] set [RecipientGiftStatus]='N' WHERE [RecipientId]='%s' ''' % data_user
        mycursor.execute(add_user)
        mydb.commit()
    except:
        try:
            mycursor.execute(
            '''SELECT [RecipientId],[Name],[Email],[PhoneNumber],[RecipientGiftStatus] FROM [dbo].[Recipient] ''')
            resi = mycursor.fetchall()
            mycursor.execute('''SELECT * FROM[dbo].[GiftCycle] ''')
            gfcycle = mycursor.fetchall()
            mycursor.execute('''  select [dbo].[Recipient].[RecipientId], [Name]  ,[Email] ,[PhoneNumber] ,[RecipientGiftStatus],[OrderNumber] from [dbo].[Recipient]  left join [dbo].[Order] on [dbo].[Recipient].RecipientId=[dbo].[Order].[RecipientId] where [RecipientGiftStatus]!='N' and [RecipientGiftStatus]!='C' and [RecipientGiftStatus]!='A'  ''')
            ordered=mycursor.fetchall()
            flash("No record has been removed because of delete query")
            return render_template('admin.html', mail=mail, resi=resi, gcycle=gfcycle, thambu=bus, temp=temp_admin, toos=totalorders, counts=counts, mys=mys,ordered=ordered)
        except:
            session['_flashes'].clear()
            session.pop('loggedin', None)
            session.pop('mail', None)
            session.clear()
            flash('Unexpected error occurred in databse ')
            return render_template('newlogin.html')
        
    mycursor.execute(
        '''SELECT [RecipientId],[Name],[Email],[PhoneNumber],[RecipientGiftStatus] FROM [dbo].[Recipient] ''')
    resi = mycursor.fetchall()
    mycursor.execute('''SELECT * FROM[dbo].[GiftCycle] ''')
    gfcycle = mycursor.fetchall()
    mycursor.execute('''  select [dbo].[Recipient].[RecipientId], [Name]  ,[Email] ,[PhoneNumber] ,[RecipientGiftStatus],[OrderNumber] from [dbo].[Recipient]  left join [dbo].[Order] on [dbo].[Recipient].RecipientId=[dbo].[Order].[RecipientId] where [RecipientGiftStatus]!='N' and [RecipientGiftStatus]!='C' and [RecipientGiftStatus]!='A'  ''')
    ordered=mycursor.fetchall()
    flash("Record Has Been Deleted Successfully")
    return render_template('admin.html', mail=mail, resi=resi, gcycle=gfcycle, thambu=bus, temp=temp_admin, toos=totalorders, counts=counts, mys=mys,ordered=ordered)


@app.route('/csvupdate', methods=["post"])
def csvupdate():
    temp_admin = '4'
    mycursor.execute(
        '''Select [file_naam] ,[file_desc] from [dbo].[csv_data] where [id]=%d''' % (6,))
    csvname = mycursor.fetchall()
    mycursor.execute(
        '''SELECT [RecipientId],[Name],[Email],[PhoneNumber],[RecipientGiftStatus] FROM [dbo].[Recipient] ''')
    resi = mycursor.fetchall()
    mycursor.execute('''SELECT * FROM[dbo].[GiftCycle] ''')
    gfcycle = mycursor.fetchall()
    mycursor.execute('''  select [dbo].[Recipient].[RecipientId], [Name]  ,[Email] ,[PhoneNumber] ,[RecipientGiftStatus],[OrderNumber] from [dbo].[Recipient]  left join [dbo].[Order] on [dbo].[Recipient].RecipientId=[dbo].[Order].[RecipientId] where [RecipientGiftStatus]!='N' and [RecipientGiftStatus]!='C' and [RecipientGiftStatus]!='A'  ''')
    ordered=mycursor.fetchall()

    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        file_path = os.path.join(
            app.config['UPLOAD_FOLDER'], uploaded_file.filename)
        # set the file path
        uploaded_file.save(file_path)
        col_names = ['OrderId', 'OrderNumber', 'OrderDate', 'RecipientId', 'GiftCycleId', 'ShippingAddress', 'ShippingCity', 'ShippingState', 'ShippingZIP',
                     'ShippingCountry', 'DeliveryURL', 'DockerNumber', 'DockerDateUpdated', 'ShippingDate', 'CreateUserId', 'UpdateUserId', 'CreateDate', 'UpdateDate']
        # Use Pandas to parse the CSV file
        csvData = pd.read_csv(file_path, names=col_names, skiprows=1)
        # Loop through the Rows
        for i, row in csvData.iterrows():
            try:
                mycursor.execute('''UPDATE [dbo].[Order] set [DeliveryURL]='%s',[DockerNumber]='%s',[DockerDateUpdated]='%s',[ShippingDate]='%s' where [OrderId]=%d  ''' % (
                    row['DeliveryURL'], row['DockerNumber'], row['DockerDateUpdated'], row['ShippingDate'], row['OrderId'],))
                mydb.commit()
            except:
                flash('Csv not Inserted so first u download Csv from Generate csv then put edit it then insert ')
                return render_template('admin.html', mail=mail, resi=resi, gcycle=gfcycle, temp=temp_admin, cs=csvname, thambu=bus, toos=totalorders, counts=counts, mys=mys,usrq='3',ordered=ordered)
                
                
           
            mycursor.execute('''Select [Email] from [dbo].[Recipient] where [RecipientId]='%s' ''' % (
                row['RecipientId'],))
            mailforsend = mycursor.fetchall()
            for (x,) in mailforsend:
                try:
                    mycursor.execute('''update [dbo].[Recipient] set [RecipientGiftStatus]='S' where [Email]='%s' ''' % (x,))
                    mycursor.execute(
                    '''Select [OrderNumber],[DeliveryURL], [ShippingAddress],[ShippingCity],[ShippingState],[ShippingZIP],[ShippingCountry] from [dbo].[Order] where [RecipientId]='%s' ''' % (resid))
                    mult = mycursor.fetchall()
                    for(oid,durl,sad,scity,sstaet,szip,scon) in mult:
        
                        message = MIMEMultipart("alternatives")
                        message['Subject']='Order Shipped'
                        html="""
                        <html>
                            <head>
                            <meta name="viewport" content="width=device-width, initial-scale=1">
                            <style>
                            </style>
                            </head>
                            <body>
                            <div>
                                <h1>eGiftPortal</h1>
                                
                                <p>Congratulations %s your order is shipped with our delivery partner you can track your order from the link given below and you can track also on eGiftPortal</p>
                                <b>Your OrderId is : %s</b>
                                <p></p>
                                <a href=%s
                                    style="height:200px; background-color:blue; color:white; text-decoration:none; padding:8px; margin-bottom:10px; border: 1px solid  black;">
                                    Track your Order</a>
                                <br>
                                <br>
                                <h4>Order summary</h4>
                                <hr>
                                <table>
                                    <tr>
                                        <td style="height: 60px;">
                                        <img src=""  alt="gift" style="height: 50px; border: 1px solid black;">
                                        </td>
                                        <td style="height:60px;">
                                        <p>Appreciation Reward</p>
                                        </td>
                                    </tr>
                                </table>
                                <table>
                                    <tr>
                                        <h4>Shipping Information</h4>
                                    </tr>
                                    <tr>
                                        <td>
                                        <b>%s</b>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>
                                        <p>%s %s %s %s %s</p>
                                        </td>
                                    </tr>
                                </table >
                                
                                <hr>
                                
                                <p style="text-align:center; margin-top:5px;">
                                If you have any questions,reply to this email or contact us at %s
                                </p>
                            </div>
                            </body>
                        </html>
                            """%(name_res,oid,durl,name_res,sad,scity,sstaet,szip,scon,email_id,)
                        htmlpart=MIMEText(html,'html')
                        message.attach(htmlpart)
                        server = sp.SMTP('smtp.gmail.com', 587)
                        server.starttls()
                        server.login(email_id, email_id_password)
                        server.sendmail(email_id, x, message.as_string())
                        server.quit()
                except:
                        flash('Csv Inserted to db but mails are not sending ')
                        return render_template('admin.html', mail=mail, resi=resi, gcycle=gfcycle, temp=temp_admin, cs=csvname, thambu=bus, toos=totalorders, counts=counts, mys=mys,usrq='3',ordered=ordered)
        mydb.commit()
        flash('Shipment Added')
        return render_template('admin.html', mail=mail, resi=resi, gcycle=gfcycle, temp=temp_admin, cs=csvname, thambu=bus, toos=totalorders, counts=counts, mys=mys,usrq='3',ordered=ordered)
    else:
        flash('Please Insert a Csv file')
        return render_template('admin.html', mail=mail, resi=resi, gcycle=gfcycle, temp=temp_admin, cs=csvname, thambu=bus, toos=totalorders, counts=counts, mys=mys,usrq='3',ordered=ordered)


@app.route('/new_csv', methods=["post"])
def new_csv():
    temp_admin = '2'
    # get the uploaded file
    uploaded_file = request.files['file']
    GiftCyclefc = int(request.form['GiftCyclefc'])
    if uploaded_file.filename != '':
        file_path = os.path.join(
            app.config['UPLOAD_FOLDER'], uploaded_file.filename)
        # set the file path
        uploaded_file.save(file_path)
        col_names = ['email']
        # Use Pandas to parse the CSV file
        csvData = pd.read_csv(file_path, names=col_names, skiprows=1)
        # Loop through the Rows
        for i, row in csvData.iterrows():
            try:
                mycursor.execute('''insert into [dbo].[User] ([UserEmail],[UserAuthenticationStatus],[GiftCycleId]) values('%s','I',%d)  ''' % (
                    row['email'], GiftCyclefc,))
                mycursor.execute(
                    '''insert into [dbo].[Recipient] ([Email],[RecipientGiftStatus]) values('%s','N')  ''' % (row['email'],))
                mydb.commit()
            except:
                try:
                    mycursor.execute(
                    '''SELECT [RecipientId],[Name],[Email],[PhoneNumber],[RecipientGiftStatus] FROM [dbo].[Recipient] ''')
                    resi = mycursor.fetchall()
                    mycursor.execute('''SELECT * FROM[dbo].[GiftCycle] ''')
                    gfcycle = mycursor.fetchall()
                    mycursor.execute('''  select [dbo].[Recipient].[RecipientId], [Name]  ,[Email] ,[PhoneNumber] ,[RecipientGiftStatus],[OrderNumber] from [dbo].[Recipient]  left join [dbo].[Order] on [dbo].[Recipient].RecipientId=[dbo].[Order].[RecipientId] where [RecipientGiftStatus]!='N' and [RecipientGiftStatus]!='C' and [RecipientGiftStatus]!='A'  ''')
                    ordered=mycursor.fetchall()
                    flash('Unexpected error occurred in databse ')
                    return render_template('admin.html', mail=mail, resi=resi, gcycle=gfcycle, thambu=bus, temp=temp_admin, toos=totalorders, counts=counts, mys=mys,ordered=ordered)
                except:
                    session['_flashes'].clear()
                    session.pop('loggedin', None)
                    session.pop('mail', None)
                    session.clear()
                    flash('Unexpected error occurred in databse ')
                    return render_template('newlogin.html')
                

    mycursor.execute(
        '''SELECT [RecipientId],[Name],[Email],[PhoneNumber],[RecipientGiftStatus] FROM [dbo].[Recipient] ''')
    resi = mycursor.fetchall()
    mycursor.execute('''SELECT * FROM[dbo].[GiftCycle] ''')
    gfcycle = mycursor.fetchall()
    mycursor.execute('''  select [dbo].[Recipient].[RecipientId], [Name]  ,[Email] ,[PhoneNumber] ,[RecipientGiftStatus],[OrderNumber] from [dbo].[Recipient]  left join [dbo].[Order] on [dbo].[Recipient].RecipientId=[dbo].[Order].[RecipientId] where [RecipientGiftStatus]!='N' and [RecipientGiftStatus]!='C' and [RecipientGiftStatus]!='A'  ''')
    ordered=mycursor.fetchall()
    flash("Csv inserted Successfully")
    return render_template('admin.html', mail=mail, resi=resi, gcycle=gfcycle, thambu=bus, temp=temp_admin, toos=totalorders, counts=counts, mys=mys,ordered=ordered)


# admin page m giftcycle m kholna h vaue=3
@app.route('/newgiftcycle', methods=["post"])
def newgiftcycle():
    temp_admin = '3'
    gcycledesc = request.form['gcycledesc']
    giftdesc = request.form['giftdesc']
    startdate = request.form['startdate']
    enddate = request.form['enddate']
    try:
        mycursor.execute(''' insert into [dbo].[GiftCycle] ([GiftCycleDesc],[GiftDesc],[StartDate],[EndDate]) values ('%s','%s','%s','%s')''' % (
            gcycledesc, giftdesc, startdate, enddate,))
        mydb.commit()
    except:
        try:
            mycursor.execute(
            '''SELECT [RecipientId],[Name],[Email],[PhoneNumber],[RecipientGiftStatus] FROM [dbo].[Recipient] ''')
            resi = mycursor.fetchall()
            mycursor.execute('''SELECT * FROM[dbo].[GiftCycle] ''')
            gfcycle = mycursor.fetchall()
            mycursor.execute('''  select [dbo].[Recipient].[RecipientId], [Name]  ,[Email] ,[PhoneNumber] ,[RecipientGiftStatus],[OrderNumber] from [dbo].[Recipient]  left join [dbo].[Order] on [dbo].[Recipient].RecipientId=[dbo].[Order].[RecipientId] where [RecipientGiftStatus]!='N' and [RecipientGiftStatus]!='C' and [RecipientGiftStatus]!='A'  ''')
            ordered=mycursor.fetchall()
            flash('Some error in insertion')
            return render_template('admin.html', mail=mail, resi=resi, gcycle=gfcycle, thambu=bus, temp=temp_admin, toos=totalorders, counts=counts, mys=mys,ordered=ordered)
        except:
            session['_flashes'].clear()
            session.pop('loggedin', None)
            session.pop('mail', None)
            session.clear()
            flash('Unexpected error occurred in databse ')
            return render_template('newlogin.html')
        
    mycursor.execute(
        '''SELECT [RecipientId],[Name],[Email],[PhoneNumber],[RecipientGiftStatus] FROM [dbo].[Recipient] ''')
    resi = mycursor.fetchall()
    mycursor.execute('''SELECT * FROM[dbo].[GiftCycle] ''')
    gfcycle = mycursor.fetchall()
    mycursor.execute('''  select [dbo].[Recipient].[RecipientId], [Name]  ,[Email] ,[PhoneNumber] ,[RecipientGiftStatus],[OrderNumber] from [dbo].[Recipient]  left join [dbo].[Order] on [dbo].[Recipient].RecipientId=[dbo].[Order].[RecipientId] where [RecipientGiftStatus]!='N' and [RecipientGiftStatus]!='C' and [RecipientGiftStatus]!='A'  ''')
    ordered=mycursor.fetchall()
    flash('Your Gift cycle is created')
    return render_template('admin.html', mail=mail, resi=resi, gcycle=gfcycle, thambu=bus, temp=temp_admin, toos=totalorders, counts=counts, mys=mys,ordered=ordered)


# Adding new user to datebase emp page in admin page
@app.route('/new_emp', methods=["post"])
def new_emp():
    temp_admin = '2'
    newmail = str(request.form['newmail'])
    try:
        mycursor.execute(
            '''insert into [dbo].[User] ([UserEmail],[UserAuthenticationStatus],[GiftCycleId]) values('%s','I',1)  ''' % (newmail,))
        mycursor.execute(
            '''insert into [dbo].[Recipient] ([Email],[RecipientGiftStatus]) values('%s','N')  ''' % (newmail,))  
        mydb.commit() 
    except pyodbc.Error as drror:
        try:
            mycursor.execute(
            '''SELECT [RecipientId],[Name],[Email],[PhoneNumber],[RecipientGiftStatus] FROM [dbo].[Recipient] ''')
            resi = mycursor.fetchall()
            mycursor.execute('''SELECT * FROM[dbo].[GiftCycle] ''')
            gfcycle = mycursor.fetchall()
            mycursor.execute('''  select [dbo].[Recipient].[RecipientId], [Name]  ,[Email] ,[PhoneNumber] ,[RecipientGiftStatus],[OrderNumber] from [dbo].[Recipient]  left join [dbo].[Order] on [dbo].[Recipient].RecipientId=[dbo].[Order].[RecipientId] where [RecipientGiftStatus]!='N' and [RecipientGiftStatus]!='C' and [RecipientGiftStatus]!='A'  ''')
            ordered=mycursor.fetchall()
            if drror.args[0] == "23000":
                flash('This User is already in database ')
            else:
                flash('Unexpected error occurred in databse ')
            return render_template('admin.html', mail=mail, resi=resi, gcycle=gfcycle, thambu=bus, temp=temp_admin, toos=totalorders, counts=counts, mys=mys,ordered=ordered)
        except:
            session['_flashes'].clear()
            session.pop('loggedin', None)
            session.pop('mail', None)
            session.clear()
            flash('Unexpected error occurred in databse ')
            return render_template('newlogin.html')
        
    mycursor.execute(
        '''SELECT [RecipientId],[Name],[Email],[PhoneNumber],[RecipientGiftStatus] FROM [dbo].[Recipient] ''')
    resi = mycursor.fetchall()
    mycursor.execute('''SELECT * FROM[dbo].[GiftCycle] ''')
    gfcycle = mycursor.fetchall()
    mycursor.execute('''  select [dbo].[Recipient].[RecipientId], [Name]  ,[Email] ,[PhoneNumber] ,[RecipientGiftStatus],[OrderNumber] from [dbo].[Recipient]  left join [dbo].[Order] on [dbo].[Recipient].RecipientId=[dbo].[Order].[RecipientId] where [RecipientGiftStatus]!='N' and [RecipientGiftStatus]!='C' and [RecipientGiftStatus]!='A'  ''')
    ordered=mycursor.fetchall()
    message = MIMEMultipart("alternatives")
    message['Subject']='Welcome User'
    message['From']=email_id
    message['To']=newmail
    html="""
    <html>
      <head>
       <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">  
      
      </head>
      <body style="background-color:White;">
      
       <h1>
         eGiftPortal
         </h1>
         <h3>
         Activate your account
         </h3>
         <h5 style="color:#999999; ">
          Congratulations your email has been successfully added now you can complete the verification and activate the account through eGiftPortal link is given below
         </h5>
         
         <a href="http://rewards.centralindia.cloudapp.azure.com:5000/" style="height:200px; background-color:blue; color:white; text-decoration:none; padding:10px; margin-bottom:10px;"> Activate your account</a>
         <br>
         <br>
         <hr>
      
         <p style="text-align:center; margin-top:5px;">
         If you have any questions,reply to this email or contact us at %s
         </p>
         </body>
    </html>
    """%(email_id,)
    htmlpart=MIMEText(html,'html')
    message.attach(htmlpart)
    server = sp.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email_id, email_id_password)
    server.sendmail(email_id, newmail, message.as_string())
    server.quit()
    try:
        flash('new user created ')
        return render_template('admin.html', mail=mail, resi=resi, gcycle=gfcycle, thambu=bus, temp=temp_admin, toos=totalorders, counts=counts, mys=mys,ordered=ordered)
    except:
        session['_flashes'].clear()
        mycursor.execute(
        '''Delete [dbo].[User] where [UserEmail]='%s' ''' % (newmail,))
        mydb.commit()
        mycursor.execute(
        '''Delete [dbo].[Recipient] where [Email]='%s'  ''' % (newmail,))
        mydb.commit()
        session.pop('loggedin', None)
        session.pop('mail', None)
        session.clear()
        flash('Please check back after some time as this site is being maintained ')
        return render_template('newlogin.html')

# update gift cycle
@app.route('/update_giftcycle', methods=["post"])
def update_giftcycle():
    temp_admin = '3'
    gfid = int(request.form['gfid'])
    gcycledesc = request.form['gcycledesc']
    giftdesc = request.form['giftdesc']
    startdate = request.form['startdate']
    enddate = request.form['enddate']
    try:
        mycursor.execute('''update [dbo].[GiftCycle] set  [GiftCycleDesc]='%s',[GiftDesc]='%s',[StartDate]='%s',[EndDate]='%s' where [GiftCycleId]=%d ''' % (
            gcycledesc, giftdesc, startdate, enddate, gfid,))
        mydb.commit()
    except:
            session.pop('loggedin', None)
            session.pop('mail', None)
            session.clear()
            flash('Unexpected error occurred in databse ')
            return render_template('newlogin.html')
    try:
        mycursor.execute(
            '''SELECT [RecipientId],[Name],[Email],[PhoneNumber],[RecipientGiftStatus] FROM [dbo].[Recipient] ''')
        resi = mycursor.fetchall()
        mycursor.execute('''  select [dbo].[Recipient].[RecipientId], [Name]  ,[Email] ,[PhoneNumber] ,[RecipientGiftStatus],[OrderNumber] from [dbo].[Recipient]  left join [dbo].[Order] on [dbo].[Recipient].RecipientId=[dbo].[Order].[RecipientId] where [RecipientGiftStatus]!='N' and [RecipientGiftStatus]!='C' and [RecipientGiftStatus]!='A' ''')
        ordered=mycursor.fetchall()
        mycursor.execute('''SELECT * FROM[dbo].[GiftCycle] ''')
        gfcycle = mycursor.fetchall()
    except:
            session.pop('loggedin', None)
            session.pop('mail', None)
            session.clear()
            flash('Unexpected error occurred in databse ')
            return render_template('newlogin.html')
    flash(' gift cycle updated ')
    return render_template('admin.html', mail=mail, resi=resi, gcycle=gfcycle, thambu=bus, temp=temp_admin, toos=totalorders, counts=counts, mys=mys,ordered=ordered)


if __name__ == "__main__":
    # serve(app, host="0.0.0.0", port=8080)
    app.run(debug=True, port=8150)
    # app.run(host="0.0.0.0")
