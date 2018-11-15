import json
import requests
import sys

token = sys.argv[1]
org=sys.argv[2]
repo=sys.argv[3]
prId=sys.argv[4]


customHeader={'Authorization': 'token {0}'.format(token)}


customPostHeader={'Authorization': 'token {0}'.format(token),'Accept':'application/vnd.github.symmetra-preview+json'}


issueUrl='https://api.github.com/repos/{0}/{1}/issues/{2}/labels'.format(org,repo,prId)
url='https://api.github.com/repos/{0}/{1}/pulls/{2}'.format(org,repo,prId)
commentUrl='https://api.github.com/repos/{0}/{1}/issues/{2}/comments'.format(org,repo,prId)
reviewRequestUrl='https://api.github.com/repos/{0}/{1}/pulls/{2}/requested_reviewers'.format(org,repo,prId)
releaseUrl='https://api.github.com/repos/{0}/{1}/releases'.format(org,repo)


response=requests.get(url, headers = customHeader)


print(response.status_code)
if response.status_code == 200 :
	existingLabels = []
	actualJson=response.json()

	#Metadata
	print("title is "+actualJson["title"])
	print("username "+actualJson["user"]["login"])
	print("total comments ",actualJson["comments"])
	print("total changed_files",actualJson["changed_files"])
	print("total commits",actualJson["commits"])
	print("mergeable",actualJson["mergeable"])


	#overview comment 
	nCF=actualJson["changed_files"] 
	nCM=actualJson["commits"] 
	commentData = { "body" : "Hi {0} , thanks for your PR .. your ratio is {1}  ".format(actualJson["user"]["login"],nCF/nCM)}

	print (json.dumps(commentData))
	commentResponse=requests.post(commentUrl,data=json.dumps(commentData), headers=customHeader)
	print("updated comments ?", commentResponse.status_code)


	#request review
	reviewData = { "reviewers" : ["vijaykiran225"]}
	print (json.dumps(reviewData))
	reviewResponse=requests.post(reviewRequestUrl,data=json.dumps(reviewData), headers=customPostHeader)
	print("updated reviewers ?", reviewResponse.status_code)


	#release post
	if actualJson["base"]["ref"] == "release":
		releaseData={"tag_name":"v1.0.0","target_commitish":"master","name":"v1.0.0","body":"Description of the release","draft":false,"prerelease":false}
		print (json.dumps(releaseData))
		releaseResponse=requests.post(releaseUrl,data=json.dumps(releaseData), headers=customPostHeader)
		print("updated releases ?", releaseResponse.status_code)

	#existing label
	for aLabel in actualJson["labels"]:
		existingLabels.append(aLabel["name"])

	print("existingLabels " , existingLabels)

	foundLabels = []

	#Release  label
	if actualJson["base"]["ref"] == "release":
		foundLabels.append("release")


	for aLine in actualJson["body"].split("\n"):
		if aLine.find('[x] Bug fix') != -1:
			if "bug" not in existingLabels:
				foundLabels.append("bug")
		elif aLine.find('[x] New feature') != -1:
			if "enhancement" not in existingLabels:
				foundLabels.append("enhancement")
		elif aLine.find('[x] Breaking change') != -1:
			if "breaking change" not in existingLabels:
				foundLabels.append("breaking change")
		elif aLine.find('[x] This change requires a documentation update') != -1:
			if "doc" not in existingLabels:
				foundLabels.append("doc")

	#updaate labels
	print("these needs to be added ", foundLabels)
	if len(foundLabels) >0 :
		data = { "labels" : foundLabels}
		print (json.dumps(data))
		labelResonse=requests.post(issueUrl,data=json.dumps(data), headers=customPostHeader)
		if labelResonse.status_code == 200:
			print("updated labels ?", labelResonse.status_code)
		else:
			print("unable to update label")
	else:
		print("no labels found")

else :
	print("failure")
