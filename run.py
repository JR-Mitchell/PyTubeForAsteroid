import subprocess, json
from .fixed_pytube import YouTube
from html import unescape

def _charScore(character):
    if character in ('-','~'):
        return 2.0
    elif character is ':':
        return 1.5
    elif character is ';':
        return 1.3
    elif character is "'":
        return 0.5
    else:
        return 1.0

def _bracketScore(word):
    if word.strip().lower() in ["official","music","audio","video","lyric","cover","remaster","version"]:
        return 1.0
    elif word.strip().isnumeric():
        return 0.5
    else:
        return -1.0

def _quoteScore(word):
    if word.strip().lower() in ["official","music","audio","video","lyric","cover","remaster","version","full","song","by"]:
        return 1.0
    elif word.strip().isnumeric():
        return 0.5
    else:
        return -1.0

def getSongName(title,details):
    """ Methodology:
            Typically, songs are either uploaded to youtube like 'Artist - SongName' or 'SongName - Artist' or 'SongName', where ' - ' may be any chosen separation string,
            but typically contains at least one non-alphanumerical character. Or I guess it could be 'by'.
            The third circumstance, 'SongName' most frequently occurs when the video is by an official artist channel; then, the artists name is typically the channel name.
            Also, most often in the third circumstance, the title may be 'SongName (Official Music Video)' or the like, and channel may be 'Artist - Topic'.
            Songs may sometimes also be uploaded with quotes, as in '"SongName" full song' or '"SongName" by Artist'.
            This code works on the theory that one of the above three cases is the case, and tries to guess which is most likely. """
    title = unescape(title)
    authorString = details["author"]
    #First, test for brackets in the title
    moddedTitle = ''.join([ "(" if character in "()[]{}" else character for character in title])
    if "(" in moddedTitle:
        #Might have (Official Music Video)
        moddedTitleBroken = [item.split(" ") for item in moddedTitle.split("(")[1:] if len([word for word in item.split(" ") if len(word) > 0]) > 0]
        moddedTitleBrokenScore = [sum([_bracketScore(word) for word in item if len(word) > 0]) for item in moddedTitleBroken]
        for i,score in enumerate(moddedTitleBrokenScore):
            if score >= 0:
                innerString = " ".join(moddedTitleBroken[i])
                frontIndex = title.index(innerString)
                backIndex = frontIndex + len(innerString)
                title = (title[:frontIndex-1] + title[backIndex+1:]).replace("  "," ")
    elif '"' in title:
        #print(title)
        #Might have "SongName"
        titleBroken = [item.split(" ") for item in title.split('"')[1:] if len([word for word in item.split('"') if len(word)>0])>0]
        titleBrokenScore = [sum([_quoteScore(word) for word in item if len(word) > 0]) for item in titleBroken]
        for i,score in enumerate(titleBrokenScore):
            #print(i,score)
            if score >= 0:
                isByStr = False
                innerString = " ".join(titleBroken[i])
                if "by" in innerString.lower(): #might be "SongName" by Artist
                    brokenInnerString = innerString.split(" ")
                    if brokenInnerString[0].strip().lower() == "by":
                        isByStr = True
                frontIndex = title.index(innerString)
                if isByStr:
                    newBackIndex = title[frontIndex:].lower().index("by")
                    return (title[:frontIndex-1].strip().strip('"').strip(),title[frontIndex+newBackIndex+2:].strip().strip('"').strip())
                backIndex = frontIndex + len(innerString)
                #print(frontIndex,backIndex)
                title = (title[:frontIndex-1] + title[backIndex+1:]).replace("  "," ").strip().strip('"').strip()
    #See if splitting the words is valid
    titleWords = [item for item in unescape(title).split(" ") if len(item) is not 0]
    titleNonAlphaNumericScore = [sum([-abs((len(word)/2.0)-i)/len(word) if character.isalnum() else _charScore(character)*abs((len(word)/2.0)-i)/len(word) for i,character in enumerate(word)]) for word in titleWords]
    splitScore = max(titleNonAlphaNumericScore)
    #print(titleWords)
    #print(titleNonAlphaNumericScore)
    mostLikelySplitIndex = titleNonAlphaNumericScore.index(splitScore)
    splitWord = titleWords[mostLikelySplitIndex]
    splitSubscores = [-abs((len(splitWord)/2.0)-i)/len(splitWord) if character.isalnum() else _charScore(character)*abs((len(splitWord)/2.0)-1)/len(splitWord) for i,character in enumerate(splitWord)]
    splitSubscore = max(splitSubscores)
    mostLikelySubsplitIndex = splitSubscores.index(splitSubscore)
    firstPart = splitWord[:mostLikelySubsplitIndex]
    while len(firstPart) > 0 and not firstPart[-1].isalnum():
        firstPart = firstPart[:-1]
    lastPart = splitWord[mostLikelySubsplitIndex:]
    while len(lastPart) > 0 and not lastPart[0].isalnum():
        lastPart = lastPart[1:]
    firstSplitString = " ".join(titleWords[:mostLikelySplitIndex] + [firstPart]).strip()
    secondSplitString = " ".join([lastPart] + titleWords[mostLikelySplitIndex+1:]).strip()
    if (splitScore > 0):
        #print("Presuming 'x - y'. Deciding order.")
        return (firstSplitString,secondSplitString)
    else:
        #print("Presuming 'songname' unless evidence against")
        isSongname = True
        #check against info in description and keywords
        if "shortDescription" in details:
            if firstSplitString.lower() in details["shortDescription"].lower() and secondSplitString.lower() not in details["shortDescription"].lower():
                isSongname = False
            elif secondSplitString.lower() in details["shortDescription"].lower() and firstSplitString.lower() not in details["shortDescription"].lower():
                isSongname = False
            elif firstSplitString.lower() in details["shortDescription"].lower() and details["shortDescription"].lower().index(secondSplitString.lower()) < details["shortDescription"].lower().index(firstSplitString.lower()):
                isSongname = False
        if "keywords" in details:
            kwords = [kword.lower() for kword in details["keywords"]]
            if firstSplitString.lower() in kwords and secondSplitString.lower() not in kwords:
                isSongname = False
            elif secondSplitString.lower() in kwords and firstSplitString.lower() not in kwords:
                isSongname = False
            elif firstSplitString.lower() in kwords and kwords.index(secondSplitString.lower()) < kwords.index(firstSplitString.lower()):
                isSongname = False
        if firstSplitString == '':
            isSongname = True
        if secondSplitString == '':
            isSongname = True
        if splitSubscore < 0:
            isSongname = True
        if isSongname:
            #might have - Topic
            if "-" in authorString:
                authorString = "-".join([item for item in authorString.split("-") if item.strip().lower() != "topic"])
            return(authorString.strip(),title.strip())
        else:
            #print("changed my mind. Deciding order.")
            return(firstSplitString,secondSplitString)


def get_song(youtubeUrl, destination):
    """ Downloads the video at youtubeUrl, saves it as a wav file at given destination, and then returns song info """
    track = YouTube(youtubeUrl)
    videoDetails = track.player_config_args["player_response"]["videoDetails"]
    sf = track.streams.filter(progressive=True,subtype="mp4")
    stream = sf.all()[0]
    songData = {"duration":videoDetails["lengthSeconds"]}
    #Work out the file name
    songData["file_path"] = destination+stream.default_filename.replace(".mp4",".mp3")
    #Check the file doesn't already exist
    fileAlreadyExists = True
    try:
        subprocess.run('ls "{}"'.format(songData["file_path"]),shell=True,check=True)
    except:
        fileAlreadyExists = False
    if fileAlreadyExists:
        print("Song already exists at {}".format(songData["file_path"]))
        return None
    else:
        #Try to guess the song name and artist
        songData["name"],songData["artist"] = getSongName(track.title,videoDetails)
        #Download
        stream.download()
        #Convert to .wav
        subprocess.call('ffmpeg -i "{}" "{}"'.format(stream.default_filename),songData["file_path"],shell=True)
        #Remove vid
        subprocess.call('rm "{}"'.format(stream.default_filename),shell=True)
        return songData

