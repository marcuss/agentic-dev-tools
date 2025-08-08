# Git and GPG Setup Documentation

This document outlines the steps taken to configure Git with proper user information and GPG signing for verified commits in this repository.

## Git User Configuration

The repository has been configured with the following user information:

```bash
# Set username for this repository only
git config --local user.name "marcuss"

# Set email for this repository only
git config --local user.email "m4rkuz@gmail.com"
```

These settings are stored in the local repository configuration and do not affect other repositories.

## GPG Signing Setup

### 1. Generate a GPG Key

A GPG key was generated for the email address m4rkuz@gmail.com using the following configuration:

```
Key-Type: RSA
Key-Length: 4096
Subkey-Type: RSA
Subkey-Length: 4096
Name-Real: Marcus Sanchez
Name-Email: m4rkuz@gmail.com
Expire-Date: 0
```

The key was generated with:

```bash
gpg --batch --generate-key /path/to/gpg-key-gen.conf
```

### 2. Configure Git to Use the GPG Key

The repository was configured to use the generated GPG key for signing commits:

```bash
# Set the signing key for this repository
git config --local user.signingkey 9817F9210C2779E5

# Enable automatic signing of all commits
git config --local commit.gpgsign true
```

### 3. Export the Public Key for GitHub

The public key was exported in ASCII-armored format to add to GitHub:

```bash
gpg --armor --export 9817F9210C2779E5
```

This public key should be added to your GitHub account settings under "SSH and GPG keys" to enable commit verification.

## Verification

A test commit was made and verified with:

```bash
git log -1 --show-signature
```

The output confirmed that the commit was properly signed with the GPG key and attributed to the correct user.

## Maintenance

- To list your GPG keys: `gpg --list-secret-keys --keyid-format=long`
- To export a key: `gpg --armor --export KEY_ID`
- To disable signing for a single commit: `git commit --no-gpg-sign`
- To enable signing for a single commit when not enabled by default: `git commit -S`

## Troubleshooting

If you encounter issues with GPG signing:

1. Ensure the GPG key is available in your keyring: `gpg --list-secret-keys`
2. Check that the correct key is configured in Git: `git config --get user.signingkey`
3. Verify that signing is enabled: `git config --get commit.gpgsign`
4. For "secret key not available" errors, ensure the key ID matches exactly what's in your keyring

For more information, refer to the [GitHub documentation on signing commits](https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits).