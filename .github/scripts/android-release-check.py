"""Verify the public Android catalog and prepare a report for the maintainer."""

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import HTTPRedirectHandler, Request, build_opener
from uuid import uuid4


PACKAGE = "ar.creativerevveal.tiertube.usuario"
REPO = "lionelvidal300-tech/tiertube-actualizaciones-usuarios"
CHANNEL = f"https://raw.githubusercontent.com/{REPO}/main/"
DOWNLOADS = "https://lionelvidal300-tech.github.io/tiertube-actualizaciones-usuarios/"
# Certificate of the existing public installation. Change after testing key migration.
SIGNER = "3b5293a805ab9c0ed4263a0ab2d357a39212c9aa131690fdce4afae4dd34926b"

VT_API = "https://www.virustotal.com/api/v3"
APPEAL = "https://support.google.com/googleplay/android-developer/contact/protectappeals"


class RejectRedirects(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def verify_apk(build_tools):
    catalog = json.loads(Path("user-android.json").read_text(encoding="utf-8"))
    version = catalog["versionName"]
    code = catalog["versionCode"]
    if not re.fullmatch(r"[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)+", version):
        raise ValueError("La versión del catálogo tiene un formato inesperado.")
    if catalog["package"] != PACKAGE or type(code) is not int or code <= 0:
        raise ValueError("El paquete o código de versión del catálogo es inválido.")

    apk = Path(f"TierTube-{version}-usuario.apk")
    if catalog["apk"] != CHANNEL + apk.name or not apk.is_file() or apk.is_symlink():
        raise ValueError("El catálogo no apunta al APK de usuario del canal oficial.")

    with apk.open("rb") as file:
        digest = hashlib.file_digest(file, "sha256").hexdigest()
    sums = Path("SHA256SUMS").read_text(encoding="utf-8").splitlines()
    if catalog["sha256"] != digest or f"{digest}  {apk.name}" not in sums:
        raise ValueError("El SHA-256 del APK difiere del catálogo o de SHA256SUMS.")

    certs = subprocess.check_output(
        [build_tools / "apksigner", "verify", "--print-certs", apk], text=True
    )
    signers = re.findall(r"(?im)^Signer #\d+ certificate SHA-256 digest: ([0-9a-f]+)$", certs)
    if [signer.lower() for signer in signers] != [SIGNER]:
        raise ValueError("El certificado del APK difiere del certificado de usuarios esperado.")

    badging = subprocess.check_output([build_tools / "aapt2", "dump", "badging", apk], text=True)
    expected = f"package: name='{PACKAGE}' versionCode='{code}' versionName='{version}'"
    if not badging.splitlines()[0].startswith(expected):
        raise ValueError("El paquete, la versión o el código del APK difiere del catálogo.")
    return apk, version, code, digest


def vt_request(path, api_key, data=None, content_type=None):
    headers = {"x-apikey": api_key, "Accept": "application/json"}
    if content_type:
        headers["Content-Type"] = content_type
    request = Request(VT_API + path, data=data, headers=headers)
    try:
        with build_opener(RejectRedirects()).open(request, timeout=25) as response:
            return json.load(response)["data"]
    except HTTPError as error:
        if error.code == 404 and data is None:
            return None
        raise ValueError(f"VirusTotal devolvió HTTP {error.code}.") from None


def vt_scan(apk, digest):
    api_key = os.environ.get("VT_API_KEY")
    if not api_key:
        return "Pendiente de configurar el secreto VT_API_KEY.", None

    report = vt_request(f"/files/{digest}", api_key)
    if report:
        return "Informe consultado por SHA-256.", report["attributes"]["last_analysis_stats"]

    if os.environ.get("VT_SUBMIT_PUBLIC_APK") != "true":
        return "VirusTotal aún no tiene un informe para este SHA-256.", None
    if apk.stat().st_size > 32_000_000:
        return "APK publicado mayor a 32 MB. Requiere análisis manual.", None

    boundary = "tiertube-" + uuid4().hex
    header = (
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; "
        f"filename=\"{apk.name}\"\r\nContent-Type: application/vnd.android.package-archive\r\n\r\n"
    ).encode("ascii")
    data = header + apk.read_bytes() + f"\r\n--{boundary}--\r\n".encode("ascii")
    submitted = vt_request("/files", api_key, data, f"multipart/form-data; boundary={boundary}")
    analysis = quote(submitted["id"], safe="")
    for _ in range(4):
        time.sleep(10)
        result = vt_request(f"/analyses/{analysis}", api_key)
        if result and result["attributes"]["status"] == "completed":
            return "VirusTotal completó el análisis del APK público.", result["attributes"]["stats"]
    return "APK público enviado. El análisis sigue pendiente en VirusTotal.", None


def main():
    build_tools, output = map(Path, sys.argv[1:])
    apk, version, code, digest = verify_apk(build_tools)
    output.mkdir(parents=True, exist_ok=True)
    report_url = f"https://www.virustotal.com/gui/file/{digest}/detection"
    (output / "datos-apelacion.txt").write_text(
        f"""Preparar solamente si Play Protect bloquea este APK.

Formulario de Google: {APPEAL}
Application package name: {PACKAGE}
SHA256 Hash of the apk of the uploaded file on Virus Total: {digest}

Additional information to support your appeal:

I’m requesting a review of a Google Play Protect block for TierTube {version}
(version code {code}), package {PACKAGE}.
This is the public Android edition distributed at {DOWNLOADS}
APK: {apk.name}
VirusTotal report: {report_url}

Device and Android version: [complete with the tested device]
Exact Play Protect message: [copy the message shown on the device]
Please review the APK identified by the SHA-256 in this form.
""",
        encoding="utf-8",
    )

    failed = False
    try:
        status, stats = vt_scan(apk, digest)
    except (OSError, ValueError, KeyError) as error:
        status = f"Error al consultar VirusTotal ({type(error).__name__})."
        if isinstance(error, ValueError) and str(error).startswith("VirusTotal devolvió HTTP"):
            status = str(error)
        stats = None
        failed = True

    if stats is not None:
        malicious = stats.get("malicious", 0)
        suspicious = stats.get("suspicious", 0)
        status += f" Motores con detección maliciosa: {malicious}. Sospechosa: {suspicious}."
        failed = failed or bool(malicious or suspicious)

    summary = f"""### TierTube Android {version}

- APK verificado: `{apk.name}`
- Paquete: `{PACKAGE}`
- Código de versión: `{code}`
- SHA-256 del archivo: `{digest}`
- SHA-256 del certificado: `{SIGNER}`
- VirusTotal: {status} [Informe por SHA-256]({report_url})
- Play Protect: prueba manual en Android. [Formulario de revisión]({APPEAL})

El archivo `datos-apelacion.txt` reúne los datos para solicitar una revisión si el teléfono muestra un bloqueo.
"""
    (output / "resultado.md").write_text(summary, encoding="utf-8")
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with Path(os.environ["GITHUB_STEP_SUMMARY"]).open("a", encoding="utf-8") as file:
            file.write(summary)
    print(summary)
    return int(failed)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        sys.exit(f"Falló la verificación del APK: {error}")
