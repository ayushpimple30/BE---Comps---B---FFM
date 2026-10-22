# Testing and Validation

This document is a template for recording repeatable tests of FFM Sentinel. Fill in actual results from the current implementation; do not mark tests as passed without running them.

## Test environment

- Date:
- Git commit:
- Operating system:
- Python version:
- Hardware used:
- AI runtime and model versions:
- Network state (online/offline):

## Test cases

| ID | Area | Procedure | Expected result | Actual result | Status |
|---|---|---|---|---|---|
| T-01 | Application startup | Follow documented startup steps | Application starts without an unhandled error | Record after test | Not run |
| T-02 | Model availability | Verify configured model is installed and callable | Model is available or a clear error is shown | Record after test | Not run |
| T-03 | Text interaction | Submit a basic prompt, if implemented | Response is returned or a clear error is shown | Record after test | Not run |
| T-04 | Camera input | Test camera input, if implemented | Input is received and handled safely | Record after test | Not run |
| T-05 | Audio input/output | Test microphone and speaker, if implemented | Audio path works as designed | Record after test | Not run |
| T-06 | Offline behaviour | Disable network and test offline-claimed features | Offline-capable workflow works without remote dependencies | Record after test | Not run |
| T-07 | Error handling | Test missing model/device/configuration | Actionable error is reported | Record after test | Not run |
| T-08 | Shutdown/restart | Exit and restart application | Resources are released and startup is repeatable | Record after test | Not run |

## Reporting results

For each executed test, record exact steps, environment, outcome, and relevant logs. Remove secrets, access tokens, private conversations, and personal data from logs and screenshots.

Use Pass, Fail, or Blocked only after running the test. Keep unexecuted cases marked Not run.

## Evidence

Store genuine screenshots or prototype photographs under docs/screenshots/ when available. Include a caption with the date, test ID, and what the evidence demonstrates. Do not publish fabricated results or claim a feature is implemented merely because it appears in a diagram.
