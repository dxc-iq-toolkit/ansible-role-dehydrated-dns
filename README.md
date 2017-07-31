marcusianlevine.dehydrated-dns
=========

Sign LetsEncrypt SSL certificates with the Dehydrated client via DNS-01 TXT challenge

Requirements
------------

By default this roles utilizes a Route53 boto hook script to create DNS TXT entries, so this role will install boto into the system Python.

As such, you must either provide a relative path to your (vault-encrypted) boto config file in your playbook via the variable `boto_config_file` —- or, if no value is provided for this variable, then the role will assume you provide environment variables `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` or otherwise configure credentials for boto.

By default this role installs configuration into `/etc`, which requires elevated privileges.

**Note: for now this role only supports signing certificates for domains whose DNS is managed by AWS Route53. Additional DNS providers would require a [custom hook script](https://github.com/lukas2511/dehydrated/wiki/Examples-for-DNS-01-hooks), along with some form of credentials for authenticating against the DNS provider's API.**

Role Variables
--------------

### Required

`hosted_zone_domain`: domain name associated with the AWS Route 53 hosted zone where your DNS entry will be created
`hosted_zone_id`: if you have both a public and private hosted zone associated with your domain name

### Optional

`subdomains`: optional list of FQDN subdomains to validate on the signed cert.
`letsencrypt_url`: URL of LetsEncrypt CA API endpoint. Defaults to [LetsEncrypt staging API](https://letsencrypt.org/docs/staging-environment/) since production is rate-limited (see comment in `defaults/main.yml` for production endpoint).
`boto_config_file`: if defined, provides a path to a [boto config file](http://boto.cloudhackers.com/en/latest/boto_config_tut.html) relative to your playbook which will be injected into the environment during role execution.
`boto_config_dest`: if `boto_config_file` is provided, you can optionally specify where the config file will be placed. Default: `/etc/boto.cfg`
`dehydrated_repo_dir`: directory into which the dehydrated GitHub repo will be cloned. Default: `~/dehydrated`
`dehydrated_dir`: directory where all supporting files for dehydrated (domain listing, dehydrated configuration) will be placed. Default: `/etc/dehydrated`
`cert_output_dir`: directory where signed certificates will be output. Defaults to the same directory as `dehydrated_dir`
`private_key_length`: length of the RSA private key generated when signing certificate. Default: 2048 (maximum length supported by Amazon Certificate Manager)

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - { role: username.rolename, x: 42 }

License
-------

BSD

Author Information
------------------

Written by Marcus Levine & Carolina Gonzalez for CKM Advisors.

Based on [this excellent article by Alagesan Palani](https://dzone.com/articles/automating-letsencrypt-certificate-generation-with).