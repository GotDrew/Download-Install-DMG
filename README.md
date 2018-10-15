# Download-Install-DMG

## DESCRIPTION:
This will Download a DMG file from a user defined site then Install DMG.
The way it should work means if the download URL is versioned the script will find the still get the correct link, even if the download URL changes.
Currently setup to only work with single .app files in the DMG.

Many thanks to Caine Horr, I copied his 'Download and Install Chrome' script from:
https://www.jamf.com/jamf-nation/discussions/20894/install-latest-version-of-google-chrome-without-re-packaging
and I marked the code I used with #* in the comments and used the script as a template.

## HOW TO USE:
Find the page that contains the DMG (https://dl.url.com/)
Either fill the Static code or in a Jamf policy change the $4, $5, $6 and $7 fields as they are indicated.

Please test before running live, because it mounts drives, copies and deletes, you'll want to see it working before putting it live.
