import logging
from rest_framework.decorators import api_view
from rest_framework.response import Response
import os
from gitview.views import getGitPath

log = logging.getLogger("gitDashboard")


def _recSearch(dir, search):
	contentDir = os.listdir(dir)
	res = []
	for cnt in contentDir:
		if os.path.isdir(dir + os.path.sep + cnt):
			if cnt.lower().find(search.lower()) > -1:
				if cnt.find('.git') > -1 or os.path.exists(dir + os.path.sep + cnt + os.path.sep + ".git"):
					# git repos
					res.append(dir + os.path.sep + cnt)
			res += _recSearch(dir + os.path.sep + cnt,search)
	return res

@api_view(['GET'])
def searchRepos(request):
	srcQuery = request.GET['search']
	basePath = getGitPath()
	autoCompleteJson = []
	for path in _recSearch(basePath, srcQuery):
		autoCompleteJson.append({'repo': path.replace(os.path.sep+os.path.sep,os.path.sep).replace(basePath, '')})
	return Response(autoCompleteJson)