import smtplib
try:
    s = smtplib.SMTP('smtp.office365.com', 587, timeout=10)
    s.starttls()
    s.login('patricia.bravo.s@outlook.com', 'wloohkjvksfznexl')
    print("Login OK: credenciales correctas")
    s.quit()
except Exception as e:
    print("Error:", e)

    #KRETP-ACQ3G-C9SNM-Y4DLG-YSDJL
    #password->fijpgprlcayncekp
    #pas-real -> Colombia#2024