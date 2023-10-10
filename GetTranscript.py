import asyncio
from pyppeteer import launch
from chat_downloader import ChatDownloader

async def main():
    print("Launching driver")
    brwsr = await launch({"headless" : True, 'args' : ['--no-sandbox']})
    url = await brwsr.newPage()
    addr = input("Enter youtube url: ")
    if addr[0:8] != "https://":
        if addr[0:4] != "www.":
            addr = "https://www." + addr
        else:
            addr = "https://" + addr 
    print("Connecting to page")
    await url.goto(addr)
    print("Waiting for page to render")
    await url.waitForSelector("#button-shape > button > yt-touch-feedback-shape > div > div.yt-spec-touch-feedback-shape__fill")
    await url.click("#button-shape > button > yt-touch-feedback-shape > div > div.yt-spec-touch-feedback-shape__fill")
    items = await url.querySelectorAll("#items > ytd-menu-service-item-renderer")
    ln = len(items) + 1
    query = "#items > ytd-menu-service-item-renderer:nth-child(" + str(ln) + ")"
    await url.click(query)


    print("Waiting for transcript to render")
    
    await url.waitForSelector(".ytd-transcript-segment-list-renderer")
    transcript = await url.querySelectorAll(".ytd-transcript-segment-list-renderer .segment")
    print("Scraping transcript")
    subs = []
    for tr in transcript:
        #offset_start = await tr.JJeval('.segment-start-offset', '(nodes => nodes.map(n => n.innerText))')
        fragment = await tr.JJeval('.ytd-transcript-segment-renderer', '(nodes => nodes.map(n=> n.innerText))')
        subs.append((fragment[0], fragment[3]))
        print(f'{fragment[0]} : {fragment[3]}')
    isHTML = input("Output as HTML y/n: ")
    if isHTML == 'y':
        isHTML = True
    else:
        isHTML = False
         
    fname = input("Enter transcript filename: ")
    try:
        if not isHTML:
            fd = open(fname, 'w')
            outString = ""
            for sub in subs:
                outString += sub[0] + " : " + sub[1]  + '\n'
            fd.write(outString)
            fd.close()
        else:
            fd = open(fname + '.html', 'w')
            outString = "<html><head><title>" + fname + "</title></head><body style='background-color: black'>"
            parentDiv = "<div style='display:flex'>"
            tDiv = "<div style='overflow-x: scroll; width: 48vw'>"
            cDiv = "<div style='overflow-x: scroll; width: 48vw'>"
            for sub in subs:
                tm = sub[0].split(":")
                tm = list(map(lambda x: int(x), tm))
                if len(tm) == 3:
                    tm[0] *= 60 * 60
                    tm[1] *= 60
                    seconds = tm[0] + tm[1] + tm[2]
                elif len(tm) == 2:
                    tm[0] *= 60
                    seconds = tm[0] + tm[1]
                else:
                    seconds = tm[0]
                tStampURL = addr + "&t=" + str(seconds) + "s"
                opTag = "<a href='" + tStampURL + "' style='color : #07FE03; font-family: courier'>"
                clsTag = "</a>"
                line = opTag + sub[0] + " : " + sub[1] + clsTag + "<br>"
                tDiv += line
            tDiv += "</div>"
            dl = ChatDownloader()
            cht = dl.get_chat(addr)
            for ch in cht:
                tText = ch['time_text']
                times = tText.split(":")
                if times[0][0] == '-':
                    continue
                else:
                    if len(times) == 3:
                        seconds = times[0] * 60 * 60 + times[1] * 60 + times[2]
                    elif len(times) == 2:
                        seconds = times[0] * 60 + times[1]
                    else:
                        seconds = times[0]
                
                msg = ch['message']
                name = ch['author']['name']
                lnk = "<a href='" + addr + "&t=" + seconds + "s' style='color : #07FE03; font-family: courier'>"
                content = tText + " : " +  name + " : " + msg
                lnk = lnk + content + "</a><br>"
                cDiv += lnk
            cDiv += "</div>"
            parentDiv += tDiv + cDiv + "</div>"
            outString += parentDiv
            outString += "</body></html>"
            fd.write(outString)
            fd.close()
        print("Exiting successfully")
    except Exception as e:
        print(e)
        
    
   
    
asyncio.get_event_loop().run_until_complete(main())
