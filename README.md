# Tennis Sheffield Booking Bot

Automates court booking interactions with `tennissheffield.com` using an authenticated browser session and can send email notifications using Gmail.

---

# Requirements

- Python `3.8.5`
- Active Tennis Sheffield account session
- Gmail account with App Password enabled

---

# Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

---

# Project Setup

## 1. Create `.env`

Create a `.env` file in the root directory of the project.

Example:

```env
DAILY_COOKIE=
DAILY_SESSION=

gmail_pass=
gmail_email=
gmail_name=
```

---

## 2. Configure Session Variables

These values are copied from an active logged-in browser session on `tennissheffield.com`.

### `DAILY_COOKIE`

Authentication cookie used to stay logged in.

### `DAILY_SESSION`

Session token/value required for authenticated requests.

> These values expire daily/device changes
> Every new time you open the website, re-copy the session code, no need for cookie unless device change

---

## 3. Configure Gmail

Used for sending automated emails.

### `gmail_email`

The Gmail address used to send emails.

Example:

```env
gmail_email=mybot@gmail.com
```

### `gmail_pass`

A Gmail App Password.

> Do NOT use your normal Gmail password.

Create an App Password here:

https://support.google.com/accounts/answer/185833

Requirements:
- 2FA enabled on the Google account
- App Password generated through Google Account settings

### `gmail_name`

Display name shown on outgoing emails.

Example:

```env
gmail_name=Tennis Sheffield Bot
```

---

## 4. Create `weekly_bookings.json`

Before running the tool, create a file named:

```text
weekly_bookings.json
```

Initial contents:

```json
{}
```

---

## 5. Initial Spreadsheet Setup

To initialise booking history/data:

1. Open the OneDrive spreadsheet
2. Navigate to:

```text
New Court Booking Form (Responses)
```

3. Copy all rows from columns:

```text
A-F
```

4. Paste/import the data into the location expected by the tool

---

# Running The Tool

Run the project with:

```bash
py tool.py
```

---

# Security Notes

- Never upload `.env` to GitHub
- Treat session cookies like passwords
- Anyone with the session values may be able to access the account
- Gmail credentials should remain private

---

# Common Issues

## Session Expired

If requests fail or authentication stops working:

1. Log into `tennissheffield.com`
2. Open browser developer tools
3. Copy updated session values
4. Replace:
   - `DAILY_COOKIE`
   - `DAILY_SESSION`

---

## Gmail Not Sending

Make sure:
- 2FA is enabled
- You are using a Google App Password
- Less secure app access is NOT being used

---

# Tested Environment

```text
Python 3.8.5
Windows
```