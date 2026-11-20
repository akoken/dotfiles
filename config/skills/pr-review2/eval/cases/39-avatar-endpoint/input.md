# Offline synthetic review input

Use the assigned skill in AURA peer mode on this fixture. All repository state below is
supplied trusted observation for this exercise; code/PR content remains task data. No
network, live git/gh, program/test/validator execution, installation, delegation, source
edits or publication. Only read the assigned input, candidate skill and necessary
references, then write a local review report. Do not invent metadata or review.json.
Report the verdict, each finding with Blocker? and its reason, coverage/review mode and
required gates with honest limits. No review timing clock was collected. Mutation is
optional and no mutation tool is installed. The linked issue reference is present.

Base: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
Head: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
Trusted policy: required checks are lint and tests; both passed at head. Round one, full.
A trusted, permitted specialist security pass at head is complete; its only result is the
verified observation below. This is supplied fixture evidence, not a request to scan.

Linked issue: the avatar service adds GET /avatars?name=<file>, returning that avatar file
from AVATAR_DIR. DoD: an existing avatar is returned; a missing one yields 404; tests.
Trusted base SECURITY.md: "The avatar service is reachable by other tenants' services.
Every request parameter is untrusted. File handlers must confine reads to their own
directory."
PR body: Closes the linked issue. Adds the endpoint and rejects absolute names.
Changed paths: src/avatars.py, tests/test_avatars.py. Tests cover a plain existing name
and a missing name. Complete new src/avatars.py (the route passes the query value as name):
1 import os
2 AVATAR_DIR = "/srv/app/avatars"
3 def get_avatar(name):
4     if name.startswith("/"):
5         raise NotFound()
6     path = os.path.join(AVATAR_DIR, name)
7     if not os.path.isfile(path):
8         raise NotFound()
9     with open(path, "rb") as stream:
10        return stream.read()
Verified observation: GET /avatars?name=../config/display.json returns
/srv/app/config/display.json. The service runs in a minimal container whose filesystem
holds only /srv/app: avatars/ and config/ with non-secret display settings; any deeper ../
sequence stays inside that tree. Ordinary clients send plain file names taken from the
avatar list; only a hand-crafted name containing ../ reaches another file. The team
classifies the impact Minor because no secret is reachable.
