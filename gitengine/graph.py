import hashlib
from datetime import datetime

from django.utils.encoding import smart_str, DjangoUnicodeDecodeError


def getGravatarUrl(email, size):
	md5Digester = hashlib.md5()
	md5Digester.update(email.encode("utf-8"))
	md5Email = md5Digester.hexdigest()
	return "http://www.gravatar.com/avatar/" + md5Email + "?d=mm&s=" + str(size)


def canvasTooltipRect(x, y, width, height, color):
	rectJS = 'var rect = new Kinetic.Rect({'
	rectJS += 'x:' + str(x) + ','
	rectJS += 'y:' + str(y) + ','
	rectJS += 'width:' + str(width) + ','
	rectJS += 'height:' + str(height) + ','
	rectJS += 'fill:"' + color + '",'
	rectJS += 'stroke: "black",'
	rectJS += 'strokeWidth: 2,'
	rectJS += 'lineJoin: "round"'
	rectJS += '});\n'
	rectJS += 'tooltipLayer.add(rect);'
	return rectJS


def canvasDateRect(x, y, width, color):
	rectJS = 'var dateRect = new Kinetic.Rect({'
	rectJS += 'x:' + str(x) + ','
	rectJS += 'y:' + str(y) + ','
	rectJS += 'width:' + str(width) + ','
	rectJS += 'height:20,'
	rectJS += 'fill:"' + color + '",'
	rectJS += 'alpha: 0.75,'
	rectJS += 'stroke: "white",'
	rectJS += 'strokeWidth: 1'

	rectJS += '});\n'
	rectJS += 'textGroup.add(dateRect);'
	return rectJS


def canvasTooltip(x, y, message, size=10):
	tooltipJS = 'var tooltip = new Kinetic.Text({'
	tooltipJS += 'text: "' + message + '",'
	tooltipJS += "x:" + str(x) + ','
	tooltipJS += "y:" + str(y) + ','
	tooltipJS += 'fontFamily: "Verdana",'
	tooltipJS += 'fontSize: ' + str(size) + ','
	tooltipJS += 'padding: 5,'
	tooltipJS += 'textFill: "black"'
	tooltipJS += '})\n;'
	tooltipJS += 'tooltipLayer.add(tooltip);'
	return tooltipJS


def canvasGravatarImage(x, y, author):
	img = ' var img = new Image();'
	img += 'var gravImg = new Kinetic.Image({'
	img += 'image:img,'
	img += "x:" + str(x) + ','
	img += "y:" + str(y) + ','
	img += 'width:32,height:32 '
	img += '});'
	img += 'tooltipLayer.add(gravImg);'
	img += 'img.src="' + getGravatarUrl(author.email, 32) + '";'
	img += canvasTooltip(x + "+30", y + "+8", author.name, 10)
	return img


def canvasCircle(x, y, radius, color, tooltip, cmt, gitGraph):
	jsvar = 'circle_' + cmt.commit.hexsha
	circleJS = "var " + jsvar + " = new Kinetic.Circle({"
	circleJS += "x:" + str(x) + ','
	circleJS += "y:" + str(y) + ','
	circleJS += "radius:" + str(radius) + ','
	circleJS += 'fill:"' + color + '",'
	circleJS += 'stroke: "black",'
	circleJS += 'strokeWidth: 1'
	circleJS += '});\n'

	circleJS += jsvar + '.on("mouseover", function(){\n'
	circleJS += 'var mousePos = stage.getMousePosition();\n'
	circleJS += 'tooltipLayer.removeChildren();\n'
	circleJS += 'document.body.style.cursor = "pointer";\n'
	tooltipY = 37
	maxLen = 0
	tooltips = ""
	numLines = 0
	tooltips += canvasGravatarImage('mousePos.x+25', 'mousePos.y+25', cmt.commit.author)
	for msg in tooltip:
		if numLines < 14:
			if numLines == 13:
				message = "[continua...]"
			else:
				if len(msg) > maxLen:
					maxLen = len(msg)
				try:
					message = smart_str(msg)
				except TypeError:
					pass
				except DjangoUnicodeDecodeError:
					message = msg.decode('latin1')
				message = msg.replace('"', '')
			tooltips += canvasTooltip('mousePos.x+20', 'mousePos.y+' + str(tooltipY + 20), message)
			tooltipY += 20
			numLines += 1

	if (tooltipY - 20) > gitGraph._maxTooltipHeight:
		gitGraph._maxTooltipHeight = tooltipY - 20 + gitGraph.branchNamesWidth

	if maxLen * 8 > gitGraph._maxTooltipWidth:
		gitGraph._maxTooltipWidth = maxLen * 8
	circleJS += canvasTooltipRect('mousePos.x+20', 'mousePos.y+20', maxLen * 8, str(tooltipY), "#FFFFFF")
	circleJS += tooltips
	circleJS += 'tooltipLayer.show();\n'
	circleJS += 'tooltipLayer.draw();\n'
	circleJS += '});\n'

	#mouseOut
	circleJS += jsvar + '.on("mouseout", function(){\n'
	circleJS += 'tooltipLayer.removeChildren();\n'
	circleJS += '//tooltipLayer.hide();\n'
	circleJS += 'tooltipLayer.draw();\n'
	circleJS += 'document.body.style.cursor = "default";\n'
	circleJS += '});\n'

	#click
	circleJS += jsvar + '.on("mousedown", function(){\n'
	if gitGraph.commitUrl:
		cmtUrl = gitGraph.commitUrl.replace("$$", cmt.commit.hexsha)
	else:
		cmtUrl = ""
	circleJS += 'window.location = "' + cmtUrl + '";'
	circleJS += '});\n'

	circleJS += 'circleGroup.add(' + jsvar + ');\n'
	return circleJS


def canvasText(x, y, text, color, gitGraph, group, fontSize=None):
	textJS = 'var text= new Kinetic.Text({'
	textJS += 'x:' + str(x) + ','
	textJS += 'y:' + str(y) + ','
	textJS += 'fontFamily: "Verdana",'
	if fontSize:
		textJS += 'fontSize:' + str(fontSize) + ','
	else:
		textJS += 'fontSize:' + str(gitGraph._fontSize) + ','
	textJS += 'text:"' + text + '",'
	textJS += 'textFill:"' + color + '"'
	textJS += '});\n'
	textJS += group + '.add(text);\n'
	return textJS


class CommitGraph:
	def __init__(self, cmt, x, y, color, gitGraph, branchName):
		self.x = x
		self.y = y
		self.cmt = cmt
		self.color = color
		self.gitGraph = gitGraph
		self.branchName = branchName

	def draw(self):
		radius = 6
		tooltip = []
		dt = datetime.fromtimestamp(self.cmt.commit.committed_date)
		tooltip.append("ID: " + self.cmt.commit.hexsha)
		tooltip.append("Date: " + dt.strftime('%Y-%m-%d %H:%M:%S'))
		message = self.cmt.commit.message
		rows = smart_str(message).split('\n')
		for row in rows:
			if len(row) > 0:
				tooltip.append(row)
		return canvasCircle(self.x, self.y, radius, self.color, tooltip, self.cmt, self.gitGraph)

	def drawLabels(self):
		labelStr = ''
		labels = self.cmt.getTags()
		labels.extend(self.cmt.getBranches())
		for lb in labels:
			labelStr += lb + ' '
		if labelStr != '':
			return 'label(' + str(self.x) + ',' + str(
				self.y + 5) + ',"' + labelStr + '",labelGroup,"#404040","black");\n'
		else:
			return ''


class GitGraphCanvas:
	def __init__(self, repo, since=None, until=None, commitUrl=None):
		self.repo = repo
		self.commitUrl = commitUrl
		self._width = 0
		self._height = 0
		self._fontSize = 10
		self._maxTooltipWidth = 0
		self._maxTooltipHeight = 0
		self.since = since
		self.until = until
		self.radius = 10
		self.xDelay = ((self.radius * 2) + 10)

	def render(self):
		#the return string
		canvas = ""
		#Dict key:cmtID value: (x,y)
		commitsPos = {}
		#Commit already added
		cmtAdded = []
		#Dict key:cmtID value:instance of GraphCommit
		graphCommits = {}
		#Dict key:sonId value=[parentID,...]
		parents = {}
		#Dict key:parentId value=[sonID,...]
		sons = {}
		#Max lenght(calculated based numchar*8) of name of branch
		maxBranchNameLength = 0
		#Dict Key:cmtID value:instance of GitCommit
		cmts = {}
		#all dates
		dates = []
		#Date associated to x coordinate
		datesX = {}
		#List of years
		years = []
		#Dict key:year value=(xMin,xMax)
		yearX = {}
		#List of months
		months = []
		#Dict key:month value=(xMin,xMax)
		monthX = {}
		#List of months
		days = []
		#Dict key:day value=(xMin,xMax)
		daysX = {}
		#Dict key:date value:[cmtID,...]
		branchesCmtsDates = {}

		#fetch branches
		allBranches = self.repo.getBranches()
		branches = {}

		for ab in allBranches.keys():
			if allBranches[ab] not in branches:
				branches[allBranches[ab]] = ab
			else:
				branches[allBranches[ab]] += " " + ab
		sortedBranches = [self.repo.head.commit.hexsha]
		tmp = []
		tmp.extend(branches.keys())
		tmp.remove(self.repo.head.commit.hexsha)
		sortedBranches.extend(tmp)

		#associate commits to its date
		for branchSha in sortedBranches:

			if len(branches[branchSha]) > maxBranchNameLength:
				maxBranchNameLength = len(branches[branchSha])
			parents[branchSha] = []
			branchCmts = self.repo.getCommits(branch=branchSha, since=self.since, until=self.until)
			branchDates = {}
			for cmt in branchCmts:
				cmts[cmt.commit.hexsha] = cmt
				dt = cmt.commit.committed_date
				dates.append(dt)
				cmtID = cmt.commit.hexsha + "_" + branchSha
				if len(cmt.commit.parents) > 0:
					firstPrt = cmt.commit.parents[0].hexsha
					firstprtID = firstPrt + "_" + branchSha
					parents[branchSha].append(firstprtID)
					for prt in cmt.commit.parents:
						if prt.hexsha in sons:
							sons[prt.hexsha].append(cmtID)
						else:
							sons[prt.hexsha] = [cmtID]
				if dt in branchDates:
					branchDates[dt].append(cmtID)
				else:
					branchDates[dt] = [cmtID]
			branchesCmtsDates[branchSha] = branchDates
		dates = sorted(set(dates))

		self.branchNamesWidth = maxBranchNameLength * self._fontSize

		x = 0
		#find the first x coordinate for each date
		currMonth = ""
		currDay = ""
		currYear = ""
		lastDt = dates[len(dates) - 1]
		for dt in dates:
			xMax = 1
			#YEARS
			year = datetime.fromtimestamp(dt).strftime('%Y')
			if currYear != year:
				#the first year
				if currYear != "":
					yearX[currYear] = (yearX[currYear][0], x)
				years.append(year)
				if dt == lastDt:
					yearX[year] = (x, self.xDelay * xMax)
				else:
					yearX[year] = (x, x)
				currYear = year
			else:
				if dt == lastDt:
					yearX[currYear] = (yearX[currYear][0], x + self.xDelay * xMax)
				#MONTHS
			month = datetime.fromtimestamp(dt).strftime('%Y-%m')
			if currMonth != month:
				#the first month
				if currMonth != "":
					monthX[currMonth] = (monthX[currMonth][0], x)
				months.append(month)
				if dt == lastDt:
					monthX[month] = (x, self.xDelay * xMax)
				else:
					monthX[month] = (x, x)
				currMonth = month
			else:
				if dt == lastDt:
					monthX[currMonth] = (monthX[currMonth][0], x + self.xDelay * xMax)
				#DAYS
			day = datetime.fromtimestamp(dt).strftime('%Y-%m-%d')
			if currDay != day:
				#the first day
				if currDay != "":
					daysX[currDay] = (daysX[currDay][0], x)
				days.append(day)
				if dt == lastDt:
					daysX[day] = (x, x + self.xDelay * xMax)
				else:
					daysX[day] = (x, x)
				currDay = day
			else:
				if dt == lastDt:
					daysX[currDay] = (daysX[currDay][0], x + self.xDelay * xMax)
				#find maximum number of commit for each date
			for branchSha in sortedBranches:
				try:
					if len(branchesCmtsDates[branchSha][dt]) > xMax:
						xMax = len(branchesCmtsDates[branchSha][dt])
				except KeyError:
					pass
			datesX[dt] = x
			x += self.xDelay * xMax
			#creation of commits graphs structures
		for branchSha in sortedBranches:
			graphCommits[branchSha] = []
			if branchSha == self.repo.head.commit.hexsha:
				color = "red"
			else:
				color = "#8ED6FF"
				#draw commits
			for dt in dates:
				cmtNum = 0
				try:
					for cmt in branchesCmtsDates[branchSha][dt]:
						cmtX = datesX[dt] + (self.xDelay * cmtNum)
						#set global width
						if cmtX > self._width:
							self._width = cmtX
						cmtID = cmt.split('_')[0]
						if cmtID not in cmtAdded:
							#do not set y because it will be recalculate later
							graphCmt = CommitGraph(cmts[cmtID], cmtX, 0, color, self, branches[branchSha])
							graphCommits[branchSha].append(graphCmt)
							#add circle positions on commitsPos dictionary
							commitsPos[cmt] = graphCmt
							cmtAdded.append(cmtID)
							cmtNum += 1
				except KeyError:
					pass
			#DRAW!
		#draw date row
		years = sorted(years)
		for y in years:
			canvas += canvasDateRect(yearX[y][0] - self.radius - 5, 7, yearX[y][1] - yearX[y][0], "black")
			yX = yearX[y][0] + ((yearX[y][1] - yearX[y][0]) / 2) - self.radius - 10
			canvas += canvasText(yX, 12, y, 'white', self, 'textGroup', fontSize=8)

		months = sorted(months)
		for mn in months:
			canvas += canvasDateRect(monthX[mn][0] - self.radius - 5, 27, monthX[mn][1] - monthX[mn][0], "#202020")
			mnX = monthX[mn][0] + ((monthX[mn][1] - monthX[mn][0]) / 2) - self.radius - 10
			canvas += canvasText(mnX, 32, mn.split('-')[1], 'white', self, 'textGroup', fontSize=8)
		days = sorted(days)
		for d in days:
			canvas += canvasDateRect(daysX[d][0] - self.radius - 5, 47, daysX[d][1] - daysX[d][0], "#404040")
			dX = daysX[d][0] + ((daysX[d][1] - daysX[d][0]) / 2) - self.radius - 10
			canvas += canvasText(dX, 52, d.split('-')[2], 'white', self, 'textGroup', fontSize=8)
			#y delay
		y = 80
		branchToDrop = [] #list of branch to drop because is empty
		branchNameCanvas = ""
		canvasCircles = ""
		for branchSha in sortedBranches:
			if len(graphCommits[branchSha]) > 0:
				if branchSha == self.repo.head.commit.hexsha:
					branchNameCanvas += canvasText(10, y - 5, branches[branchSha], "red", self, 'branchNames', 8)
					color = "red"
				else:
					branchNameCanvas += canvasText(10, y - 5, branches[branchSha], "black", self, 'branchNames', 8)
					color = "#8ED6FF"
					#draw circle
				for grpCmt in graphCommits[branchSha]:
					grpCmt.y = y
					canvasCircles += grpCmt.draw()
					canvasCircles += grpCmt.drawLabels()
				y += self.radius + 20
			else:
				branchToDrop.append(branchSha)
		for delSha in branchToDrop:
			sortedBranches.remove(delSha)

		#set the global height
		self._height = y
		#Lines
		lines = {}
		for par in sons.keys():
			for branchSha in sortedBranches:
				parID = par + "_" + branchSha
				if parID in commitsPos:
					xPar = commitsPos[parID].x
					yPar = commitsPos[parID].y
					for son in sons[par]:
						if son in commitsPos:
							x = commitsPos[son].x
							y = commitsPos[son].y
							if yPar == y:
								#horizontal
								if y not in lines.keys():
									lines[y] = (min(xPar, x), max(xPar, x))
								else:
									lines[y] = (min(lines[y][0], xPar), max(lines[y][1], x))
							else:
								canvas += 'line(' + str(xPar) + ',' + str(yPar) + ',' + str(x) + ',' + str(
									y) + ',"#000000",lineGroup);\n'
		for lnY in lines:
			canvas += 'line(' + str(lines[lnY][0]) + ',' + str(lnY) + ',' + str(lines[lnY][1]) + ',' + str(
				lnY) + ',"#000000",lineGroup);\n'
		canvas += canvasCircles
		return branchNameCanvas, canvas

	def getWidth(self):
		return self._width

	def getHeight(self):
		return self._height + self._maxTooltipHeight
