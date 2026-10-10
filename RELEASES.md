# Toolchain releases

Keep packaging sources, rebuild scripts, documentation, and `SHA256SUMS` in Git. Use the existing
package manifests and source recipes for provenance; the release process does not add validation
claims.

For each release, start from a clean source checkout and create a versioned tag that points to the
intended commit. Prepare a draft GitHub Release for that tag and upload the archives with their
existing filenames plus the lowercase `SHA256SUMS` manifest. Download every uploaded asset back to a
temporary directory and compare its SHA-256 and size with the local copy; run
`shasum -a 256 -c SHA256SUMS` against the round-tripped files. Publish only after the source tag
resolves to the intended clean commit and every uploaded asset passes this check. Keep published
assets immutable; corrections require a new tag and release.

The `toolchains-20261009` URL used in the READMEs is the pinned asset path for this migration; the
links become usable after the draft release is published with that tag. SDKTools download URL
migration is a separate follow-up: removing the archives from Git history breaks consumers still
using raw-GitHub archive URLs. Update those consumers to the pinned release assets when the release
is published. Keep the existing Gitee mirror archives until
that mirror is migrated separately. The force-sync Gitee workflow is opt-in through the repository
variable `GITEE_GIT_MIRROR_ENABLED=true`; keep it unset or false during history replacement and
enable it only after Gitee binary distribution has migrated. Before history replacement, verify
that no mirror run is queued or active.
