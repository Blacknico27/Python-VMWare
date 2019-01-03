#!/usr/bin/python
# coding: utf8

from pyVim.connect import SmartConnect
import ssl

vcenter_host = "your_vcenter_host"
vcenter_user = "your_user"
vcenter_password = 'your_password'

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

def list_sub_elements(folder,start_level):
        for element in folder:
                decalage = "------"
                level_number = 0
                while   level_number < start_level:
                        decalage = decalage+"------"
                        level_number = level_number +1
                decalage = decalage+"> "
                print(decalage+element.name)
                if find_element_type(element) == "Folder":
                        list_sub_elements(element.childEntity,start_level+1)
                elif find_element_type(element) == "VM":
                        print(decalage+element.network[0].name.encode('utf-8'))
                        try:
                                print(decalage+element.guest.guestFullName.encode('utf-8'))
                        except:
                                print(decalage+"\033[1;31;40m"+"La machine virtuelle n'a pas d'OS de référencé"+"\033[1;37;40m")
                        try:
                                print(decalage+element.config.annotation.encode('utf-8'))
                        except:
                                print(decalage+"\033[1;31;40m"+"La machine virtuelle n'a pas d'annotation"+"\033[1;37;40m")


s = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
s.verify_mode = ssl.CERT_NONE


try:
        connection = SmartConnect(host=vcenter_host, user=vcenter_user, pwd=vcenter_password)
        print('Valid certificate')
except:
        connection = SmartConnect(host=vcenter_host, user=vcenter_user, pwd=vcenter_password, sslContext=s)
        print('Invalid or untrusted certificate')

datacenter = connection.content.rootFolder.childEntity[0]
root_folder = datacenter.vmFolder.childEntity
print("Cluster ESX")
list_sub_elements(root_folder,0)
