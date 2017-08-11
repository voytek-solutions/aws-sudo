# What if I Want To Use `awssudo` With Instance Profile

If you want to use `awssudo` on a EC2 box with Instace Profile, simply make sure
that the `source_profile` is empty in the `~/.aws/credentials` file.

```
[my-profile]
role_arn = arn:aws:iam::123456123456:role/my_deployment_role
source_profile =
```

Now you can generate temporary access credentials and save them in
`~/.aws/credentials` for later use with:

```
$ awssudo -i my-profile
```

... or proxy your command via `awssudo` like this

```
$ awssudo my-profile aws iam list-users
```

**Remember** that Role attached to your EC2 instance profile needs to have right to
assume role.
