"""Create the Play upload keystore for Benkyo Studio.

    python tools/make_release_key.py

The key is written OUTSIDE the git repository on purpose. Losing this file
means you can never update the app on Google Play again, so copy it somewhere
safe and keep the password file with it.

Nothing is printed except the public certificate fingerprint.
"""
import base64
import datetime
import secrets
import string
import sys
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID

OUT_DIR = Path(r"D:\Keys\akane")
KS_NAME = "akane-upload.keystore"
ALIAS = "akane"
CN = "AKANE Upload"
YEARS = 25


def random_password(length=28):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*-_"
    while True:
        pw = "".join(secrets.choice(alphabet) for _ in range(length))
        if (
            any(c.isupper() for c in pw)
            and any(c.islower() for c in pw)
            and any(c.isdigit() for c in pw)
            and any(c in "!@#$%^&*-_" for c in pw)
        ):
            return pw


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ks_path = OUT_DIR / KS_NAME
    if ks_path.exists():
        print("Refusing to overwrite an existing keystore:", ks_path)
        return 1

    password = random_password()
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, CN),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Hive Pulse Interactive"),
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        ]
    )
    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(days=1))
        .not_valid_after(now + datetime.timedelta(days=365 * YEARS))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .sign(key, hashes.SHA256())
    )

    blob = pkcs12.serialize_key_and_certificates(
        name=ALIAS.encode("utf-8"),
        key=key,
        cert=cert,
        cas=None,
        encryption_algorithm=serialization.BestAvailableEncryption(password.encode("utf-8")),
    )
    ks_path.write_bytes(blob)
    ks_path.chmod(0o600)

    secrets_txt = OUT_DIR / "KEY-CREDENTIALS-DO-NOT-COMMIT.txt"
    secrets_txt.write_text(
        "Benkyo Studio - Google Play upload key\n"
        "======================================\n"
        "\n"
        "Keystore file : %s\n"
        "Alias         : %s\n"
        "Key password  : %s\n"
        "Store password: %s\n"
        "Created       : %s\n"
        "Valid for     : %d years\n"
        "\n"
        "KEEP THIS FILE AND THE KEYSTORE TOGETHER, OFFLINE, IN TWO PLACES.\n"
        "If you lose them you cannot publish an update to this app again.\n"
        "\n"
        "Base64 of the keystore (this is what CI uses):\n%s\n"
        % (
            ks_path,
            ALIAS,
            password,
            password,
            now.isoformat(),
            YEARS,
            base64.b64encode(blob).decode("ascii"),
        ),
        encoding="utf-8",
    )
    secrets_txt.chmod(0o600)

    fingerprint = cert.fingerprint(hashes.SHA256()).hex().upper()
    print("keystore :", ks_path)
    print("alias    :", ALIAS)
    print("password :", password)
    print("sha256   :", ":".join(fingerprint[i:i + 2] for i in range(0, len(fingerprint), 2)))
    print("credentials file:", secrets_txt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
