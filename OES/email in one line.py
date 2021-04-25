import smtplib 
gmailaddress = '19DCE032@charusat.edu.in'
gmailpassword = 'namang942'
mailto = input("what email address do you want to send your message to? \n ")
msg = input("What is your message? \n ")
mailServer = smtplib.SMTP('smtp.gmail.com' , 587)
mailServer.starttls()
mailServer.login(gmailaddress , gmailpassword)
mailServer.sendmail(gmailaddress, mailto , msg)

print(" \n Sent!")
mailServer.quit()
