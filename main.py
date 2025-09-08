import base64
import os
from pathlib import Path
from typing import Iterable
import argparse

from Crypto.Cipher import AES

from key import KEY


def pkcs7_unpad(padded: bytes) -> bytes:
    if not padded:
        return padded
    pad_len = padded[-1]
    # Basic validation
    if pad_len == 0 or pad_len > AES.block_size:
        return padded
    if padded.endswith(bytes([pad_len]) * pad_len):
        return padded[:-pad_len]
    return padded


def iter_text_files(directory: Path) -> Iterable[Path]:
    for entry in sorted(directory.iterdir()):
        if entry.is_file():
            yield entry


def decrypt_file_content(data: bytes) -> str:
    # Remove whitespace/newlines then base64-decode
    b64_compact = b"".join(data.split())
    encrypted = base64.b64decode(b64_compact)
    cipher = AES.new(KEY, AES.MODE_ECB)
    decrypted = cipher.decrypt(encrypted)
    plain = pkcs7_unpad(decrypted)
    return plain.decode("utf-8", errors="strict")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def pkcs7_pad(data: bytes) -> bytes:
    block = AES.block_size
    pad_len = block - (len(data) % block)
    if pad_len == 0:
        pad_len = block
    return data + bytes([pad_len]) * pad_len


def encrypt_text_to_base64(text: str) -> str:
    data = text.encode("utf-8")
    padded = pkcs7_pad(data)
    cipher = AES.new(KEY, AES.MODE_ECB)
    encrypted = cipher.encrypt(padded)
    return base64.b64encode(encrypted).decode("ascii")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["decrypt", "encrypt"], default="decrypt")
    args = parser.parse_args()

    project_root = Path(__file__).parent
    in_dir = project_root / "ZH"
    out_dir = project_root / "new_ZH_encrypted"

    if args.mode == "decrypt":
        ensure_dir(out_dir)
        for src in iter_text_files(in_dir):
            try:
                content = src.read_bytes()
                text = decrypt_file_content(content)
                dst = out_dir / src.name
                dst.write_text(text, encoding="utf-8")
                print(f"解密完成: {src.name} -> {dst}")
            except Exception as exc:
                print(f"解密失败: {src.name}: {exc}")
    else:
        ensure_dir(out_dir)
        for src in iter_text_files(in_dir):
            try:
                text = src.read_text(encoding="utf-8")
                b64 = encrypt_text_to_base64(text)
                dst = out_dir / src.name
                # 写为单行 Base64（不追加额外换行）
                dst.write_text(b64, encoding="utf-8")
                print(f"加密完成: {src.name} -> {dst}")
            except Exception as exc:
                print(f"加密失败: {src.name}: {exc}")


if __name__ == "__main__":
    main()
