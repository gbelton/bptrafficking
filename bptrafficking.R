# load required libraries
library("RSQLite")
library(stringr)
library(plyr)
library(dplyr)


# Open SQL Database
con = dbConnect(SQLite(), dbname="bpscrape.sqlite")
# get a list of all tables
alltables = dbListTables(con)
# get the Escorts table as a data.frame
escorts = dbGetQuery( con,'select * from Escorts' )
# get the Posts table as a data.frame
posts = dbGetQuery( con,'select * from Posts' )

#close connection to database
dbDisconnect(con)

#Clean data

# convert datetime from string to POSIX datetime
posts[[3]] <- as.POSIXlt(posts[,3], tx='', format = '%Y-%m-%d %H:%M:%S')

#convert age to numeric
escorts$age <- as.numeric(escorts$age)

# search body for phone number; start with the easy ones
escorts$phone <- gsub("[^[:alnum:]]", "", escorts$body)
escorts$phone <- as.character(str_extract(escorts$phone, "[2-9][0-9]{9}"))

# this function checks to see if phone is NA, then tries to clear up 
# obscured phone numbers
cleanphone1 <- function(x, y) {
     if (is.na(x)) {
          x <- y
          x <- gsub('one', '1', x, perl=TRUE, ignore.case=TRUE)
          x <- gsub('two', '2', x, perl=TRUE, ignore.case=TRUE)
          x <- gsub('three', '3', x, perl=TRUE, ignore.case=TRUE)
          x <- gsub('four', '4', x, perl=TRUE, ignore.case=TRUE)
          x <- gsub('five', '5', x, perl=TRUE, ignore.case=TRUE)
          x <- gsub('six', '6', x, perl=TRUE, ignore.case=TRUE)
          x <- gsub('seven', '7', x, perl=TRUE, ignore.case=TRUE)
          x <- gsub('eight', '8', x, perl=TRUE, ignore.case=TRUE)
          x <- gsub('nine', '9', x, perl=TRUE, ignore.case=TRUE)
          x <- gsub('zero', '0', x, perl=TRUE, ignore.case=TRUE)
          x <- gsub('ten', '10', x, perl=TRUE, ignore.case=TRUE)
          x <- gsub('l', '1', x, perl=TRUE, ignore.case=TRUE)
          x <- gsub('o', '0', x, perl=TRUE, ignore.case=TRUE)
          x <- gsub("[^[:alnum:]]", "", x)
          x <- as.character(str_extract(x, "[2-9][0-9]{9}"))
     } else x <- x
}

escorts<-adply(escorts, 1, transform, phone=cleanphone1(phone, body))

#some ads have phone number in title instead of body
cleanphone2 <- function(x,y) {
     if (is.na(x)) {
          x <- y
          x <- gsub("[^[:alnum:]]", "", x)
          x <- as.character(str_extract(x, "[2-9][0-9]{9}"))
          
     } else x <- x
     
}
escorts<-adply(escorts, 1, transform, phone=cleanphone2(phone, title))

#add location to posts and ads
posts$location <- substr(posts$backpageurl, 8, regexpr('\\.', posts$backpageurl)-1)
# substring of backpageurl starting at the position after http:// and stopping at the
# last character before the first period.

escorts$location <- substr(escorts$AdUrl, 8, regexpr('\\.', escorts$AdUrl)-1)


# combine tables

temp <- join(posts, escorts, by = 'id', type = 'left')

#list of fields to keep
keeps <- c('id', 'datetime', 'location', 'phone')
temp <- temp[, keeps, drop = FALSE]
temp$date = as.Date(temp$datetime)

#########################################
## Following section is incomplete!
#########################################

### Loop through dates in database
days <- sort(unique(temp$date))
#starting with second date
days <- days[2:length(days)]
for(day in days) {
     
     #calculate number of unique phone numbers in each city for that date
     daytemp <- temp[ which(temp$date==day),]
     keeps <- c('id', 'location', 'phone', 'date')
     daytemp <- daytemp[, keeps, drop = FALSE]
     phonetemp <- daytemp %>% distinct(phone)
     #build a new table with a count of the phone numbers per location
     citycounts <- phonetemp %>% group_by(location) %>% summarise(rows = length(location))
     # add lat and lon to citycounts
     geog <- read.csv('geog.csv', stringsAsFactors = FALSE)
     citycounts <- join(citycounts, geog, by = 'location', type = 'left')
     
     #plot cities on map with circles proportional to number of phone numbers

     #get list of unique phone numbers
     phones <- daytemp$phone
     
     #for each phone number:
     for(phone in phones) {
          # if phone number appears in more than one city, ignore it
          n <- nrow(unique(daytemp[ which(daytemp$phone==phone), 2:4 ]))
          if (n==1) {
               # Otherwise, attempt to determine if the phone number was posted in a 
               #    different city in previous day (week?)
               
               #Create table with current city and previous city for each phone number
          } #end if statement
     } #end phones loop
          #plot lines connecting previous city to current city on same map 
     #save high-resolution image of map
} #end days loop

##########
#OUTSIDE of R:
#
#use video editing software to convert series of images into animated video
#
##########
