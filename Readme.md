# Resilio Companion

A companion service to be run alongside Resilio Sync.

I'm still exploring what I want this to be, but the general goal is to
iron out the painful and broken parts of Resilio and to attach on
crucially missing features.


## Tools

### Globally Synced Ignore List

Running the `ignore` command will run through all shares to look for a
`resilio-ignore.txt` file in the root folder. It will then copy that to the
local .sync/IgnoreList file, and can optionally delete all files that match the
IgnoreList (useful for cleaning up files on servers that should have been ignored).
