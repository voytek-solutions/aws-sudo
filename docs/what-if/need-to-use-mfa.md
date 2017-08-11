# What if I need to use MFA

Make sure that you profile has the `mfa_serial` present

```
[profile some-profile]
mfa_serial = arn:aws:iam::123456123456:mfa/user.name
role_arn = arn:aws:iam::654321654321:role/PowerUsers
source_profile = my-source
output = json
region = eu-west-1
```
