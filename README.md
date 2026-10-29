# Build Together: Campus Hackathon Site

A small, dependency-free Python website for a campus hackathon. It serves an
event landing page, a student sign-in interface, and a registration-interest
form.

## Requirements

- Python 3.9 or newer
- A web browser

No third-party Python packages are required.

## Run locally

From the project directory, run:

```powershell
python hackathon_site.py
```

On Windows, this also works when the Python launcher is installed:

```powershell
py hackathon_site.py
```

Open http://127.0.0.1:8000 if it does not open automatically. Press `Ctrl+C`
in the terminal to stop the server.

## Features

- Responsive campus hackathon landing page and event information
- Student sign-in form with a show-password toggle
- Registration-interest form with server-side input validation
- Runs locally on `127.0.0.1`; no third-party dependencies

## Demo limitations

The student sign-in interface is only a front-end demonstration. It does not
authenticate accounts, create sessions, or connect to a school identity
provider. The password is not sent to the server or saved. Do not use real
credentials.

Registration submissions are validated by the local server but are not stored
or emailed. This project is not ready to host publicly as an authentication or
registration service.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).