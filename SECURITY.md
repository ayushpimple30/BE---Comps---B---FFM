# Security Policy

## Supported project

Security reports for the FFM Sentinel repository are welcome. As this is an engineering project under development, security fixes and response times are not guaranteed.

## Reporting a vulnerability

Please do not publish passwords, API keys, personal data, or a working exploit in a public issue.

Instead, contact the repository maintainers privately through GitHub's available contact options. Include:

- A concise description of the issue and its potential impact.
- The affected file, component, version, or commit.
- Reproduction steps and proof-of-concept details that do not expose real secrets or other people's data.
- Any suggested mitigation, if known.

If private contact is unavailable, create a minimal public issue that asks for a private reporting channel without including exploit details.

## Security practices

- Keep credentials and local environment files out of version control.
- Use placeholders in examples and rotate any secret that is accidentally exposed.
- Review dependencies, AI model sources, and their license/security notices.
- Treat camera, microphone, and other user-provided data with care.
- Do not assume that local inference alone makes the complete application secure or private.

Please allow maintainers reasonable time to assess a report before publicly disclosing details.
