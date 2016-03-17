import sys

import com.xebialabs.xlrelease.api.XLReleaseServiceHolder as XLReleaseServiceHolder



#get the releaseApi
releaseApi = XLReleaseServiceHolder.getReleaseApi()

# get the object of the current release
this_release = releaseApi.getRelease(release.id)


# extract the tags
tags = this_release.getTags()

# let's print and be merry
print "found these tags for release: %s" % release.id
print tags


#add the tag

tags.add(str(tag))

#print and be merry
print "adding tag: %s to release: %s" % (tag, release.id)

# update the release with the new set of tags
this_release.setTags(tags)

#save the updated release back to xlr
releaseApi.updateRelease(release.id, this_release)

# and we're good ..
# see it isn't hard .. just print a lot and be merry..
# or don't and be miserable .. see if i care..
