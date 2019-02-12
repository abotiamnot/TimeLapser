import smtplib
import config
import dynamic as dyn
import MotionMod
motionstate=False 
Confirmation=False
from time import sleep
subject_Alert="ALERT! Intruder Detected"
message_Alert="ALERT! Somebody just tresspassed in your premisis"
subject_Conf="Email Configuration successful "
message_Conf="Hi. Your camera has been configured in Security Camera Mode. You will receive intrution alerts on this Email Address"
def send_email(subject,msg):
	try:
		server=smtplib.SMTP('smtp.gmail.com:587')
		server.ehlo()
		server.starttls()
		server.login(config.EMAIL_ADDRESS, config.PASSWORD)
		message='subject:{}\n\n{}'.format(subject, msg)
		email_list = dyn.email_extractor()
		for mail_ in email_list:
				print(mail_)
				server.sendmail(config.EMAIL_ADDRESS,mail_, message)
		server.quit()
		print("success: email sent")
	except:
		print("failed to send")

sleep(10)
while True:
	motionState=MotionMod.motion()
	if Confirmation==False:
		send_email(subject_Conf,message_Conf)
		Confirmation=True
		
		
#	if motionState==True:
#		send_email(subject_Alert,message_Alert)
#		sleep(2)

