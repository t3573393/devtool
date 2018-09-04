# check config example
Use the Execute System Groovy Script Plugin:
set the groovy file :  check_config.groovy  (notation: the file relative path)  

binding the check target value args, eg(it supports the xml(xpath), properties(name),ini(section and name)):

fileType0=xml
filePath0=applicationContext.xml
key0=/beans/bean[@name='transactionManager']/property[@name='entityManagerFactory']/@ref
value0=entityManagerFactory

fileType1=properties
filePath1=config.ini
key1=eclipse.p2.data.area
value1=@config.dir/../p2

fileType2=ini
filePath2=tox.ini
section2=tox
key2=envlist
value2=py26,py27,py34,py35,py36