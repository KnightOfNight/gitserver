When you setup a new repository and you want it to automatically update to a
remote on bitbucket, you must perform the following steps...

1. copy hooks/post-update to <repo>/hooks/

2. add a git remote for bitbucket using a command like this...
    git remote add bitbucket ssh://git@bitbucket.org/<user>/<repo>.git

3. make sure your bitbucket account has an SSH key that allows your git server to push
