# extract and analyze leaflets from www.prospektangebote.de
# the html pages are parsed in a non intelligent way
# the found images are downloaded and
# the images are analyzed via tesseract ocr
# TODO: implement search on textfiles
import subprocess
import os.path
import os

server="https://img.offers-cdn.net/assets/uploads/flyers/{}/large/combi-{}.jpg"
page="https://www.prospektangebote.de/anzeigen/angebote/{}-{}.html"
mainpage="https://www.prospektangebote.de/geschaefte/{}.html"

def openFlyer(file,tag):
    with open(file,"r") as f:
        cont=f.read()
    flyers=cont.split('<li class="item item-flyer">')
    for fl in flyers:
        if "openStoreFlyer('{}'".format(tag) in fl:
            number=fl.split("item-cover")[1].split('href="')[1].split('"')[0].split("-")[-1].split(".")[0]
            valid=fl.split("meta")[1].split("period")[1].split("</i>")[1].split("</p>")[0].strip()
            break
    return (number,valid)

def getPages(server, number, maxi, dir):
    if not os.path.exists(dir):
        for i in range(maxi+1):
            print(server.format(number,i))
            subprocess.run(["wget",server.format(number,i),"--directory-prefix="+dir])
    else:
        print("already downloaded")

def maxPages(filename,number,page,tmpname="prospektpage.html"):
    if not os.path.exists(tmpname):
        subprocess.run(["wget",page.format(filename,number),"-O", tmpname])

    with open(tmpname,"r") as f:
        cont=f.read()
    return int(cont.split('var amountPages = ')[1].split(";")[0].strip())

def download(name,tag):
    subprocess.run(["wget",mainpage.format(name),"-O",name+".html"])
    number,valid=openFlyer(name+".html",tag)
    valid_d=[x[0:-1].replace(".","_") for x in [valid.split(" ")[2],valid.split(" ")[5]]]
    dir=name+"-"+valid_d[1]
    maxpage=maxPages(name,number,page,dir+"p.html")
    # print(valid,maxpage,dir)
    getPages(server,number,maxpage,dir)
    print(valid,", pages:",maxpage,", saved in:", dir)
    return dir

def tesseract(dir):
    for entry in os.listdir(dir):
        name=entry.split("/")[-1].split(".")[0]
        if entry.endswith(".jpg") and not os.path.exists(os.path.join(dir,name+"txt")):
           subprocess.run(["tesseract",os.path.join(dir,entry),os.path.join(dir,name), "-l", "deu", "--psm", "3", "--oem", "1"])

def combi():
    name="combi-prospekte"
    tag="Combi Prospekt"
    dir = download(name,tag)
    tesseract(dir)

def main():
    combi()

main()
