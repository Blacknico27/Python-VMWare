#!/usr/bin/python
# coding: utf8

from pyVim.connect import SmartConnect #for using VMWare API
import ssl #for using SSL
import smtplib #to use smtp
from email.MIMEMultipart import MIMEMultipart #for complex mail
from email.MIMEText import MIMEText #for complex mail

vcenter_host = "your_vcenter"
vcenter_user = "your_user"
vcenter_password = 'your_password'

host_list=[] #array for listing misconfigured VMs
host_counter=0 #counter for misconfigured VMs

smtp_server = "smtp.mydomain.com"
emetteur = "sender@toto.com"
destinataire = "recipient@toto.com"

#************************************************************************************************************
#fonctions
def send_mail(fromaddr,toaddr,subject,body):

        try:
                msg = MIMEMultipart()
                msg['From'] = fromaddr
                msg['To'] = toaddr
                msg['Subject'] = subject

                msg.attach(MIMEText(body, 'plain', _charset='utf-8'))

                server = smtplib.SMTP(smtp_server, 25)
                #server.starttls()
                #server.login(username, password)
                text = msg.as_string()
                server.sendmail(fromaddr, toaddr, text)
                server.quit()

        except:

                print("Le message n'a pas pu être envoyé !")

def find_element_type(element):
        if str(element).find("vim.Folder") != -1:
                #print("Ceci est un dossier !")
                return "Folder"
        elif str(element).find("vim.VirtualMachine") != -1:
                #print("Ceci est une machine virtuelle !")
                return "VM"
        elif str(element).find("vim.VirtualApp") != -1:
                #print("Ceci est une App !")
                return "App"
        else:
                return "Unknow type or error"

def list_sub_elements(folder):
        global host_list
        global host_counter

        for element in folder:
                if find_element_type(element) == "Folder":

                        list_sub_elements(element.childEntity)

                elif find_element_type(element) == "VM":

                        #print(element.name)
                        #print(element.runtime.powerState)

                        if element.runtime.powerState == "poweredOff" and element.config.template == False:
                                #print("La machine virtuelle "+element.name+" est eteinte !")
                                host_counter = host_counter +1
                                host_list.append(element.name)

s = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
s.verify_mode = ssl.CERT_NONE


try:
        connection = SmartConnect(host=vcenter_host, user=vcenter_user, pwd=vcenter_password)
        #print('Valid certificate')
except:
        connection = SmartConnect(host=vcenter_host, user=vcenter_user, pwd=vcenter_password, sslContext=s)
        #print('Invalid or untrusted certificate')

datacenter = connection.content.rootFolder.childEntity[0]
root_folder = datacenter.vmFolder.childEntity
list_sub_elements(root_folder)

if len(host_list) != 0:

        #préparation du mail
        message = "Bonjour,\r\n\r\nCet email a pour but de vous informer de la liste des machines VMWare qui sont éteintes.\r\n\r\n"
        message = message+"Il y a "+str(host_counter)+" machines éteintes.\r\n\r\n"
        for host in host_list:

                message = message+host+"\r\n"

        message = message+"\r\nMerci de vérifier l'utilité de ces machines !"

        print(message)

        #envoi du message
        send_mail(emetteur,destinataire,"Machines VMWare éteintes",message)
