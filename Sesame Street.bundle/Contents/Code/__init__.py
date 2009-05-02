import re, urllib
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

WEB_ROOT = 'http://www.sesamestreet.org'
SEARCH_PAGE = 'http://www.sesamestreet.org/browseallvideos?p_p_lifecycle=0&p_p_id=BrowseAndPlayContents_WAR_sesameportlets4369&p_p_action=localSearch'

CACHE_INTERVAL = 3600 * 6

####################################################################################################
def Start():
  Plugin.AddPrefixHandler("/video/sesameStreet", MainMenu, 'Sesame Street', 'icon-default.jpg', 'art-default.jpg')
  MediaContainer.title1 = 'Sesame Street'
  MediaContainer.content = 'Items'
  MediaContainer.art = R('art-default.jpg')
  HTTP.SetCacheTime(CACHE_INTERVAL)

####################################################################################################
def MainMenu():
  dir = MediaContainer()
  dir.Append(Function(DirectoryItem(Browse, title="By Subject"), url=WEB_ROOT+'/browsevideosbysubject', title='By Subject'))
  dir.Append(Function(DirectoryItem(Browse, title="By Theme"), url=WEB_ROOT+'/browsevideosbytheme', title='By Theme'))
  dir.Append(Function(DirectoryItem(Browse, title="By Character"), url=WEB_ROOT+'/browsevideosbycharacter', title='By Character'))
  dir.Append(Function(SearchDirectoryItem(Search, title=L("Search..."), prompt=L("Search for Videos"), thumb=R('search.png'))))
  return dir
  

####################################################################################################
def Browse(sender, url, title = None, replaceParent=False, values=None):
    Log(sender)
    page = XML.ElementFromURL(url, cacheTime=1200, isHTML=True, values=values)
    dir = MediaContainer(title1="Sesame Street", title2=title, replaceParent=replaceParent)
    for tag in page.xpath("//div[@id='browse']/div/div/table/tr/td | //div[@id='browse']/div/div/div/table/tr/td"):
        """
            The HTML incorrectly uses a self-closed anchor tag around the show name. The browser corrects this
            but etree does not.
        """
        if tag.xpath(".//div[@class='browse-desc']/div//a")[0].get('onclick'):
            dir.Append(CreateCategory(tag))
        else:
            dir.Append(CreateVideo(tag))
            
    AddPager(page, dir, title)  
    
    return dir
    
####################################################################################################
def CreateVideo(tag):
    url = tag.xpath(".//div[@class='browse-desc']/div//a")[0].get('href')
    return WebVideoItem(WEB_ROOT+url, GetTitle(tag), thumb=GetThumb(tag))

####################################################################################################
def CreateCategory(tag):
    url =  tag.xpath(".//div[@class='browse-desc']/div//a")[0].get('onclick')
    urlParts = re.match("doSearch\('([^']*)','([^']*)", url)
    url = urlParts.group(1) + urllib.quote_plus(urlParts.group(2))
    title = GetTitle(tag)
    return Function(DirectoryItem(Browse, title=title, thumb=GetThumb(tag)), url=WEB_ROOT+'/'+url, title=title)

####################################################################################################
def GetTitle(tag):
    title = tag.xpath(".//div[@class='browse-desc']/div//a")[0].text
    if not title:
        title = tag.xpath(".//div[@class='browse-desc']/div//a")[0].tail
    title = title.strip()
    return title

####################################################################################################    
def GetThumb(tag):
    return WEB_ROOT+tag.xpath(".//div[@class='thumb-image']/a/img")[0].get('src')
    
####################################################################################################    
def AddPager(page, dir, pageTitle):
    next = page.xpath("//span[@class='nav-pagination']/a[@class='current']/following-sibling::a")
    if next:
        next = next[0]
        title = "Page "+next.text.strip()
        url = next.get('href')
        dir.Append(Function(DirectoryItem(Browse, title=title), url=url, title=pageTitle, replaceParent=True))
    prev = page.xpath("//span[@class='nav-pagination']/a[@class='current']/preceding-sibling::a")
    if prev:
        prev = prev[0]
        title = "Page "+prev.text.strip()
        url = prev.get('href')
        dir.Append(Function(DirectoryItem(Browse, title=title), url=url, title=pageTitle, replaceParent=True))
    
        
####################################################################################################
def Search(sender, query):
    return Browse(sender, SEARCH_PAGE, title="Search Results", values={"p_p_sesameStreetKeyword":query})

    